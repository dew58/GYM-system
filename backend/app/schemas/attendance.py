"""
Pydantic schemas for Attendance endpoints.
"""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.attendance import CheckInMethod


class CheckInRequest(BaseModel):
    member_id: Optional[UUID] = None
    barcode: Optional[str] = None
    method: CheckInMethod = CheckInMethod.MANUAL


class AttendanceResponse(BaseModel):
    id: UUID
    member_id: UUID
    check_in: datetime
    method: CheckInMethod

    class Config:
        from_attributes = True


class AttendanceListResponse(BaseModel):
    items: list[AttendanceResponse]
    total: int
    page: int
    page_size: int


class AttendanceReport(BaseModel):
    date: str
    total_check_ins: int
    unique_members: int
