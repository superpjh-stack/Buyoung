from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class ShippingOrderCreate(BaseModel):
    order_id: UUID
    customer_id: UUID
    planned_ship_date: Optional[date] = None


class ShippingOrderOut(BaseModel):
    shipping_order_id: UUID
    shipping_order_no: str
    order_id: UUID
    customer_id: UUID
    planned_ship_date: Optional[date] = None
    shipping_status: str
    delivery_risk_flag: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class ShippingLotCreate(BaseModel):
    production_lot_id: UUID
    shipped_qty: int = Field(gt=0)
    tracking_no: Optional[str] = None
    shipped_date: Optional[date] = None


class ShippingLotOut(BaseModel):
    shipping_lot_id: UUID
    shipping_order_id: UUID
    production_lot_id: UUID
    shipped_qty: int
    tracking_no: Optional[str] = None
    shipped_date: Optional[date] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ClaimCreate(BaseModel):
    customer_id: UUID
    shipping_lot_id: Optional[UUID] = None
    claim_type: str
    claim_severity: str = Field(pattern="^(CRITICAL|MAJOR|MINOR)$")
    description: str


class ClaimOut(BaseModel):
    claim_id: UUID
    claim_no: str
    customer_id: UUID
    claim_type: str
    claim_severity: str
    status: str
    description: str
    root_cause: Optional[str] = None
    claim_date: date
    created_at: datetime
    model_config = {"from_attributes": True}
