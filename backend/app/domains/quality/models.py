import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class QualityStandard(Base):
    __tablename__ = "quality_standard"

    qs_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    qs_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    product_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    process_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    criteria: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class QualityInspection(Base):
    __tablename__ = "quality_inspection"

    inspection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("production_lot.production_lot_id"), nullable=False)
    qs_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quality_standard.qs_id"), nullable=False)
    inspection_type: Mapped[str] = mapped_column(String(20), nullable=False)  # INCOMING/IN_PROCESS/FINAL
    inspector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    result: Mapped[str] = mapped_column(String(10), nullable=False)  # PASS/FAIL/HOLD
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    inspected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    defects: Mapped[list["DefectRecord"]] = relationship("DefectRecord", back_populates="inspection")


class DefectRecord(Base):
    __tablename__ = "defect_record"

    defect_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quality_inspection.inspection_id"), nullable=False)
    production_lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("production_lot.production_lot_id"), nullable=False)
    defect_type: Mapped[str] = mapped_column(String(50), nullable=False)
    defect_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # CRITICAL/MAJOR/MINOR
    corrective_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    inspection: Mapped["QualityInspection"] = relationship("QualityInspection", back_populates="defects")
