from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class WorkOrderCreate(BaseModel):
    order_id: UUID
    bom_id: UUID
    planned_qty: int = Field(gt=0)
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None


class WorkOrderOut(BaseModel):
    work_order_id: UUID
    work_order_no: str
    order_id: UUID
    bom_id: UUID
    status: str
    planned_qty: int
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ProductionLotOut(BaseModel):
    production_lot_id: UUID
    production_lot_no: str
    work_order_id: UUID
    process_type: str
    planned_qty: int
    actual_qty: Optional[int] = None
    defect_qty: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ActualQtyUpdate(BaseModel):
    actual_qty: int = Field(ge=0)
    defect_qty: int = Field(ge=0, default=0)


class FormingProcessCreate(BaseModel):
    equipment_id: UUID
    pressure_mpa: Optional[float] = None
    speed_mpm: Optional[float] = None
    temperature_c: Optional[float] = None
    bending_angle_deg: Optional[float] = None
    cut_length_mm: Optional[float] = None
    defect_count: int = 0
    defect_flag: bool = False


class FormingProcessOut(BaseModel):
    forming_id: UUID
    production_lot_id: UUID
    equipment_id: UUID
    pressure_mpa: Optional[float] = None
    speed_mpm: Optional[float] = None
    defect_count: int
    defect_flag: bool
    recorded_at: datetime
    model_config = {"from_attributes": True}


class WeldingProcessCreate(BaseModel):
    equipment_id: UUID
    current_a: Optional[float] = None
    voltage_v: Optional[float] = None
    speed_mpm: Optional[float] = None
    gas_flow_lpm: Optional[float] = None
    wire_feed_mpm: Optional[float] = None
    defect_count: int = 0
    defect_flag: bool = False


class WeldingProcessOut(BaseModel):
    welding_id: UUID
    production_lot_id: UUID
    equipment_id: UUID
    current_a: Optional[float] = None
    voltage_v: Optional[float] = None
    defect_count: int
    defect_flag: bool
    recorded_at: datetime
    model_config = {"from_attributes": True}


class PackingRecordCreate(BaseModel):
    work_order_id: UUID
    packed_qty: int = Field(gt=0)
    label_barcode: Optional[str] = None
    label_info: Optional[dict] = None


class PackingRecordOut(BaseModel):
    packing_id: UUID
    production_lot_id: UUID
    work_order_id: UUID
    packed_qty: int
    label_barcode: Optional[str] = None
    status: str
    packed_at: datetime
    model_config = {"from_attributes": True}
