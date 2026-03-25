"""AI Extraction Job ORM model."""
from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ExtractionJobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class AIExtractionJob(Base):
    __tablename__ = "ai_extraction_jobs"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    component_model_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("component_models.id", ondelete="CASCADE"), nullable=False)
    minio_key: Mapped[str] = mapped_column(Text, nullable=False)
    celery_task_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ExtractionJobStatus] = mapped_column(
        PgEnum(ExtractionJobStatus, name="extraction_job_status", create_type=False),
        nullable=False,
        server_default="queued",
    )
    parameters_extracted: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    parameters_auto_verified: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    parameters_flagged: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    parameters_manual: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    error_message: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column()

    # Relationships
    component_model: Mapped["ComponentModel"] = relationship("ComponentModel")
