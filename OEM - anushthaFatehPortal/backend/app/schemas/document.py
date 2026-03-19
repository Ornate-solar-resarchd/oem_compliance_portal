"""Document generation schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.common import DocumentFormat, DocumentType


class DocumentGenerateRequest(BaseModel):
    document_type: DocumentType
    format: DocumentFormat
    technical_sheet_id: UUID | None = None
    project_id: UUID | None = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    technical_sheet_id: UUID | None = None
    project_id: UUID | None = None
    document_type: DocumentType
    format: DocumentFormat
    minio_key: str | None = None
    file_size_bytes: int | None = None
    sha256: str | None = None
    is_ready: bool
    error_message: str | None = None
    created_at: datetime
    ready_at: datetime | None = None


class DocumentStatusResponse(BaseModel):
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE
    result: dict | None = None
