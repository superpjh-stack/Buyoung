from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.common.response import ok
from app.common.exceptions import NotFoundError
from app.domains.equipment.models import Equipment, EquipmentSensorData
from app.domains.equipment.schemas import EquipmentOut, EquipmentStatusUpdate, SensorDataOut

router = APIRouter()


@router.get("")
async def list_equipment(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Equipment).where(Equipment.is_deleted == False))
    return ok([EquipmentOut.model_validate(e) for e in result.scalars()])


@router.get("/{equipment_id}")
async def get_equipment(equipment_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    eq = await db.get(Equipment, equipment_id)
    if not eq or eq.is_deleted:
        raise NotFoundError("설비를 찾을 수 없습니다.")
    return ok(EquipmentOut.model_validate(eq))


@router.put("/{equipment_id}/status")
async def update_status(
    equipment_id: UUID,
    body: EquipmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    eq = await db.get(Equipment, equipment_id)
    if not eq or eq.is_deleted:
        raise NotFoundError("설비를 찾을 수 없습니다.")
    eq.status = body.status
    return ok(EquipmentOut.model_validate(eq))


@router.get("/{equipment_id}/sensor-data")
async def get_sensor_data(
    equipment_id: UUID,
    from_: datetime = Query(alias="from"),
    to: datetime = Query(),
    interval: str = Query(default="5m"),
    metrics: str = Query(default="pressure,speed,current"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(EquipmentSensorData).where(
            and_(
                EquipmentSensorData.equipment_id == equipment_id,
                EquipmentSensorData.timestamp >= from_,
                EquipmentSensorData.timestamp <= to,
            )
        ).order_by(EquipmentSensorData.timestamp)
    )
    records = result.scalars().all()
    metric_list = [m.strip() for m in metrics.split(",")]
    series = []
    for r in records:
        row = {"timestamp": r.timestamp.isoformat(), "anomaly_flag": r.anomaly_flag}
        if "pressure" in metric_list:
            row["pressure_mpa"] = float(r.pressure_mpa) if r.pressure_mpa else None
        if "speed" in metric_list:
            row["speed_mpm"] = float(r.speed_mpm) if r.speed_mpm else None
        if "current" in metric_list:
            row["current_a"] = float(r.current_a) if r.current_a else None
        series.append(row)
    return ok({"equipment_id": str(equipment_id), "interval": interval, "series": series})
