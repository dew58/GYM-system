"""
Payments router — record payments, installments, receipts, daily reports.
"""

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentListResponse, DailyClosingReport

router = APIRouter(prefix="/payments", tags=["Payments"])

PAYMENT_ROLES = [UserRole.SUPER_ADMIN, UserRole.MANAGER, UserRole.RECEPTIONIST, UserRole.ACCOUNTANT]


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    member_id: Optional[str] = None,
    method: Optional[PaymentMethod] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List payments with filters and pagination."""
    query = select(Payment).order_by(Payment.created_at.desc())

    if member_id:
        query = query.where(Payment.member_id == member_id)
    if method:
        query = query.where(Payment.method == method)
    if date_from:
        query = query.where(func.date(Payment.created_at) >= date_from)
    if date_to:
        query = query.where(func.date(Payment.created_at) <= date_to)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    payments = result.scalars().all()

    return PaymentListResponse(items=payments, total=total, page=page, page_size=page_size)


@router.post("", response_model=PaymentResponse, status_code=201)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(PAYMENT_ROLES)),
):
    """Record a new payment."""
    receipt_number = f"REC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    payment = Payment(
        **data.model_dump(),
        receipt_number=receipt_number,
        created_by=current_user.id,
    )
    db.add(payment)
    await db.flush()
    await db.refresh(payment)
    return payment


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get payment details."""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/{payment_id}/receipt")
async def generate_receipt(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a PDF receipt for a payment."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A5
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as pdf_canvas

    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A5)
    width, height = A5

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 30 * mm, "GYM RECEIPT")

    c.setFont("Helvetica", 10)
    c.drawString(15 * mm, height - 45 * mm, f"Receipt #: {payment.receipt_number}")
    c.drawString(15 * mm, height - 52 * mm, f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M')}")
    c.drawString(15 * mm, height - 59 * mm, f"Amount: {payment.amount:.2f} EGP")
    c.drawString(15 * mm, height - 66 * mm, f"Method: {payment.method.value.upper()}")
    c.drawString(15 * mm, height - 73 * mm, f"Status: {payment.status.value.upper()}")

    if payment.discount_amount > 0:
        c.drawString(15 * mm, height - 80 * mm, f"Discount: {payment.discount_amount:.2f} EGP")

    if payment.installment_number:
        c.drawString(
            15 * mm, height - 87 * mm,
            f"Installment: {payment.installment_number} of {payment.total_installments}"
        )

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, 15 * mm, "Thank you for choosing our gym!")

    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=receipt_{payment.receipt_number}.pdf"},
    )


@router.get("/reports/daily-closing", response_model=DailyClosingReport)
async def daily_closing_report(
    report_date: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.MANAGER, UserRole.ACCOUNTANT])),
):
    """Get daily closing report with revenue breakdown."""
    target_date = report_date or date.today()

    # Total revenue
    total_result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            func.date(Payment.created_at) == target_date,
            Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL]),
        )
    )
    total_revenue = float(total_result.scalar())

    # Cash revenue
    cash_result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            func.date(Payment.created_at) == target_date,
            Payment.method == PaymentMethod.CASH,
            Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL]),
        )
    )
    cash_revenue = float(cash_result.scalar())

    # Payment count
    count_result = await db.execute(
        select(func.count()).where(func.date(Payment.created_at) == target_date)
    )
    total_payments = count_result.scalar()

    return DailyClosingReport(
        date=str(target_date),
        total_revenue=total_revenue,
        cash_revenue=cash_revenue,
        card_revenue=total_revenue - cash_revenue,
        total_payments=total_payments,
        new_subscriptions=0,
    )
