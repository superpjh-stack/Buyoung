import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Numeric, String, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class PLCController(Base):
    __tablename__ = "plc_controller"

    plc_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plc_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    plc_type: Mapped[str] = mapped_column(String(20), nullable=False)  # MASTER / SLAVE
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    protocol: Mapped[str] = mapped_column(String(20), nullable=False)  # OPC-UA / Modbus / MQTT
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    equipment: Mapped[list["Equipment"]] = relationship("Equipment", back_populates="plc")


class Equipment(Base):
    __tablename__ = "equipment"

    equipment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    equipment_name: Mapped[str] = mapped_column(String(100), nullable=False)
    process_type: Mapped[str] = mapped_column(String(30), nullable=False)
    plc_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("plc_controller.plc_id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="IDLE", nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow)

    plc: Mapped["PLCController | None"] = relationship("PLCController", back_populates="equipment")
    sensor_data: Mapped[list["EquipmentSensorData"]] = relationship("EquipmentSensorData", back_populates="equipment")


class EquipmentSensorData(Base):
    """TimescaleDB Hypertable — 파티셔닝 키: timestamp"""
    __tablename__ = "equipment_sensor_data"

    sensor_record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.equipment_id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    pressure_mpa: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    speed_mpm: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    current_a: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    voltage_v: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    temperature_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    vibration_mm: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    production_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    anomaly_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sensor_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="sensor_data")
