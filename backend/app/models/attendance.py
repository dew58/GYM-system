"""
Attendance model — check-in logs with barcode/QR/manual methods.
"""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CheckInMethod(str, enum.Enum):
    MANUAL = "manual"
    BARCODE = "barcode"
    QR_CODE = "qr_code"


class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id"), nullable=False, index=True
    )
    check_in: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    method: Mapped[CheckInMethod] = mapped_column(
        Enum(CheckInMethod), default=CheckInMethod.MANUAL
    )
    checked_in_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    member = relationship("Member", back_populates="attendances")
