"""
Pydantic schemas for Expense endpoints.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.expense import ExpenseCategory


class ExpenseCreate(BaseModel):
    category: ExpenseCategory
    amount: float = Field(..., gt=0, description="Amount in EGP")
    expense_date: date
    description: Optional[str] = None
    vendor: Optional[str] = None


class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    amount: Optional[float] = None
    expense_date: Optional[date] = None
    description: Optional[str] = None
    vendor: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: UUID
    category: ExpenseCategory
    amount: float
    expense_date: date
    description: Optional[str]
    vendor: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int


class MonthlySummary(BaseModel):
    month: str
    total_revenue: float
    total_expenses: float
    net_profit: float
    expense_breakdown: dict[str, float]
