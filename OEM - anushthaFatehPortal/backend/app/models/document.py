"""Document (generated exports) ORM model."""
from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DocumentFormat(str, enum.Enum):
    pdf = "pdf"
    excel = "excel"
    pptx = "pptx"


class DocumentType(str, enum.Enum):
    compliance_sheet = "compliance_sheet"
    comparison_report = "comparison_report"
    customer_proposal = "customer_proposal"
    audit_export = "audit_export"
    full_project_pack = "full_project_pack"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    technical_sheet_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("technical_sheets.id", ondelete="SET NULL"))
    project_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"))
    document_type: Mapped[DocumentType] = mapped_column(PgEnum(DocumentType, name="document_type", create_type=False), nullable=False)
    format: Mapped[DocumentFormat] = mapped_column(PgEnum(DocumentFormat, name="document_format", create_type=False), nullable=False)
    minio_key: Mapped[str | None] = mapped_column(Text)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    sha256: Mapped[str | None] = mapped_column(Text)
    generated_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    celery_task_id: Mapped[str | None] = mapped_column(Text)
    is_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    ready_at: Mapped[datetime | None] = mapped_column()

    # Relationships
    technical_sheet: Mapped["TechnicalSheet | None"] = relationship("TechnicalSheet", back_populates="documents")
    project: Mapped["Project | None"] = relationship("Project", back_populates="documents")
