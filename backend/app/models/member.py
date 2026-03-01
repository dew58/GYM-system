"""
Member model — gym members with Egypt-specific fields.
"""

import uuid
import enum
from datetime import date, datetime, timezone

from sqlalchemy import String, Text, Enum, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Arabic and English names for Egyptian market
    name_ar: Mapped[str] = mapped_column(String(150), nullable=False, comment="Arabic name")
    name_en: Mapped[str] = mapped_column(String(150), nullable=True, comment="English name")
    # Egyptian National ID (14 digits)
    national_id: Mapped[str] = mapped_column(
        String(14), unique=True, nullable=True, index=True, comment="Egyptian National ID"
    )
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    emergency_contact: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    medical_notes: Mapped[str] = mapped_column(Text, nullable=True)
    profile_image: Mapped[str] = mapped_column(String(500), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    barcode: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=True, index=True, comment="Barcode / QR for check-in"
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    subscriptions = relationship("Subscription", back_populates="member", lazy="selectin")
    attendances = relationship("Attendance", back_populates="member", lazy="selectin")
    payments = relationship("Payment", back_populates="member", lazy="selectin")
    trainer_assignments = relationship("TrainerAssignment", back_populates="member", lazy="selectin")
