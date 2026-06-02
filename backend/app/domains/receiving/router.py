from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.common.response import ok, paginated
from app.common.pagination import PaginationParams, get_pagination
from app.common.exceptions import NotFoundError
from app.domains.receiving.models import ReceivingLot, InventoryStock, Supplier, Material
from app.domains.receiving.schemas import (
    ReceivingLotCreate, ReceivingLotOut, InspectionUpdate,
    SupplierOut, MaterialOut,
)

router = APIRouter()


@router.get("")
async def list_lots(
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    total = await db.scalar(select(func.count()).where(ReceivingLot.is_deleted == False))
    result = await db.execute(
        select(ReceivingLot).where(ReceivingLot.is_deleted == False)
        .offset(pagination.offset).limit(pagination.limit)
    )
    lots = result.scalars().all()
    return paginated([ReceivingLotOut.model_validate(l) for l in lots],
                     pagination.page, pagination.limit, total)


@router.post("", status_code=201)
async def create_lot(
    body: ReceivingLotCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    import uuid
    lot_no = f"LOT-{__import__('datetime').datetime.now().strftime('%Y%m%d%H%M%S')}"
    lot = ReceivingLot(lot_no=lot_no, **body.model_dump())
    db.add(lot)
    await db.flush()
    return ok(ReceivingLotOut.model_validate(lot))


@router.get("/{lot_id}")
async def get_lot(lot_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    lot = await db.get(ReceivingLot, lot_id)
    if not lot or lot.is_deleted:
        raise NotFoundError("입고 LOT를 찾을 수 없습니다.")
    return ok(ReceivingLotOut.model_validate(lot))


@router.put("/{lot_id}/inspection")
async def update_inspection(
    lot_id: UUID,
    body: InspectionUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    lot = await db.get(ReceivingLot, lot_id)
    if not lot or lot.is_deleted:
        raise NotFoundError("입고 LOT를 찾을 수 없습니다.")
    lot.inspection_result = body.inspection_result
    return ok(ReceivingLotOut.model_validate(lot))


@router.get("/{lot_id}/traceability")
async def lot_traceability(lot_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    lot = await db.get(ReceivingLot, lot_id)
    if not lot:
        raise NotFoundError("입고 LOT를 찾을 수 없습니다.")
    # TODO: 생산 LOT 연계 조회
    return ok({"lot_id": str(lot_id), "lot_no": lot.lot_no, "material_code": lot.material_code})
