"""ComplianceTemplate and ComplianceTemplateParameter ORM models."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ComplianceTemplate(Base):
    __tablename__ = "compliance_templates"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    component_type_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("component_types.id", ondelete="RESTRICT"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    component_type: Mapped["ComponentType"] = relationship("ComponentType", back_populates="compliance_templates")
    template_parameters: Mapped[list["ComplianceTemplateParameter"]] = relationship("ComplianceTemplateParameter", back_populates="compliance_template", cascade="all, delete-orphan")


class ComplianceTemplateParameter(Base):
    __tablename__ = "compliance_template_parameters"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    compliance_template_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("compliance_templates.id", ondelete="CASCADE"), nullable=False)
    standard_parameter_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("standard_parameters.id", ondelete="RESTRICT"), nullable=False)
    is_mandatory_override: Mapped[bool | None] = mapped_column(Boolean)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    # Relationships
    compliance_template: Mapped["ComplianceTemplate"] = relationship("ComplianceTemplate", back_populates="template_parameters")
    standard_parameter: Mapped["StandardParameter"] = relationship("StandardParameter", back_populates="template_parameters")
