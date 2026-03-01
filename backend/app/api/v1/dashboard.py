"""
Dashboard router — aggregate stats for the admin dashboard.
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.models.member import Member
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.trainer import Trainer
from app.models.attendance import Attendance
from app.models.payment import Payment, PaymentStatus
from app.schemas.dashboard import DashboardSummary, RevenueDataPoint, AttendanceDataPoint

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
DASH_ROLES = [UserRole.SUPER_ADMIN, UserRole.MANAGER, UserRole.ACCOUNTANT]


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(DASH_ROLES))):
    today = date.today()
    total_members = (await db.execute(select(func.count()).select_from(Member))).scalar()
    active_members = (await db.execute(select(func.count()).where(Member.is_active == True))).scalar()
    active_subs = (await db.execute(select(func.count()).where(
        Subscription.status == SubscriptionStatus.ACTIVE))).scalar()
    expiring = (await db.execute(select(func.count()).where(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Subscription.end_date <= today + timedelta(days=7),
        Subscription.end_date >= today))).scalar()
    trainers = (await db.execute(select(func.count()).select_from(Trainer).where(Trainer.is_active == True))).scalar()
    today_att = (await db.execute(select(func.count()).where(
        func.date(Attendance.check_in) == today))).scalar()
    paid_filter = Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL])
    daily_rev = float((await db.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(
        func.date(Payment.created_at) == today, paid_filter))).scalar())
    monthly_rev = float((await db.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(
        func.extract("month", Payment.created_at) == today.month,
        func.extract("year", Payment.created_at) == today.year, paid_filter))).scalar())
    yearly_rev = float((await db.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(
        func.extract("year", Payment.created_at) == today.year, paid_filter))).scalar())
    return DashboardSummary(total_members=total_members, active_members=active_members,
        active_subscriptions=active_subs, expiring_soon=expiring, total_trainers=trainers,
        today_attendance=today_att, daily_revenue=daily_rev, monthly_revenue=monthly_rev, yearly_revenue=yearly_rev)


@router.get("/revenue-chart", response_model=list[RevenueDataPoint])
async def revenue_chart(months: int = 6, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(DASH_ROLES))):
    from app.models.expense import Expense
    data = []
    today = date.today()
    for i in range(months - 1, -1, -1):
        m = today.month - i; y = today.year
        while m <= 0: m += 12; y -= 1
        rev = float((await db.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(
            func.extract("month", Payment.created_at) == m, func.extract("year", Payment.created_at) == y,
            Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL])))).scalar())
        exp = float((await db.execute(select(func.coalesce(func.sum(Expense.amount), 0)).where(
            func.extract("month", Expense.expense_date) == m,
            func.extract("year", Expense.expense_date) == y))).scalar())
        data.append(RevenueDataPoint(label=f"{y}-{m:02d}", revenue=rev, expenses=exp))
    return data


@router.get("/attendance-chart", response_model=list[AttendanceDataPoint])
async def attendance_chart(days: int = 14, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(DASH_ROLES))):
    data = []
    today = date.today()
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        count = (await db.execute(select(func.count()).where(
            func.date(Attendance.check_in) == d))).scalar()
        data.append(AttendanceDataPoint(label=str(d), count=count))
    return data
