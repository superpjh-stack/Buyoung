from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.common.response import ok
from app.common.exceptions import NotFoundError
from app.domains.quality.models import QualityInspection, DefectRecord
from app.domains.quality.schemas import (
    InspectionCreate, InspectionOut,
    DefectRecordCreate, DefectRecordOut,
)

router = APIRouter()


@router.post("", status_code=201)
async def create_inspection(
    body: InspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    inspection = QualityInspection(**body.model_dump(), inspector_id=current_user.user_id)
    db.add(inspection)
    await db.flush()
    return ok(InspectionOut.model_validate(inspection))


@router.get("/{inspection_id}")
async def get_inspection(inspection_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    inspection = await db.get(QualityInspection, inspection_id)
    if not inspection:
        raise NotFoundError("검사 결과를 찾을 수 없습니다.")
    return ok(InspectionOut.model_validate(inspection))


@router.post("/{inspection_id}/defects", status_code=201)
async def create_defect(
    inspection_id: UUID,
    body: DefectRecordCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    inspection = await db.get(QualityInspection, inspection_id)
    if not inspection:
        raise NotFoundError("검사 결과를 찾을 수 없습니다.")
    defect = DefectRecord(
        inspection_id=inspection_id,
        production_lot_id=inspection.production_lot_id,
        **body.model_dump(),
    )
    db.add(defect)
    await db.flush()
    return ok(DefectRecordOut.model_validate(defect))


@router.get("/{inspection_id}/defects")
async def list_defects(inspection_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(DefectRecord).where(DefectRecord.inspection_id == inspection_id)
    )
    return ok([DefectRecordOut.model_validate(d) for d in result.scalars()])
