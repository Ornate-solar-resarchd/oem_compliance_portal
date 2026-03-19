"""Technical sheet schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.common import WorkflowStage, ComplianceStatus


class SheetCreate(BaseModel):
    project_id: UUID
    component_model_id: UUID
    compliance_template_id: UUID | None = None


class ComplianceResultUpdate(BaseModel):
    standard_parameter_id: UUID
    oem_value: str | None = None


class ComplianceResultBulkUpdate(BaseModel):
    results: list[ComplianceResultUpdate]


class WaiveRequest(BaseModel):
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_min_length(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Waive reason must be at least 10 characters")
        return v.strip()


class ComplianceResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    technical_sheet_id: UUID
    standard_parameter_id: UUID
    oem_value: str | None = None
    status: ComplianceStatus
    waive_reason: str | None = None
    waived_by: UUID | None = None
    waived_at: datetime | None = None
    evaluated_at: datetime | None = None
    # Joined fields
    code: str | None = None
    display_name: str | None = None
    section: str | None = None
    unit: str | None = None
    is_mandatory: bool | None = None


class SheetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sheet_number: str | None = None
    project_id: UUID
    component_model_id: UUID
    stage: WorkflowStage
    revision: int
    compliance_score: Decimal | None = None
    pass_count: int
    fail_count: int
    waived_count: int
    pending_count: int
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    # Joined
    project_name: str | None = None
    model_name: str | None = None
    oem_name: str | None = None


class SheetDetailResponse(SheetResponse):
    results: list[ComplianceResultResponse] = []
    versions_count: int = 0


class SheetVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    technical_sheet_id: UUID
    revision: int
    stage: WorkflowStage
    snapshot: dict[str, Any]
    created_at: datetime


class SheetScoreResponse(BaseModel):
    compliance_score: Decimal | None = None
    pass_count: int
    fail_count: int
    waived_count: int
    pending_count: int
    total: int
