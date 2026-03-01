"""
Trainer router — CRUD, assignments, sessions, commission calculation.
"""

from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.trainer import Trainer, TrainerAssignment, TrainerSession
from app.schemas.trainer import (
    TrainerCreate, TrainerUpdate, TrainerResponse,
    TrainerAssignmentCreate, TrainerAssignmentResponse,
    TrainerSessionCreate, TrainerSessionResponse,
)

router = APIRouter(prefix="/trainers", tags=["Trainers"])

ADMIN_ROLES = [UserRole.SUPER_ADMIN, UserRole.MANAGER]


@router.get("", response_model=list[TrainerResponse])
async def list_trainers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all trainers."""
    result = await db.execute(select(Trainer).order_by(Trainer.name))
    return result.scalars().all()


@router.post("", response_model=TrainerResponse, status_code=201)
async def create_trainer(
    data: TrainerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Add a new trainer."""
    trainer = Trainer(**data.model_dump())
    db.add(trainer)
    await db.flush()
    await db.refresh(trainer)
    return trainer


@router.get("/{trainer_id}", response_model=TrainerResponse)
async def get_trainer(
    trainer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get trainer details."""
    result = await db.execute(select(Trainer).where(Trainer.id == trainer_id))
    trainer = result.scalar_one_or_none()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return trainer


@router.put("/{trainer_id}", response_model=TrainerResponse)
async def update_trainer(
    trainer_id: str,
    data: TrainerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Update a trainer."""
    result = await db.execute(select(Trainer).where(Trainer.id == trainer_id))
    trainer = result.scalar_one_or_none()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(trainer, field, value)

    await db.flush()
    await db.refresh(trainer)
    return trainer


# ── Assignments ──────────────────────────────────────────────
@router.get("/{trainer_id}/assignments", response_model=list[TrainerAssignmentResponse])
async def list_assignments(
    trainer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all members assigned to a trainer."""
    result = await db.execute(
        select(TrainerAssignment).where(
            TrainerAssignment.trainer_id == trainer_id,
            TrainerAssignment.is_active == True,
        )
    )
    return result.scalars().all()


@router.post("/assignments", response_model=TrainerAssignmentResponse, status_code=201)
async def assign_member(
    data: TrainerAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Assign a member to a trainer."""
    assignment = TrainerAssignment(**data.model_dump())
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return assignment


# ── Sessions ─────────────────────────────────────────────────
@router.get("/{trainer_id}/sessions", response_model=list[TrainerSessionResponse])
async def list_sessions(
    trainer_id: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List training sessions for a trainer."""
    query = select(TrainerSession).where(TrainerSession.trainer_id == trainer_id)
    if date_from:
        query = query.where(TrainerSession.session_date >= date_from)
    if date_to:
        query = query.where(TrainerSession.session_date <= date_to)
    query = query.order_by(TrainerSession.session_date.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/sessions", response_model=TrainerSessionResponse, status_code=201)
async def record_session(
    data: TrainerSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES + [UserRole.TRAINER])),
):
    """Record a training session."""
    session = TrainerSession(**data.model_dump())
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


@router.get("/{trainer_id}/commission")
async def calculate_commission(
    trainer_id: str,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES + [UserRole.ACCOUNTANT])),
):
    """Calculate trainer commission for a given month."""
    result = await db.execute(select(Trainer).where(Trainer.id == trainer_id))
    trainer = result.scalar_one_or_none()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    # Count sessions in the month
    session_count = (await db.execute(
        select(func.count()).where(
            TrainerSession.trainer_id == trainer_id,
            func.extract("month", TrainerSession.session_date) == month,
            func.extract("year", TrainerSession.session_date) == year,
        )
    )).scalar()

    # Count active assignments
    member_count = (await db.execute(
        select(func.count()).where(
            TrainerAssignment.trainer_id == trainer_id,
            TrainerAssignment.is_active == True,
        )
    )).scalar()

    commission = float(trainer.salary) + (member_count * float(trainer.commission_rate))

    return {
        "trainer_id": str(trainer_id),
        "trainer_name": trainer.name,
        "month": month,
        "year": year,
        "base_salary": float(trainer.salary),
        "commission_rate": float(trainer.commission_rate),
        "active_members": member_count,
        "sessions_delivered": session_count,
        "total_commission": commission,
        "total_pay": float(trainer.salary) + commission,
    }
