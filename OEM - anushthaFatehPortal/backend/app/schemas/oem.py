"""OEM schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class OEMCreate(BaseModel):
    name: str
    country_of_origin: str
    website: str | None = None
    contact_email: EmailStr | None = None
    notes: str | None = None


class OEMUpdate(BaseModel):
    name: str | None = None
    country_of_origin: str | None = None
    website: str | None = None
    contact_email: EmailStr | None = None
    notes: str | None = None


class OEMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    country_of_origin: str
    website: str | None = None
    contact_email: str | None = None
    is_approved: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    # Computed fields (populated by service)
    score: Decimal | None = None
    models_count: int | None = None
