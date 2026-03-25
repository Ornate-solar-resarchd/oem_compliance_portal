"""Project ORM model."""
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectType(str, enum.Enum):
    utility = "utility"
    ci = "ci"
    btm = "btm"
    hybrid = "hybrid"


class ProjectStatus(str, enum.Enum):
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name: Mapped[str] = mapped_column(Text, nullable=False)
    client_name: Mapped[str] = mapped_column(Text, nullable=False)
    project_type: Mapped[ProjectType] = mapped_column(PgEnum(ProjectType, name="project_type", create_type=False), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(PgEnum(ProjectStatus, name="project_status", create_type=False), nullable=False, server_default="active")
    capacity_kwh: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    power_kw: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    location: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str | None] = mapped_column(Text)
    customer_user_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    customer_user: Mapped["User | None"] = relationship("User", back_populates="customer_projects", foreign_keys=[customer_user_id])
    creator: Mapped["User | None"] = relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    technical_sheets: Mapped[list["TechnicalSheet"]] = relationship("TechnicalSheet", back_populates="project")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="project")
