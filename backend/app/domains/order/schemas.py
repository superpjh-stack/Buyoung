from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class CustomerCreate(BaseModel):
    customer_code: str
    customer_name: str
    contact_info: Optional[dict] = None


class CustomerOut(BaseModel):
    customer_id: UUID
    customer_code: str
    customer_name: str
    contact_info: Optional[dict] = None
    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_id: UUID
    product_type: str
    product_spec: Optional[dict] = None
    requested_delivery_date: Optional[date] = None
    quantity: Optional[int] = None


class OrderOut(BaseModel):
    order_id: UUID
    order_no: str
    customer_id: UUID
    status: str
    product_type: str
    product_spec: Optional[dict] = None
    requested_delivery_date: Optional[date] = None
    quantity: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class QuoteOut(BaseModel):
    quote_id: UUID
    quote_no: str
    order_id: UUID
    total_amount: Optional[float] = None
    material_cost: Optional[float] = None
    process_cost: Optional[float] = None
    process_cost_breakdown: Optional[dict] = None
    shap_explanation: Optional[dict] = None
    confidence_score: Optional[float] = None
    estimated_lead_time_days: Optional[int] = None
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    contact_info: Optional[dict] = None


class QuoteTrigger(BaseModel):
    drawing_id: UUID
    material_price_override: Optional[dict] = None


class BOMOut(BaseModel):
    bom_id: UUID
    order_id: UUID
    bom_version: str
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}
