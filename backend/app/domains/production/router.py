from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.common.response import ok
from app.common.exceptions import NotFoundError
from app.domains.production.models import ProductionLot, FormingProcess, WeldingProcess, PackingRecord
from app.domains.production.schemas import (
    ProductionLotOut, ActualQtyUpdate,
    FormingProcessCreate, FormingProcessOut,
    WeldingProcessCreate, WeldingProcessOut,
    PackingRecordCreate, PackingRecordOut,
)

router = APIRouter()


@router.get("/{lot_id}")
async def get_production_lot(lot_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    lot = await db.get(ProductionLot, lot_id)
    if not lot:
        raise NotFoundError("생산 LOT를 찾을 수 없습니다.")
    return ok(ProductionLotOut.model_validate(lot))


@router.put("/{lot_id}/actual-qty")
async def update_actual_qty(
    lot_id: UUID,
    body: ActualQtyUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    lot = await db.get(ProductionLot, lot_id)
    if not lot:
        raise NotFoundError("생산 LOT를 찾을 수 없습니다.")
    lot.actual_qty = body.actual_qty
    lot.defect_qty = body.defect_qty
    return ok(ProductionLotOut.model_validate(lot))


@router.post("/{lot_id}/forming", status_code=201)
async def create_forming(
    lot_id: UUID,
    body: FormingProcessCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    record = FormingProcess(production_lot_id=lot_id, **body.model_dump())
    db.add(record)
    await db.flush()
    return ok(FormingProcessOut.model_validate(record))


@router.get("/{lot_id}/forming")
async def list_forming(lot_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(FormingProcess).where(FormingProcess.production_lot_id == lot_id))
    return ok([FormingProcessOut.model_validate(r) for r in result.scalars()])


@router.post("/{lot_id}/welding", status_code=201)
async def create_welding(
    lot_id: UUID,
    body: WeldingProcessCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    record = WeldingProcess(production_lot_id=lot_id, **body.model_dump())
    db.add(record)
    await db.flush()
    return ok(WeldingProcessOut.model_validate(record))


@router.post("/{lot_id}/packing", status_code=201)
async def create_packing(
    lot_id: UUID,
    body: PackingRecordCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    record = PackingRecord(production_lot_id=lot_id, **body.model_dump())
    db.add(record)
    await db.flush()
    return ok(PackingRecordOut.model_validate(record))
