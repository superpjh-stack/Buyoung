from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.common.response import ok, paginated
from app.common.pagination import PaginationParams, get_pagination
from app.common.exceptions import NotFoundError
from app.domains.receiving.models import InventoryStock

router = APIRouter()


class AvailabilityCheckBody(BaseModel):
    material_code: str
    required_qty: float = Field(gt=0)


@router.get("")
async def list_inventory(
    material_code: Optional[str] = None,
    location_code: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(InventoryStock)
    if material_code:
        q = q.where(InventoryStock.material_code == material_code)
    if location_code:
        q = q.where(InventoryStock.location_code == location_code)
    total = await db.scalar(select(func.count()).select_from(q.subquery()))
    result = await db.execute(q.offset(pagination.offset).limit(pagination.limit))
    stocks = result.scalars().all()
    return paginated(
        [
            {
                "stock_id": str(s.stock_id),
                "material_code": s.material_code,
                "location_code": s.location_code,
                "quantity_on_hand": float(s.quantity_on_hand),
                "quantity_allocated": float(s.quantity_allocated),
                "quantity_available": float(s.quantity_available),
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in stocks
        ],
        pagination.page, pagination.limit, total,
    )


@router.get("/{material_code}")
async def get_inventory_by_material(
    material_code: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(InventoryStock).where(InventoryStock.material_code == material_code)
    )
    stocks = result.scalars().all()
    if not stocks:
        raise NotFoundError("해당 자재의 재고 정보를 찾을 수 없습니다.")

    total_available = sum(float(s.quantity_available) for s in stocks)

    return ok({
        "material_code": material_code,
        "total_available": total_available,
        "locations": [
            {
                "stock_id": str(s.stock_id),
                "location_code": s.location_code,
                "quantity_on_hand": float(s.quantity_on_hand),
                "quantity_allocated": float(s.quantity_allocated),
                "quantity_available": float(s.quantity_available),
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in stocks
        ],
    })


@router.post("/check-availability")
async def check_availability(
    body: AvailabilityCheckBody,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(
            func.coalesce(func.sum(InventoryStock.quantity_available), 0).label("total_available")
        ).where(InventoryStock.material_code == body.material_code)
    )
    total_available = float(result.scalar())
    is_available = total_available >= body.required_qty

    return ok({
        "material_code": body.material_code,
        "required_qty": body.required_qty,
        "available_qty": total_available,
        "is_available": is_available,
        "shortage": max(0.0, body.required_qty - total_available),
    })
