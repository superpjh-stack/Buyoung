import uuid
from datetime import datetime, date, timezone
from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Supplier(Base):
    __tablename__ = "supplier"

    supplier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(100), nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)

    lots: Mapped[list["ReceivingLot"]] = relationship("ReceivingLot", back_populates="supplier")


class Material(Base):
    __tablename__ = "material"

    material_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    material_name: Mapped[str] = mapped_column(String(100), nullable=False)
    material_type: Mapped[str] = mapped_column(String(30), nullable=False)
    spec: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    standard_unit_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)


class ReceivingLot(Base):
    __tablename__ = "receiving_lot"

    lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("supplier.supplier_id"), nullable=False)
    material_code: Mapped[str] = mapped_column(String(30), nullable=False)
    received_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    thickness_mm: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    inspection_result: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    storage_location: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="lots")


class InventoryStock(Base):
    __tablename__ = "inventory_stock"

    stock_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_code: Mapped[str] = mapped_column(String(30), nullable=False)
    location_code: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity_on_hand: Mapped[float] = mapped_column(Numeric(10, 3), default=0, nullable=False)
    quantity_allocated: Mapped[float] = mapped_column(Numeric(10, 3), default=0, nullable=False)
    quantity_available: Mapped[float] = mapped_column(Numeric(10, 3), default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)


class MaterialAllocation(Base):
    __tablename__ = "material_allocation"

    allocation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("receiving_lot.lot_id"), nullable=False)
    work_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="RESERVED", nullable=False)
    allocated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
