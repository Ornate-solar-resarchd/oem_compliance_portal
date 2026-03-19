"""OEM, ComponentType, and ComponentModel ORM models."""
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ComponentCategory(str, enum.Enum):
    battery_cell = "battery_cell"
    battery_module = "battery_module"
    battery_pack = "battery_pack"
    bms = "bms"
    pcs = "pcs"
    thermal_management = "thermal_management"
    fire_suppression = "fire_suppression"
    enclosure = "enclosure"
    switchgear = "switchgear"
    communication = "communication"


class OEM(Base):
    __tablename__ = "oems"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    country_of_origin: Mapped[str] = mapped_column(Text, nullable=False)
    website: Mapped[str | None] = mapped_column(Text)
    contact_email: Mapped[str | None] = mapped_column(Text)
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    creator: Mapped["User | None"] = relationship("User", back_populates="created_oems", foreign_keys=[created_by])
    component_models: Mapped[list["ComponentModel"]] = relationship("ComponentModel", back_populates="oem")


class ComponentType(Base):
    __tablename__ = "component_types"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    category: Mapped[ComponentCategory] = mapped_column(PgEnum(ComponentCategory, name="component_category", create_type=False), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    component_models: Mapped[list["ComponentModel"]] = relationship("ComponentModel", back_populates="component_type")
    standard_parameters: Mapped[list["StandardParameter"]] = relationship("StandardParameter", back_populates="component_type")
    compliance_templates: Mapped[list["ComplianceTemplate"]] = relationship("ComplianceTemplate", back_populates="component_type")


class ComponentModel(Base):
    __tablename__ = "component_models"
    __table_args__ = (
        {"comment": "UNIQUE(oem_id, model_name)"},
    )

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    oem_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("oems.id", ondelete="RESTRICT"), nullable=False)
    component_type_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("component_types.id", ondelete="RESTRICT"), nullable=False)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    datasheet_url: Mapped[str | None] = mapped_column(Text)
    datasheet_minio_key: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    fill_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    compliance_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    created_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    oem: Mapped["OEM"] = relationship("OEM", back_populates="component_models")
    component_type: Mapped["ComponentType"] = relationship("ComponentType", back_populates="component_models")
    parameter_values: Mapped[list["ParameterValue"]] = relationship("ParameterValue", back_populates="component_model", cascade="all, delete-orphan")
    technical_sheets: Mapped[list["TechnicalSheet"]] = relationship("TechnicalSheet", back_populates="component_model")
