"""StandardParameter and ParameterValue ORM models."""
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import ARRAY, Boolean, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ParameterDataType(str, enum.Enum):
    numeric = "numeric"
    range = "range"
    boolean = "boolean"
    enum = "enum"
    text = "text"


class ExtractionSource(str, enum.Enum):
    ai = "ai"
    manual = "manual"
    import_ = "import"  # 'import' is a Python reserved word


class StandardParameter(Base):
    __tablename__ = "standard_parameters"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    component_type_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("component_types.id", ondelete="RESTRICT"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    section: Mapped[str] = mapped_column(Text, nullable=False)
    data_type: Mapped[ParameterDataType] = mapped_column(PgEnum(ParameterDataType, name="parameter_data_type", create_type=False), nullable=False)
    unit: Mapped[str | None] = mapped_column(Text)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    acceptance_min: Mapped[Decimal | None] = mapped_column(Numeric)
    acceptance_max: Mapped[Decimal | None] = mapped_column(Numeric)
    acceptance_enum: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    regulatory_ref: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    component_type: Mapped["ComponentType"] = relationship("ComponentType", back_populates="standard_parameters")
    parameter_values: Mapped[list["ParameterValue"]] = relationship("ParameterValue", back_populates="standard_parameter")
    template_parameters: Mapped[list["ComplianceTemplateParameter"]] = relationship("ComplianceTemplateParameter", back_populates="standard_parameter")


class ParameterValue(Base):
    __tablename__ = "parameter_values"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    component_model_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("component_models.id", ondelete="CASCADE"), nullable=False)
    standard_parameter_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("standard_parameters.id", ondelete="RESTRICT"), nullable=False)
    value_raw: Mapped[str | None] = mapped_column(Text)
    value_jsonb: Mapped[dict | None] = mapped_column(JSONB)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    source: Mapped[ExtractionSource] = mapped_column(PgEnum(ExtractionSource, name="extraction_source", create_type=False, values_callable=lambda e: [v.value if v.name != "import_" else "import" for v in e]), nullable=False, server_default="manual")
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    extracted_at: Mapped[datetime | None] = mapped_column()
    verified_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    verified_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    component_model: Mapped["ComponentModel"] = relationship("ComponentModel", back_populates="parameter_values")
    standard_parameter: Mapped["StandardParameter"] = relationship("StandardParameter", back_populates="parameter_values")
