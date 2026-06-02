from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.common.response import ok, paginated
from app.common.pagination import PaginationParams, get_pagination
from app.common.exceptions import NotFoundError
from app.domains.receiving.models import Supplier, ReceivingLot
from app.domains.receiving.schemas import SupplierOut

router = APIRouter()


class SupplierCreate:
    def __init__(self, supplier_code: str, supplier_name: str, quality_score: float | None = None):
        self.supplier_code = supplier_code
        self.supplier_name = supplier_name
        self.quality_score = quality_score


from pydantic import BaseModel
from typing import Optional


class SupplierCreateBody(BaseModel):
    supplier_code: str
    supplier_name: str
    quality_score: Optional[float] = None


@router.get("")
async def list_suppliers(
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(Supplier).where(Supplier.is_deleted == False)
    total = await db.scalar(select(func.count()).select_from(q.subquery()))
    result = await db.execute(q.offset(pagination.offset).limit(pagination.limit))
    suppliers = result.scalars().all()
    return paginated(
        [SupplierOut.model_validate(s) for s in suppliers],
        pagination.page, pagination.limit, total,
    )


@router.post("", status_code=201)
async def create_supplier(
    body: SupplierCreateBody,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("ADMIN", "MANAGER")),
):
    supplier = Supplier(**body.model_dump())
    db.add(supplier)
    await db.flush()
    return ok(SupplierOut.model_validate(supplier))


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    supplier = await db.get(Supplier, supplier_id)
    if not supplier or supplier.is_deleted:
        raise NotFoundError("공급업체를 찾을 수 없습니다.")
    return ok(SupplierOut.model_validate(supplier))


@router.get("/{supplier_id}/quality")
async def get_supplier_quality(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    supplier = await db.get(Supplier, supplier_id)
    if not supplier or supplier.is_deleted:
        raise NotFoundError("공급업체를 찾을 수 없습니다.")

    lot_stats = await db.execute(
        select(
            func.count(ReceivingLot.lot_id).label("lot_count"),
        ).where(
            ReceivingLot.supplier_id == supplier_id,
            ReceivingLot.is_deleted == False,
        )
    )
    row = lot_stats.one()

    return ok({
        "supplier_id": str(supplier.supplier_id),
        "supplier_code": supplier.supplier_code,
        "supplier_name": supplier.supplier_name,
        "quality_score": float(supplier.quality_score) if supplier.quality_score is not None else None,
        "lot_count": row.lot_count,
    })
