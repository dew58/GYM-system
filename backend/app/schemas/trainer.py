"""
Pydantic schemas for Trainer endpoints.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TrainerCreate(BaseModel):
    name: str = Field(..., max_length=150)
    phone: Optional[str] = None
    specialization: Optional[str] = None
    commission_rate: float = Field(default=0, ge=0, le=100)
    salary: float = Field(default=0, ge=0)
    user_id: Optional[UUID] = None


class TrainerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    commission_rate: Optional[float] = None
    salary: Optional[float] = None
    is_active: Optional[bool] = None


class TrainerResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    name: str
    phone: Optional[str]
    specialization: Optional[str]
    commission_rate: float
    salary: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TrainerAssignmentCreate(BaseModel):
    trainer_id: UUID
    member_id: UUID


class TrainerAssignmentResponse(BaseModel):
    id: UUID
    trainer_id: UUID
    member_id: UUID
    assigned_date: date
    is_active: bool

    class Config:
        from_attributes = True


class TrainerSessionCreate(BaseModel):
    trainer_id: UUID
    member_id: UUID
    session_date: date
    duration_minutes: int = 60
    notes: Optional[str] = None


class TrainerSessionResponse(BaseModel):
    id: UUID
    trainer_id: UUID
    member_id: UUID
    session_date: date
    duration_minutes: int
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
