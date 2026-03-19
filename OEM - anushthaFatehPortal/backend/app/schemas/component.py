"""Component type and model schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.common import ComponentCategory


class ComponentTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: ComponentCategory
    description: str | None = None
    created_at: datetime


class ComponentModelCreate(BaseModel):
    oem_id: UUID
    component_type_id: UUID
    model_name: str
    datasheet_url: str | None = None


class ComponentModelUpdate(BaseModel):
    model_name: str | None = None
    datasheet_url: str | None = None
    is_active: bool | None = None


class ComponentModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    oem_id: UUID
    component_type_id: UUID
    model_name: str
    datasheet_url: str | None = None
    is_active: bool
    fill_rate: Decimal | None = None
    compliance_score: Decimal | None = None
    created_at: datetime
    updated_at: datetime
    # Joined fields
    oem_name: str | None = None
    component_type_name: str | None = None


class ComponentModelDetailResponse(ComponentModelResponse):
    parameters: list[dict] = []  # parameter values grouped by section
