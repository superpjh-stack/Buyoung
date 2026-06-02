import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Numeric, String, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class CadDrawing(Base):
    __tablename__ = "cad_drawing"

    cad_drawing_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drawing_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("order.order_id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # DWG / PDF
    parsed_objects: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    parse_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    parsed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
