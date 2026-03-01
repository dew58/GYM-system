"""
Trainer models — trainers, assignments, sessions.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Trainer(Base):
    __tablename__ = "trainers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, unique=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    specialization: Mapped[str] = mapped_column(String(200), nullable=True)
    commission_rate: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, comment="Commission % per member"
    )
    salary: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0, comment="Monthly salary in EGP"
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    assignments = relationship("TrainerAssignment", back_populates="trainer", lazy="selectin")
    sessions = relationship("TrainerSession", back_populates="trainer", lazy="selectin")


class TrainerAssignment(Base):
    """Links a trainer to a member."""
    __tablename__ = "trainer_assignments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    trainer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainers.id"), nullable=False, index=True
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id"), nullable=False, index=True
    )
    assigned_date: Mapped[date] = mapped_column(Date, default=lambda: date.today())
    is_active: Mapped[bool] = mapped_column(default=True)

    trainer = relationship("Trainer", back_populates="assignments")
    member = relationship("Member", back_populates="trainer_assignments")


class TrainerSession(Base):
    """Tracks individual training sessions delivered."""
    __tablename__ = "trainer_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    trainer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainers.id"), nullable=False, index=True
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id"), nullable=False
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    trainer = relationship("Trainer", back_populates="sessions")
