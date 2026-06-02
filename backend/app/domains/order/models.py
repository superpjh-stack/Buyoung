import uuid
from datetime import datetime, date, timezone
from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Integer, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Customer(Base):
    __tablename__ = "customer"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "order"

    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customer.customer_id"), nullable=False)
    cad_drawing_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cad_drawing.cad_drawing_id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="RECEIVED", nullable=False)
    product_type: Mapped[str] = mapped_column(String(50), nullable=False)
    product_spec: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    requested_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    cad_drawing: Mapped["CadDrawing | None"] = relationship("CadDrawing", foreign_keys=[cad_drawing_id])
    quotes: Mapped[list["Quote"]] = relationship("Quote", back_populates="order")
    boms: Mapped[list["BOM"]] = relationship("BOM", back_populates="order")


class Quote(Base):
    __tablename__ = "quote"

    quote_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("order.order_id"), nullable=False)
    ml_model_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    total_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    material_cost: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    process_cost: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    process_cost_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    shap_explanation: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    estimated_lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="AUTO", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    order: Mapped["Order"] = relationship("Order", back_populates="quotes")


class BOM(Base):
    __tablename__ = "bom"

    bom_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("order.order_id"), nullable=False)
    quote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("quote.quote_id"), nullable=True)
    bom_version: Mapped[str] = mapped_column(String(10), default="v1", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    order: Mapped["Order"] = relationship("Order", back_populates="boms")
    lines: Mapped[list["BOMLine"]] = relationship("BOMLine", back_populates="bom")


class BOMLine(Base):
    __tablename__ = "bom_line"

    bom_line_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bom_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bom.bom_id"), nullable=False)
    material_code: Mapped[str] = mapped_column(String(30), nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    process_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    unit_cost: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    bom: Mapped["BOM"] = relationship("BOM", back_populates="lines")


# Forward reference — defined in cad domain but referenced here
from app.domains.cad.models import CadDrawing  # noqa: E402, F401
