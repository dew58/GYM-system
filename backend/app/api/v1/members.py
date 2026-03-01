"""
Member router — CRUD, profile image upload, barcode generation.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.member import Member
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse, MemberListResponse

router = APIRouter(prefix="/members", tags=["Members"])

# Roles allowed to manage members
MEMBER_MANAGERS = [UserRole.SUPER_ADMIN, UserRole.MANAGER, UserRole.RECEPTIONIST]


@router.get("", response_model=MemberListResponse)
async def list_members(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List members with pagination and search (Arabic/English name, phone, national ID)."""
    query = select(Member).order_by(Member.created_at.desc())

    if search:
        search_filter = or_(
            Member.name_ar.ilike(f"%{search}%"),
            Member.name_en.ilike(f"%{search}%"),
            Member.phone.ilike(f"%{search}%"),
            Member.national_id.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    if is_active is not None:
        query = query.where(Member.is_active == is_active)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    members = result.scalars().all()

    return MemberListResponse(items=members, total=total, page=page, page_size=page_size)


@router.post("", response_model=MemberResponse, status_code=201)
async def create_member(
    data: MemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(MEMBER_MANAGERS)),
):
    """Create a new gym member with a unique barcode."""
    # Check duplicate national ID
    if data.national_id:
        existing = await db.execute(
            select(Member).where(Member.national_id == data.national_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="National ID already registered")

    member = Member(**data.model_dump())
    # Generate unique barcode
    member.barcode = f"GYM-{uuid.uuid4().hex[:8].upper()}"

    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get member details by ID."""
    result = await db.execute(select(Member).where(Member.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: str,
    data: MemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(MEMBER_MANAGERS)),
):
    """Update member details."""
    result = await db.execute(select(Member).where(Member.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(member, field, value)

    await db.flush()
    await db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=204)
async def delete_member(
    member_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.MANAGER])),
):
    """Soft-delete a member (set inactive)."""
    result = await db.execute(select(Member).where(Member.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.is_active = False
    await db.flush()


@router.post("/{member_id}/upload-image", response_model=MemberResponse)
async def upload_profile_image(
    member_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(MEMBER_MANAGERS)),
):
    """Upload a profile image for a member."""
    import os
    from app.core.config import settings

    result = await db.execute(select(Member).where(Member.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are allowed")

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{member_id}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    member.profile_image = f"/uploads/{filename}"
    await db.flush()
    await db.refresh(member)
    return member
