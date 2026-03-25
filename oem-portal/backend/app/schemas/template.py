"""Compliance template schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TemplateParameterCreate(BaseModel):
    standard_parameter_id: UUID
    is_mandatory_override: bool | None = None
    sort_order: int = 0


class TemplateParameterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    standard_parameter_id: UUID
    is_mandatory_override: bool | None = None
    sort_order: int
    # Joined
    code: str | None = None
    display_name: str | None = None
    section: str | None = None


class TemplateCreate(BaseModel):
    name: str
    component_type_id: UUID
    description: str | None = None
    parameters: list[TemplateParameterCreate] = []


class TemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class TemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    component_type_id: UUID
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TemplateDetailResponse(TemplateResponse):
    parameters: list[TemplateParameterResponse] = []
