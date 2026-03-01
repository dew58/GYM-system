"""
Payment model — cash payments, installments, receipts.
"""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Numeric, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    INSTALLMENT = "installment"


class PaymentStatus(str, enum.Enum):
    PAID = "paid"
    PARTIAL = "partial"
    PENDING = "pending"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id"), nullable=False, index=True
    )
    subscription_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("subscriptions.id"), nullable=True
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, comment="Amount in EGP")
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), default=PaymentMethod.CASH)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PAID)
    receipt_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=True, index=True)
    installment_number: Mapped[int] = mapped_column(Integer, nullable=True, comment="e.g. 1 of 3")
    total_installments: Mapped[int] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    member = relationship("Member", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")
