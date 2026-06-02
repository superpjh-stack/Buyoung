from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.common.response import ok, paginated
from app.common.pagination import PaginationParams, get_pagination
from app.common.exceptions import NotFoundError
from app.domains.receiving.models import Material, InventoryStock
from app.domains.receiving.schemas import MaterialOut

router = APIRouter()


class MaterialCreateBody(BaseModel):
    material_code: str
    material_name: str
    material_type: str
    spec: Optional[str] = None
    unit: str
    standard_unit_price: Optional[float] = None


@router.get("")
async def list_materials(
    material_type: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(Material).where(Material.is_deleted == False)
    if material_type:
        q = q.where(Material.material_type == material_type)
    total = await db.scalar(select(func.count()).select_from(q.subquery()))
    result = await db.execute(q.offset(pagination.offset).limit(pagination.limit))
    materials = result.scalars().all()
    return paginated(
        [MaterialOut.model_validate(m) for m in materials],
        pagination.page, pagination.limit, total,
    )


@router.post("", status_code=201)
async def create_material(
    body: MaterialCreateBody,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("ADMIN", "MANAGER")),
):
    material = Material(**body.model_dump())
    db.add(material)
    await db.flush()
    return ok(MaterialOut.model_validate(material))


@router.get("/{material_code}")
async def get_material(
    material_code: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(Material).where(
            Material.material_code == material_code,
            Material.is_deleted == False,
        )
    )
    material = result.scalar_one_or_none()
    if not material:
        raise NotFoundError("자재를 찾을 수 없습니다.")
    return ok(MaterialOut.model_validate(material))


@router.get("/{material_code}/stock")
async def get_material_stock(
    material_code: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    mat_result = await db.execute(
        select(Material).where(
            Material.material_code == material_code,
            Material.is_deleted == False,
        )
    )
    material = mat_result.scalar_one_or_none()
    if not material:
        raise NotFoundError("자재를 찾을 수 없습니다.")

    stock_result = await db.execute(
        select(InventoryStock).where(InventoryStock.material_code == material_code)
    )
    stocks = stock_result.scalars().all()

    total_on_hand = sum(float(s.quantity_on_hand) for s in stocks)
    total_allocated = sum(float(s.quantity_allocated) for s in stocks)
    total_available = sum(float(s.quantity_available) for s in stocks)

    return ok({
        "material_code": material_code,
        "material_name": material.material_name,
        "unit": material.unit,
        "locations": [
            {
                "location_code": s.location_code,
                "quantity_on_hand": float(s.quantity_on_hand),
                "quantity_allocated": float(s.quantity_allocated),
                "quantity_available": float(s.quantity_available),
            }
            for s in stocks
        ],
        "totals": {
            "quantity_on_hand": total_on_hand,
            "quantity_allocated": total_allocated,
            "quantity_available": total_available,
        },
    })
