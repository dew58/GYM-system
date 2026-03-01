"""
Expense model — gym operational expenses categorized.
"""

import uuid
import enum
from datetime import date, datetime, timezone

from sqlalchemy import String, Numeric, Date, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExpenseCategory(str, enum.Enum):
    RENT = "rent"
    ELECTRICITY = "electricity"
    WATER = "water"
    SALARIES = "salaries"
    MAINTENANCE = "maintenance"
    EQUIPMENT = "equipment"
    SUPPLEMENTS = "supplements"
    MARKETING = "marketing"
    CLEANING = "cleaning"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    category: Mapped[ExpenseCategory] = mapped_column(Enum(ExpenseCategory), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, comment="Amount in EGP")
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    vendor: Mapped[str] = mapped_column(String(200), nullable=True)
    receipt_image: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
