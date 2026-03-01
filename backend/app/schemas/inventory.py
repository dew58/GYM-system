"""
Pydantic schemas for Inventory endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.inventory import InventoryCategory, TransactionType


class InventoryItemCreate(BaseModel):
    name: str = Field(..., max_length=200)
    category: InventoryCategory
    quantity: int = Field(default=0, ge=0)
    unit_price: float = Field(..., gt=0, description="Selling price in EGP")
    cost_price: Optional[float] = None
    low_stock_threshold: int = Field(default=5, ge=0)
    description: Optional[str] = None


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[InventoryCategory] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    cost_price: Optional[float] = None
    low_stock_threshold: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class InventoryItemResponse(BaseModel):
    id: UUID
    name: str
    category: InventoryCategory
    quantity: int
    unit_price: float
    cost_price: Optional[float]
    low_stock_threshold: int
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryTransactionCreate(BaseModel):
    item_id: UUID
    transaction_type: TransactionType
    quantity: int = Field(..., gt=0)
    unit_price: Optional[float] = None
    member_id: Optional[UUID] = None
    notes: Optional[str] = None


class InventoryTransactionResponse(BaseModel):
    id: UUID
    item_id: UUID
    transaction_type: TransactionType
    quantity: int
    unit_price: Optional[float]
    member_id: Optional[UUID]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
