import uuid
from datetime import datetime, date, timezone
from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Integer, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class ShippingOrder(Base):
    __tablename__ = "shipping_order"

    shipping_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipping_order_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("order.order_id"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customer.customer_id"), nullable=False)
    planned_ship_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    shipping_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    delivery_risk_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)

    lots: Mapped[list["ShippingLot"]] = relationship("ShippingLot", back_populates="shipping_order")


class ShippingLot(Base):
    __tablename__ = "shipping_lot"

    shipping_lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipping_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shipping_order.shipping_order_id"), nullable=False)
    production_lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("production_lot.production_lot_id"), nullable=False)
    shipped_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    tracking_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shipped_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    shipping_order: Mapped["ShippingOrder"] = relationship("ShippingOrder", back_populates="lots")


class Claim(Base):
    __tablename__ = "claim"

    claim_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customer.customer_id"), nullable=False)
    shipping_lot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("shipping_lot.shipping_lot_id"), nullable=True)
    claim_type: Mapped[str] = mapped_column(String(30), nullable=False)
    claim_severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    claim_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)
