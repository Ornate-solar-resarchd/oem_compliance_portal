"""AI extraction job schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractionJobCreate(BaseModel):
    component_model_id: UUID
    minio_key: str


class ExtractionJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    component_model_id: UUID
    minio_key: str
    celery_task_id: str | None = None
    status: str  # queued, running, done, failed
    parameters_extracted: int
    parameters_auto_verified: int
    parameters_flagged: int
    parameters_manual: int
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class VerifyParameterRequest(BaseModel):
    is_correct: bool
    corrected_value: str | None = None
