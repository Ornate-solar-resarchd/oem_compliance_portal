"""User CRUD schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.common import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.engineer
    organisation: str | None = None
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    organisation: str | None = None
    is_active: bool | None = None


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: UserRole
    organisation: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
