"""Parameter schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.common import ParameterDataType, ExtractionSource


class StandardParameterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    component_type_id: UUID
    code: str
    display_name: str
    section: str
    data_type: ParameterDataType
    unit: str | None = None
    is_mandatory: bool
    acceptance_min: Decimal | None = None
    acceptance_max: Decimal | None = None
    acceptance_enum: list[str] | None = None
    regulatory_ref: str | None = None
    sort_order: int
    created_at: datetime


class ParameterValueCreate(BaseModel):
    standard_parameter_id: UUID
    value_raw: str | None = None
    value_jsonb: dict[str, Any] | None = None
    confidence: Decimal | None = None
    source: ExtractionSource = ExtractionSource.manual


class ParameterValueUpdate(BaseModel):
    value_raw: str | None = None
    value_jsonb: dict[str, Any] | None = None
    confidence: Decimal | None = None
    source: ExtractionSource | None = None
    is_verified: bool | None = None


class ParameterValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    component_model_id: UUID
    standard_parameter_id: UUID
    value_raw: str | None = None
    value_jsonb: dict[str, Any] | None = None
    confidence: Decimal | None = None
    source: ExtractionSource
    is_verified: bool
    extracted_at: datetime | None = None
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ParameterValueDetailResponse(ParameterValueResponse):
    """Includes joined standard parameter info."""
    code: str | None = None
    display_name: str | None = None
    section: str | None = None
    unit: str | None = None
    data_type: ParameterDataType | None = None
    is_mandatory: bool | None = None
    status: str | None = None  # compliance status when used in sheet context
