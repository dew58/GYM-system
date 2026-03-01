"""
Expenses router — CRUD + monthly summary with net profit.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.models.expense import Expense, ExpenseCategory
from app.models.payment import Payment, PaymentStatus
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseListResponse, MonthlySummary

router = APIRouter(prefix="/expenses", tags=["Expenses"])
EXPENSE_ROLES = [UserRole.SUPER_ADMIN, UserRole.ACCOUNTANT]


@router.get("", response_model=ExpenseListResponse)
async def list_expenses(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    category: Optional[ExpenseCategory] = None,
    date_from: Optional[date] = None, date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(EXPENSE_ROLES + [UserRole.MANAGER])),
):
    query = select(Expense).order_by(Expense.expense_date.desc())
    if category: query = query.where(Expense.category == category)
    if date_from: query = query.where(Expense.expense_date >= date_from)
    if date_to: query = query.where(Expense.expense_date <= date_to)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return ExpenseListResponse(items=result.scalars().all(), total=total, page=page, page_size=page_size)


@router.post("", response_model=ExpenseResponse, status_code=201)
async def create_expense(data: ExpenseCreate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(EXPENSE_ROLES))):
    expense = Expense(**data.model_dump())
    db.add(expense); await db.flush(); await db.refresh(expense)
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(expense_id: str, data: ExpenseUpdate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(EXPENSE_ROLES))):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense: raise HTTPException(status_code=404, detail="Expense not found")
    for field, value in data.model_dump(exclude_unset=True).items(): setattr(expense, field, value)
    await db.flush(); await db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=204)
async def delete_expense(expense_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(EXPENSE_ROLES))):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense: raise HTTPException(status_code=404, detail="Expense not found")
    await db.delete(expense); await db.flush()


@router.get("/monthly-summary", response_model=MonthlySummary)
async def monthly_summary(month: int = Query(..., ge=1, le=12), year: int = Query(..., ge=2020),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(EXPENSE_ROLES + [UserRole.MANAGER]))):
    rev = float((await db.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(
        func.extract("month", Payment.created_at) == month, func.extract("year", Payment.created_at) == year,
        Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL])))).scalar())
    exp = float((await db.execute(select(func.coalesce(func.sum(Expense.amount), 0)).where(
        func.extract("month", Expense.expense_date) == month, func.extract("year", Expense.expense_date) == year))).scalar())
    bd = await db.execute(select(Expense.category, func.sum(Expense.amount)).where(
        func.extract("month", Expense.expense_date) == month, func.extract("year", Expense.expense_date) == year
    ).group_by(Expense.category))
    return MonthlySummary(month=f"{year}-{month:02d}", total_revenue=rev, total_expenses=exp,
        net_profit=rev - exp, expense_breakdown={r[0].value: float(r[1]) for r in bd.all()})
