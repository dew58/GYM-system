"""
Inventory router — CRUD items, transactions (sale/purchase), low-stock alerts.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.inventory import InventoryItem, InventoryTransaction, TransactionType
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    InventoryTransactionCreate, InventoryTransactionResponse,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])
INVENTORY_ROLES = [UserRole.SUPER_ADMIN, UserRole.MANAGER]


@router.get("", response_model=list[InventoryItemResponse])
async def list_items(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(InventoryItem).order_by(InventoryItem.name))
    return result.scalars().all()


@router.post("", response_model=InventoryItemResponse, status_code=201)
async def create_item(data: InventoryItemCreate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(INVENTORY_ROLES))):
    item = InventoryItem(**data.model_dump())
    db.add(item); await db.flush(); await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_item(item_id: str, data: InventoryItemUpdate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(INVENTORY_ROLES))):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(status_code=404, detail="Item not found")
    for f, v in data.model_dump(exclude_unset=True).items(): setattr(item, f, v)
    await db.flush(); await db.refresh(item)
    return item


@router.get("/low-stock", response_model=list[InventoryItemResponse])
async def low_stock_alerts(db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(INVENTORY_ROLES))):
    result = await db.execute(select(InventoryItem).where(
        InventoryItem.quantity <= InventoryItem.low_stock_threshold, InventoryItem.is_active == True))
    return result.scalars().all()


@router.post("/transactions", response_model=InventoryTransactionResponse, status_code=201)
async def create_transaction(data: InventoryTransactionCreate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == data.item_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(status_code=404, detail="Item not found")
    if data.transaction_type == TransactionType.SALE:
        if item.quantity < data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        item.quantity -= data.quantity
    elif data.transaction_type == TransactionType.PURCHASE:
        item.quantity += data.quantity
    elif data.transaction_type == TransactionType.RETURN:
        item.quantity += data.quantity
    txn = InventoryTransaction(**data.model_dump())
    db.add(txn); await db.flush(); await db.refresh(txn)
    return txn


@router.get("/transactions", response_model=list[InventoryTransactionResponse])
async def list_transactions(item_id: Optional[str] = None, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    query = select(InventoryTransaction).order_by(InventoryTransaction.created_at.desc())
    if item_id: query = query.where(InventoryTransaction.item_id == item_id)
    result = await db.execute(query.limit(100))
    return result.scalars().all()
