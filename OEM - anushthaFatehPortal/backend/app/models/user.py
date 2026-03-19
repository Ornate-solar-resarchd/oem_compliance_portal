"""User ORM model."""
from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    engineer = "engineer"
    reviewer = "reviewer"
    commercial = "commercial"
    customer = "customer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[UserRole] = mapped_column(PgEnum(UserRole, name="user_role", create_type=False), nullable=False, server_default="engineer")
    organisation: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    keycloak_sub: Mapped[str | None] = mapped_column(Text, unique=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    created_oems: Mapped[list["OEM"]] = relationship("OEM", back_populates="creator", foreign_keys="OEM.created_by")
    created_projects: Mapped[list["Project"]] = relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    customer_projects: Mapped[list["Project"]] = relationship("Project", back_populates="customer_user", foreign_keys="Project.customer_user_id")
