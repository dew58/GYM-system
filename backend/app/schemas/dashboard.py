"""
Pydantic schemas for Dashboard endpoints.
"""

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_members: int
    active_members: int
    active_subscriptions: int
    expiring_soon: int  # Subscriptions expiring within 7 days
    total_trainers: int
    today_attendance: int
    monthly_revenue: float
    yearly_revenue: float
    daily_revenue: float


class RevenueDataPoint(BaseModel):
    label: str  # e.g. "Jan 2026" or "2026-02-15"
    revenue: float
    expenses: float


class AttendanceDataPoint(BaseModel):
    label: str
    count: int
