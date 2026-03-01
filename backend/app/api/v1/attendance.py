"""
Attendance router — check-in (manual, barcode, QR), attendance logs and reports.
"""

from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.member import Member
from app.models.attendance import Attendance, CheckInMethod
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas.attendance import CheckInRequest, AttendanceResponse, AttendanceListResponse

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/check-in", response_model=AttendanceResponse, status_code=201)
async def check_in(
    data: CheckInRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check in a member. Supports:
    - Manual: provide member_id
    - Barcode/QR: provide barcode string
    """
    member = None

    if data.barcode:
        result = await db.execute(select(Member).where(Member.barcode == data.barcode))
        member = result.scalar_one_or_none()
    elif data.member_id:
        result = await db.execute(select(Member).where(Member.id == data.member_id))
        member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not member.is_active:
        raise HTTPException(status_code=400, detail="Member account is inactive")

    # Check for active subscription
    sub_result = await db.execute(
        select(Subscription).where(
            Subscription.member_id == member.id,
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.start_date <= date.today(),
            Subscription.end_date >= date.today(),
        )
    )
    active_sub = sub_result.scalar_one_or_none()
    if not active_sub:
        raise HTTPException(
            status_code=400,
            detail="No active subscription. Please renew membership.",
        )

    # Prevent duplicate check-in within 1 hour
    recent_result = await db.execute(
        select(Attendance).where(
            Attendance.member_id == member.id,
            Attendance.check_in >= datetime.now(timezone.utc).replace(
                hour=datetime.now(timezone.utc).hour - 1
            ),
        )
    )
    if recent_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already checked in recently")

    attendance = Attendance(
        member_id=member.id,
        method=data.method,
        checked_in_by=current_user.id,
    )
    db.add(attendance)
    await db.flush()
    await db.refresh(attendance)
    return attendance


@router.get("", response_model=AttendanceListResponse)
async def list_attendance(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    member_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List attendance records with filters."""
    query = select(Attendance).order_by(Attendance.check_in.desc())

    if member_id:
        query = query.where(Attendance.member_id == member_id)
    if date_from:
        query = query.where(func.date(Attendance.check_in) >= date_from)
    if date_to:
        query = query.where(func.date(Attendance.check_in) <= date_to)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    return AttendanceListResponse(items=records, total=total, page=page, page_size=page_size)


@router.get("/today-count")
async def today_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's attendance count."""
    count = (await db.execute(
        select(func.count()).where(func.date(Attendance.check_in) == date.today())
    )).scalar()

    unique = (await db.execute(
        select(func.count(func.distinct(Attendance.member_id))).where(
            func.date(Attendance.check_in) == date.today()
        )
    )).scalar()

    return {"date": str(date.today()), "total_check_ins": count, "unique_members": unique}
