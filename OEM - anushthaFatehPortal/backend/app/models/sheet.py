"""TechnicalSheet, SheetComplianceResult, and SheetVersion ORM models."""
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WorkflowStage(str, enum.Enum):
    draft = "draft"
    engineering_review = "engineering_review"
    technical_lead = "technical_lead"
    management = "management"
    customer_submission = "customer_submission"
    customer_signoff = "customer_signoff"
    locked = "locked"


class ComplianceStatus(str, enum.Enum):
    pass_ = "pass"      # 'pass' is Python reserved
    fail = "fail"
    waived = "waived"
    pending = "pending"


class TechnicalSheet(Base):
    __tablename__ = "technical_sheets"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    sheet_number: Mapped[str | None] = mapped_column(Text, unique=True)
    project_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False)
    component_model_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("component_models.id", ondelete="RESTRICT"), nullable=False)
    compliance_template_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("compliance_templates.id", ondelete="SET NULL"))
    stage: Mapped[WorkflowStage] = mapped_column(PgEnum(WorkflowStage, name="workflow_stage", create_type=False), nullable=False, server_default="draft")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    compliance_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    pass_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    waived_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    pending_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    lock_hash: Mapped[str | None] = mapped_column(Text)
    locked_at: Mapped[datetime | None] = mapped_column()
    locked_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="technical_sheets")
    component_model: Mapped["ComponentModel"] = relationship("ComponentModel", back_populates="technical_sheets")
    compliance_template: Mapped["ComplianceTemplate | None"] = relationship("ComplianceTemplate")
    compliance_results: Mapped[list["SheetComplianceResult"]] = relationship("SheetComplianceResult", back_populates="technical_sheet", cascade="all, delete-orphan")
    versions: Mapped[list["SheetVersion"]] = relationship("SheetVersion", back_populates="technical_sheet", cascade="all, delete-orphan")
    workflow: Mapped["ApprovalWorkflow | None"] = relationship("ApprovalWorkflow", back_populates="technical_sheet", uselist=False)
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="technical_sheet")


class SheetComplianceResult(Base):
    __tablename__ = "sheet_compliance_results"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    technical_sheet_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("technical_sheets.id", ondelete="CASCADE"), nullable=False)
    standard_parameter_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("standard_parameters.id", ondelete="RESTRICT"), nullable=False)
    oem_value: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ComplianceStatus] = mapped_column(
        PgEnum(ComplianceStatus, name="compliance_status", create_type=False,
               values_callable=lambda e: [v.value if v.name != "pass_" else "pass" for v in e]),
        nullable=False, server_default="pending",
    )
    waive_reason: Mapped[str | None] = mapped_column(Text)
    waived_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    waived_at: Mapped[datetime | None] = mapped_column()
    evaluated_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    technical_sheet: Mapped["TechnicalSheet"] = relationship("TechnicalSheet", back_populates="compliance_results")
    standard_parameter: Mapped["StandardParameter"] = relationship("StandardParameter")


class SheetVersion(Base):
    __tablename__ = "sheet_versions"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    technical_sheet_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("technical_sheets.id", ondelete="CASCADE"), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    stage: Mapped[WorkflowStage] = mapped_column(PgEnum(WorkflowStage, name="workflow_stage", create_type=False), nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    technical_sheet: Mapped["TechnicalSheet"] = relationship("TechnicalSheet", back_populates="versions")
