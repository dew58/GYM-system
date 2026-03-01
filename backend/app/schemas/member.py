"""
Pydantic schemas for Member endpoints.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.member import Gender


class MemberCreate(BaseModel):
    name_ar: str = Field(..., max_length=150, description="Arabic name")
    name_en: Optional[str] = Field(None, max_length=150, description="English name")
    national_id: Optional[str] = Field(None, max_length=14, description="Egyptian National ID")
    phone: str = Field(..., max_length=20)
    emergency_contact: Optional[str] = None
    email: Optional[str] = None
    gender: Gender
    date_of_birth: Optional[date] = None
    medical_notes: Optional[str] = None
    address: Optional[str] = None


class MemberUpdate(BaseModel):
    name_ar: Optional[str] = None
    name_en: Optional[str] = None
    national_id: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    medical_notes: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class MemberResponse(BaseModel):
    id: UUID
    name_ar: str
    name_en: Optional[str]
    national_id: Optional[str]
    phone: str
    emergency_contact: Optional[str]
    email: Optional[str]
    gender: Gender
    date_of_birth: Optional[date]
    medical_notes: Optional[str]
    profile_image: Optional[str]
    address: Optional[str]
    barcode: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MemberListResponse(BaseModel):
    items: list[MemberResponse]
    total: int
    page: int
    page_size: int
