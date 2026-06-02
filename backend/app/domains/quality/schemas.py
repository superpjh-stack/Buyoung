from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class InspectionCreate(BaseModel):
    production_lot_id: UUID
    qs_id: UUID
    inspection_type: str = Field(pattern="^(INCOMING|IN_PROCESS|FINAL)$")
    result: str = Field(pattern="^(PASS|FAIL|HOLD)$")
    remarks: Optional[str] = None


class InspectionOut(BaseModel):
    inspection_id: UUID
    production_lot_id: UUID
    qs_id: UUID
    inspection_type: str
    inspector_id: UUID
    result: str
    remarks: Optional[str] = None
    inspected_at: datetime
    model_config = {"from_attributes": True}


class DefectRecordCreate(BaseModel):
    defect_type: str
    defect_location: Optional[str] = None
    severity: str = Field(pattern="^(CRITICAL|MAJOR|MINOR)$")
    corrective_action: Optional[str] = None


class DefectRecordOut(BaseModel):
    defect_id: UUID
    inspection_id: UUID
    production_lot_id: UUID
    defect_type: str
    defect_location: Optional[str] = None
    severity: str
    corrective_action: Optional[str] = None
    recorded_at: datetime
    model_config = {"from_attributes": True}
