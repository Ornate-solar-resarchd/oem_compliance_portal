"""Project schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.common import ProjectType, ProjectStatus


class ProjectCreate(BaseModel):
    name: str
    client_name: str
    project_type: ProjectType
    capacity_kwh: Decimal | None = None
    power_kw: Decimal | None = None
    location: str | None = None
    state: str | None = None
    customer_user_id: UUID | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    client_name: str | None = None
    status: ProjectStatus | None = None
    capacity_kwh: Decimal | None = None
    power_kw: Decimal | None = None
    location: str | None = None
    state: str | None = None
    customer_user_id: UUID | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    client_name: str
    project_type: ProjectType
    status: ProjectStatus
    capacity_kwh: Decimal | None = None
    power_kw: Decimal | None = None
    location: str | None = None
    state: str | None = None
    created_at: datetime
    updated_at: datetime
    # Computed
    sheets_count: int | None = None
    progress: float | None = None


class ProjectDetailResponse(ProjectResponse):
    sheets: list[dict] = []
