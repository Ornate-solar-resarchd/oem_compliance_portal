"""ApprovalWorkflow and WorkflowStep ORM models."""
from __future__ import annotations

import enum
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.sheet import WorkflowStage


class ApprovalAction(str, enum.Enum):
    submit = "submit"
    approve = "approve"
    reject = "reject"
    waive = "waive"
    lock = "lock"


class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    workflow_number: Mapped[str | None] = mapped_column(Text, unique=True)
    technical_sheet_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("technical_sheets.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_stage: Mapped[WorkflowStage] = mapped_column(PgEnum(WorkflowStage, name="workflow_stage", create_type=False), nullable=False, server_default="draft")
    assigned_to: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    due_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    technical_sheet: Mapped["TechnicalSheet"] = relationship("TechnicalSheet", back_populates="workflow")
    assignee: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_to])
    steps: Mapped[list["WorkflowStep"]] = relationship("WorkflowStep", back_populates="workflow", order_by="WorkflowStep.created_at")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    workflow_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("approval_workflows.id", ondelete="CASCADE"), nullable=False)
    stage: Mapped[WorkflowStage] = mapped_column(PgEnum(WorkflowStage, name="workflow_stage", create_type=False), nullable=False)
    action: Mapped[ApprovalAction] = mapped_column(PgEnum(ApprovalAction, name="approval_action", create_type=False), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    signature_hash: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    workflow: Mapped["ApprovalWorkflow"] = relationship("ApprovalWorkflow", back_populates="steps")
    actor: Mapped["User"] = relationship("User", foreign_keys=[actor_id])
