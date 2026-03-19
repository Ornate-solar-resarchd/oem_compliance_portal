"""Auth request/response schemas."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, ConfigDict


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPayload(BaseModel):
    sub: str
    email: str
    name: str
    role: str
    org: str
    exp: int
    iat: int


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str
    role: str
    organisation: str | None = None


class LoginResponse(BaseModel):
    token: str
    user: UserInfo
