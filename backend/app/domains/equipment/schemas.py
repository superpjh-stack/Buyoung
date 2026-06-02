from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class EquipmentOut(BaseModel):
    equipment_id: UUID
    equipment_code: str
    equipment_name: str
    process_type: str
    plc_id: Optional[UUID] = None
    status: str
    model_config = {"from_attributes": True}


class EquipmentStatusUpdate(BaseModel):
    status: str = Field(pattern="^(IDLE|RUNNING|MAINTENANCE|ERROR)$")


class SensorDataCreate(BaseModel):
    equipment_id: UUID
    timestamp: datetime
    pressure_mpa: Optional[float] = None
    speed_mpm: Optional[float] = None
    current_a: Optional[float] = None
    voltage_v: Optional[float] = None
    temperature_c: Optional[float] = None
    vibration_mm: Optional[float] = None
    production_count: Optional[int] = None
    anomaly_flag: bool = False
    sensor_snapshot: Optional[dict] = None


class SensorDataOut(BaseModel):
    sensor_record_id: UUID
    equipment_id: UUID
    timestamp: datetime
    pressure_mpa: Optional[float] = None
    speed_mpm: Optional[float] = None
    current_a: Optional[float] = None
    voltage_v: Optional[float] = None
    temperature_c: Optional[float] = None
    anomaly_flag: bool
    model_config = {"from_attributes": True}
