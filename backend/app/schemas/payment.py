"""
Pydantic schemas for Payment endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    member_id: UUID
    subscription_id: Optional[UUID] = None
    amount: float = Field(..., gt=0, description="Amount in EGP")
    discount_amount: float = Field(default=0, ge=0)
    method: PaymentMethod = PaymentMethod.CASH
    status: PaymentStatus = PaymentStatus.PAID
    installment_number: Optional[int] = None
    total_installments: Optional[int] = None
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: UUID
    member_id: UUID
    subscription_id: Optional[UUID]
    amount: float
    discount_amount: float
    method: PaymentMethod
    status: PaymentStatus
    receipt_number: Optional[str]
    installment_number: Optional[int]
    total_installments: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    page: int
    page_size: int


class DailyClosingReport(BaseModel):
    date: str
    total_revenue: float
    cash_revenue: float
    card_revenue: float
    total_payments: int
    new_subscriptions: int
