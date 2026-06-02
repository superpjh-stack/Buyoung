from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class ReceivingLotCreate(BaseModel):
    supplier_id: UUID
    material_code: str
    received_date: date
    quantity: float = Field(gt=0)
    weight_kg: Optional[float] = None
    thickness_mm: Optional[float] = None
    storage_location: Optional[str] = None


class InspectionUpdate(BaseModel):
    inspection_result: str = Field(pattern="^(PASS|FAIL|HOLD|PENDING)$")


class ReceivingLotOut(BaseModel):
    lot_id: UUID
    lot_no: str
    supplier_id: UUID
    material_code: str
    received_date: date
    quantity: float
    weight_kg: Optional[float] = None
    thickness_mm: Optional[float] = None
    inspection_result: str
    storage_location: Optional[str] = None
    model_config = {"from_attributes": True}


class SupplierOut(BaseModel):
    supplier_id: UUID
    supplier_code: str
    supplier_name: str
    quality_score: Optional[float] = None
    model_config = {"from_attributes": True}


class MaterialOut(BaseModel):
    material_id: UUID
    material_code: str
    material_name: str
    material_type: str
    unit: str
    standard_unit_price: Optional[float] = None
    model_config = {"from_attributes": True}
