"""Workflow schemas."""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.common import ApprovalAction, WorkflowStage


class WorkflowAdvanceRequest(BaseModel):
    action: ApprovalAction
    comment: str | None = None

    @field_validator("comment")
    @classmethod
    def comment_required_for_reject(cls, v: str | None, info) -> str | None:
        # Validated at service level since we need access to action
        return v


class WorkflowStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    stage: WorkflowStage
    action: ApprovalAction
    actor_id: UUID
    comment: str | None = None
    signature_hash: str | None = None
    created_at: datetime
    # Joined
    actor_name: str | None = None


class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_number: str | None = None
    technical_sheet_id: UUID
    current_stage: WorkflowStage
    assigned_to: UUID | None = None
    due_date: date | None = None
    created_at: datetime
    updated_at: datetime
    # Joined
    sheet_number: str | None = None
    project_name: str | None = None
    model_name: str | None = None


class WorkflowDetailResponse(WorkflowResponse):
    steps: list[WorkflowStepResponse] = []
