"""
Subscription router — plans, subscriptions, freeze, renew, promo codes.
"""

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.subscription import SubscriptionPlan, Subscription, SubscriptionStatus, PromoCode
from app.schemas.subscription import (
    PlanCreate, PlanUpdate, PlanResponse,
    SubscriptionCreate, SubscriptionResponse,
    FreezeRequest, RenewRequest,
    PromoCodeCreate, PromoCodeResponse,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

ADMIN_ROLES = [UserRole.SUPER_ADMIN, UserRole.MANAGER]


# ── Plans ────────────────────────────────────────────────────
@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all subscription plans."""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.is_active == True).order_by(SubscriptionPlan.duration_days)
    )
    return result.scalars().all()


@router.post("/plans", response_model=PlanResponse, status_code=201)
async def create_plan(
    data: PlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
):
    """Create a new subscription plan."""
    plan = SubscriptionPlan(**data.model_dump())
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return plan


@router.put("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: str,
    data: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
):
    """Update a subscription plan."""
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)

    await db.flush()
    await db.refresh(plan)
    return plan


# ── Subscriptions ────────────────────────────────────────────
@router.get("", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    member_id: Optional[str] = None,
    status: Optional[SubscriptionStatus] = None,
    expiring_within_days: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List subscriptions with optional filters."""
    query = select(Subscription).order_by(Subscription.created_at.desc())

    if member_id:
        query = query.where(Subscription.member_id == member_id)
    if status:
        query = query.where(Subscription.status == status)
    if expiring_within_days:
        cutoff = date.today() + timedelta(days=expiring_within_days)
        query = query.where(
            Subscription.end_date <= cutoff,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(
    data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES + [UserRole.RECEPTIONIST])),
):
    """Create a new subscription for a member."""
    # Fetch plan
    plan_result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == data.plan_id))
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    end_date = data.start_date + timedelta(days=plan.duration_days)

    # Apply promo code discount if provided
    if data.promo_code:
        promo_result = await db.execute(
            select(PromoCode).where(
                PromoCode.code == data.promo_code,
                PromoCode.is_active == True,
                PromoCode.valid_from <= date.today(),
                PromoCode.valid_to >= date.today(),
            )
        )
        promo = promo_result.scalar_one_or_none()
        if promo and promo.used_count < promo.max_uses:
            promo.used_count += 1

    subscription = Subscription(
        member_id=data.member_id,
        plan_id=data.plan_id,
        start_date=data.start_date,
        end_date=end_date,
        notes=data.notes,
    )
    db.add(subscription)
    await db.flush()
    await db.refresh(subscription)
    return subscription


@router.post("/{sub_id}/freeze", response_model=SubscriptionResponse)
async def freeze_subscription(
    sub_id: str,
    data: FreezeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Freeze a subscription, extending its end date."""
    result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub.status != SubscriptionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Can only freeze active subscriptions")

    remaining_freeze = sub.max_freeze_days - sub.freeze_days_used
    if data.freeze_days > remaining_freeze:
        raise HTTPException(status_code=400, detail=f"Only {remaining_freeze} freeze days remaining")

    sub.status = SubscriptionStatus.FROZEN
    sub.freeze_start = date.today()
    sub.freeze_days_used += data.freeze_days
    sub.end_date = sub.end_date + timedelta(days=data.freeze_days)

    await db.flush()
    await db.refresh(sub)
    return sub


@router.post("/{sub_id}/unfreeze", response_model=SubscriptionResponse)
async def unfreeze_subscription(
    sub_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Unfreeze a subscription."""
    result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub.status != SubscriptionStatus.FROZEN:
        raise HTTPException(status_code=400, detail="Subscription is not frozen")

    sub.status = SubscriptionStatus.ACTIVE
    sub.freeze_start = None
    await db.flush()
    await db.refresh(sub)
    return sub


@router.post("/{sub_id}/renew", response_model=SubscriptionResponse)
async def renew_subscription(
    sub_id: str,
    data: RenewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES + [UserRole.RECEPTIONIST])),
):
    """Renew a subscription with a new plan."""
    result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
    old_sub = result.scalar_one_or_none()
    if not old_sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    plan_result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == data.plan_id))
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    start = data.start_date or max(old_sub.end_date, date.today())
    end = start + timedelta(days=plan.duration_days)

    # Expire old subscription
    old_sub.status = SubscriptionStatus.EXPIRED

    new_sub = Subscription(
        member_id=old_sub.member_id,
        plan_id=data.plan_id,
        start_date=start,
        end_date=end,
    )
    db.add(new_sub)
    await db.flush()
    await db.refresh(new_sub)
    return new_sub


# ── Promo Codes ──────────────────────────────────────────────
@router.get("/promo-codes", response_model=list[PromoCodeResponse])
async def list_promo_codes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """List all promo codes."""
    result = await db.execute(select(PromoCode).order_by(PromoCode.created_at.desc()))
    return result.scalars().all()


@router.post("/promo-codes", response_model=PromoCodeResponse, status_code=201)
async def create_promo_code(
    data: PromoCodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
):
    """Create a new promo code."""
    promo = PromoCode(**data.model_dump())
    db.add(promo)
    await db.flush()
    await db.refresh(promo)
    return promo
