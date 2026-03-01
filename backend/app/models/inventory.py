"""
Inventory models — supplements, equipment, and sales tracking.
"""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Numeric, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InventoryCategory(str, enum.Enum):
    SUPPLEMENT = "supplement"
    EQUIPMENT = "equipment"
    ACCESSORY = "accessory"
    APPAREL = "apparel"
    OTHER = "other"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[InventoryCategory] = mapped_column(Enum(InventoryCategory), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, comment="Price in EGP")
    cost_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=5)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    transactions = relationship("InventoryTransaction", back_populates="item", lazy="selectin")


class TransactionType(str, enum.Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("inventory_items.id"), nullable=False, index=True
    )
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("members.id"), nullable=True
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    item = relationship("InventoryItem", back_populates="transactions")
