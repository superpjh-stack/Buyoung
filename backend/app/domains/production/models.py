import uuid
from datetime import datetime, date, timezone
from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Integer, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class WorkOrder(Base):
    __tablename__ = "work_order"

    work_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_order_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("order.order_id"), nullable=False)
    bom_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bom.bom_id"), nullable=False)
    routing_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PLANNED", nullable=False)
    planned_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)

    production_lots: Mapped[list["ProductionLot"]] = relationship("ProductionLot", back_populates="work_order")


class ProductionLot(Base):
    __tablename__ = "production_lot"

    production_lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_lot_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    work_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("work_order.work_order_id"), nullable=False)
    lot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("receiving_lot.lot_id"), nullable=True)
    process_type: Mapped[str] = mapped_column(String(30), nullable=False)
    planned_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_qty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defect_qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="IN_PROGRESS", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    work_order: Mapped["WorkOrder"] = relationship("WorkOrder", back_populates="production_lots")
    forming_records: Mapped[list["FormingProcess"]] = relationship("FormingProcess", back_populates="production_lot")
    welding_records: Mapped[list["WeldingProcess"]] = relationship("WeldingProcess", back_populates="production_lot")
    packing_records: Mapped[list["PackingRecord"]] = relationship("PackingRecord", back_populates="production_lot")


class FormingProcess(Base):
    __tablename__ = "forming_process"

    forming_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("production_lot.production_lot_id"), nullable=False)
    equipment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    pressure_mpa: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    speed_mpm: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    temperature_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    bending_angle_deg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    cut_length_mm: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    defect_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defect_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    production_lot: Mapped["ProductionLot"] = relationship("ProductionLot", back_populates="forming_records")


class WeldingProcess(Base):
    __tablename__ = "welding_process"

    welding_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("production_lot.production_lot_id"), nullable=False)
    equipment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    current_a: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    voltage_v: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    speed_mpm: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    gas_flow_lpm: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    wire_feed_mpm: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    bead_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    defect_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defect_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    production_lot: Mapped["ProductionLot"] = relationship("ProductionLot", back_populates="welding_records")


class PackingRecord(Base):
    __tablename__ = "packing_record"

    packing_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("production_lot.production_lot_id"), nullable=False)
    work_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    packed_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    label_barcode: Mapped[str | None] = mapped_column(String(100), nullable=True)
    label_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PACKED", nullable=False)
    packed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    production_lot: Mapped["ProductionLot"] = relationship("ProductionLot", back_populates="packing_records")
