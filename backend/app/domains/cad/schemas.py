from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class CadDrawingOut(BaseModel):
    cad_drawing_id: UUID
    drawing_no: str
    order_id: UUID
    file_path: str
    file_type: str
    parse_status: str
    confidence_score: Optional[float] = None
    parsed_objects: Optional[dict] = None
    parsed_at: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ParseStatusOut(BaseModel):
    drawing_id: UUID
    parse_status: str
