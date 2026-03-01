"""
Pydantic schemas for Subscription and SubscriptionPlan endpoints.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.subscription import SubscriptionStatus


# ── Plans ────────────────────────────────────────────────────
class PlanCreate(BaseModel):
    name: str = Field(..., max_length=100)
    name_ar: Optional[str] = None
    duration_days: int = Field(..., gt=0)
    price: float = Field(..., gt=0, description="Price in EGP")
    description: Optional[str] = None


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    name_ar: Optional[str] = None
    duration_days: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PlanResponse(BaseModel):
    id: UUID
    name: str
    name_ar: Optional[str]
    duration_days: int
    price: float
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Subscriptions ────────────────────────────────────────────
class SubscriptionCreate(BaseModel):
    member_id: UUID
    plan_id: UUID
    start_date: date
    promo_code: Optional[str] = None
    notes: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: UUID
    member_id: UUID
    plan_id: UUID
    start_date: date
    end_date: date
    status: SubscriptionStatus
    freeze_days_used: int
    max_freeze_days: int
    notes: Optional[str]
    created_at: datetime
    plan: Optional[PlanResponse] = None

    class Config:
        from_attributes = True


class FreezeRequest(BaseModel):
    freeze_days: int = Field(..., gt=0, le=30)


class RenewRequest(BaseModel):
    plan_id: UUID
    start_date: Optional[date] = None
    promo_code: Optional[str] = None


# ── Promo Codes ──────────────────────────────────────────────
class PromoCodeCreate(BaseModel):
    code: str = Field(..., max_length=30)
    discount_percent: float = Field(..., gt=0, le=100)
    valid_from: date
    valid_to: date
    max_uses: int = Field(default=100, gt=0)


class PromoCodeResponse(BaseModel):
    id: UUID
    code: str
    discount_percent: float
    valid_from: date
    valid_to: date
    max_uses: int
    used_count: int
    is_active: bool

    class Config:
        from_attributes = True
