"""
WorkflowService — approval workflow state machine and management.

Handles stage transitions, role-based permission enforcement,
pre-transition validation, and workflow assignment.
"""
from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import func, select, and_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import text as sa_text

from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    SheetLockedError,
    WorkflowTransitionError,
)
from app.models.sheet import (
    ComplianceStatus,
    SheetComplianceResult,
    TechnicalSheet,
    WorkflowStage,
)
from app.models.workflow import ApprovalAction, ApprovalWorkflow, WorkflowStep
from app.services.base import BaseService


# ---------------------------------------------------------------------------
# Role-to-stage permission matrix
# Maps (stage, action) -> set of allowed roles
# ---------------------------------------------------------------------------
ROLE_STAGE_MATRIX: dict[tuple[str, str], set[str]] = {
    # draft -> submit
    ("draft", "submit"):                {"engineer", "admin"},
    # engineering_review -> approve|reject
    ("engineering_review", "approve"):   {"engineer", "reviewer", "admin"},
    ("engineering_review", "reject"):    {"engineer", "reviewer", "admin"},
    # technical_lead -> approve|reject
    ("technical_lead", "approve"):       {"reviewer", "admin"},
    ("technical_lead", "reject"):        {"reviewer", "admin"},
    # management -> approve|reject
    ("management", "approve"):           {"admin"},
    ("management", "reject"):            {"admin"},
    # customer_submission -> approve|reject
    ("customer_submission", "approve"):  {"commercial", "admin"},
    ("customer_submission", "reject"):   {"commercial", "admin"},
    # customer_signoff -> approve|reject
    ("customer_signoff", "approve"):     {"customer", "admin"},
    ("customer_signoff", "reject"):      {"customer", "admin"},
}

# Stages from which reject is allowed (everything except draft and locked)
_REJECTABLE_STAGES: set[str] = {
    "engineering_review",
    "technical_lead",
    "management",
    "customer_submission",
    "customer_signoff",
}

# Minimum compliance score required to submit from draft
_MIN_SUBMIT_SCORE = 0  # configurable threshold


class WorkflowService(BaseService):
    """State machine and management operations for approval workflows."""

    # ── Helpers ─────────────────────────────────────────────────────────

    async def _get_workflow_or_404(self, workflow_id: UUID) -> ApprovalWorkflow:
        """Fetch a workflow by ID or raise NotFoundError."""
        wf = await self.db.get(ApprovalWorkflow, workflow_id)
        if wf is None:
            raise NotFoundError("ApprovalWorkflow", workflow_id)
        return wf

    def _check_role_permission(
        self, stage: str, action: str, role: str
    ) -> None:
        """Verify the actor's role is allowed for this stage+action."""
        # Lock is admin-only from any stage
        if action == "lock":
            if role != "admin":
                raise ForbiddenError(
                    f"Only admin can lock a sheet (your role: {role})"
                )
            return

        # Reject from any rejectable stage
        if action == "reject":
            if stage not in _REJECTABLE_STAGES:
                raise WorkflowTransitionError(
                    current_stage=stage,
                    action=action,
                    reason=f"Cannot reject from stage '{stage}'",
                )
            key = (stage, "reject")
            allowed = ROLE_STAGE_MATRIX.get(key, set())
            if role not in allowed:
                raise ForbiddenError(
                    f"Role '{role}' cannot reject at stage '{stage}'"
                )
            return

        key = (stage, action)
        allowed = ROLE_STAGE_MATRIX.get(key)
        if allowed is None:
            raise WorkflowTransitionError(
                current_stage=stage,
                action=action,
                reason=f"No transition defined for action '{action}' at stage '{stage}'",
            )
        if role not in allowed:
            raise ForbiddenError(
                f"Role '{role}' cannot perform '{action}' at stage '{stage}'"
            )

    async def _pre_transition_validation(
        self, sheet: TechnicalSheet, action: str
    ) -> None:
        """Run pre-transition checks before advancing the workflow.

        - On submit: verify minimum compliance score and no mandatory
          parameters left pending.
        - On lock: same checks as submit (final integrity gate).
        """
        if action not in ("submit", "lock", "approve"):
            return

        # Check mandatory parameters are not pending/fail
        if action in ("submit", "approve"):
            mandatory_check_q = (
                select(func.count())
                .select_from(SheetComplianceResult)
                .join(
                    SheetComplianceResult.standard_parameter,
                )
                .where(
                    and_(
                        SheetComplianceResult.technical_sheet_id == sheet.id,
                        SheetComplianceResult.status.in_([
                            ComplianceStatus.pending,
                            ComplianceStatus.fail,
                        ]),
                    )
                )
            )
            # Import here to avoid circular — StandardParameter already loaded via join
            from app.models.parameter import StandardParameter

            mandatory_pending_q = (
                select(func.count())
                .select_from(SheetComplianceResult)
                .join(StandardParameter, SheetComplianceResult.standard_parameter_id == StandardParameter.id)
                .where(
                    and_(
                        SheetComplianceResult.technical_sheet_id == sheet.id,
                        StandardParameter.is_mandatory.is_(True),
                        SheetComplianceResult.status == ComplianceStatus.pending,
                    )
                )
            )
            mandatory_pending = (await self.db.execute(mandatory_pending_q)).scalar_one()

            if mandatory_pending > 0:
                raise WorkflowTransitionError(
                    current_stage=sheet.stage.value,
                    action=action,
                    reason=(
                        f"{mandatory_pending} mandatory parameter(s) still pending evaluation. "
                        "All mandatory parameters must be evaluated before advancing."
                    ),
                )

        # Check minimum score threshold on submit
        if action == "submit" and sheet.compliance_score is not None:
            if sheet.compliance_score < _MIN_SUBMIT_SCORE:
                raise WorkflowTransitionError(
                    current_stage=sheet.stage.value,
                    action=action,
                    reason=(
                        f"Compliance score ({sheet.compliance_score}%) is below "
                        f"the minimum threshold ({_MIN_SUBMIT_SCORE}%)"
                    ),
                )

    # ── List ────────────────────────────────────────────────────────────

    async def list_workflows(
        self,
        page: int = 1,
        per_page: int = 20,
        stage: str | None = None,
        assigned_to: UUID | None = None,
    ) -> dict[str, Any]:
        """Return a paginated list of workflows with sheet and project joins."""
        query = (
            select(ApprovalWorkflow)
            .options(
                joinedload(ApprovalWorkflow.technical_sheet)
                .joinedload(TechnicalSheet.project),
                joinedload(ApprovalWorkflow.assignee),
            )
            .order_by(ApprovalWorkflow.updated_at.desc())
        )

        if stage is not None:
            query = query.where(ApprovalWorkflow.current_stage == stage)
        if assigned_to is not None:
            query = query.where(ApprovalWorkflow.assigned_to == assigned_to)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        paginated = self._paginate(query, page, per_page)
        rows = (await self.db.execute(paginated)).scalars().unique().all()

        return {
            "items": rows,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": max(1, -(-total // per_page)),
        }

    # ── Get single ──────────────────────────────────────────────────────

    async def get_workflow(self, workflow_id: UUID) -> dict[str, Any]:
        """Return a workflow with all steps (audit trail)."""
        query = (
            select(ApprovalWorkflow)
            .options(
                joinedload(ApprovalWorkflow.technical_sheet)
                .joinedload(TechnicalSheet.project),
                joinedload(ApprovalWorkflow.assignee),
                selectinload(ApprovalWorkflow.steps)
                .joinedload(WorkflowStep.actor),
            )
            .where(ApprovalWorkflow.id == workflow_id)
        )
        wf = (await self.db.execute(query)).scalars().unique().first()
        if wf is None:
            raise NotFoundError("ApprovalWorkflow", workflow_id)

        return {
            "workflow": wf,
            "steps": wf.steps,
        }

    # ── Advance (State Machine) ─────────────────────────────────────────

    async def advance(
        self,
        workflow_id: UUID,
        action: str,
        actor_id: UUID,
        comment: str | None = None,
    ) -> ApprovalWorkflow:
        """Execute a workflow state transition.

        Steps:
        1. Role-based permission check using ROLE_STAGE_MATRIX
        2. Pre-transition validation (mandatory params, score thresholds)
        3. Call stored procedure: CALL advance_workflow(...)
        4. Post-transition: create version snapshot
        """
        # Load workflow with sheet
        query = (
            select(ApprovalWorkflow)
            .options(joinedload(ApprovalWorkflow.technical_sheet))
            .where(ApprovalWorkflow.id == workflow_id)
        )
        wf = (await self.db.execute(query)).scalars().unique().first()
        if wf is None:
            raise NotFoundError("ApprovalWorkflow", workflow_id)

        sheet = wf.technical_sheet
        if sheet.is_locked:
            raise SheetLockedError(sheet.sheet_number or str(sheet.id))

        current_stage = wf.current_stage.value

        # 1. Role-based permission check
        actor_role = self.actor.get("role", "")
        self._check_role_permission(current_stage, action, actor_role)

        # 2. Pre-transition validation
        await self._pre_transition_validation(sheet, action)

        # 3. Call stored procedure
        await self.db.execute(
            sa_text(
                "CALL advance_workflow(:wf_id, :action::approval_action, :actor_id, :comment)"
            ),
            {
                "wf_id": workflow_id,
                "action": action,
                "actor_id": actor_id,
                "comment": comment,
            },
        )
        await self.db.flush()

        # 4. Post-transition: create version snapshot
        await self.db.execute(
            sa_text("CALL create_sheet_version(:sheet_id, :actor_id)"),
            {"sheet_id": sheet.id, "actor_id": actor_id},
        )
        await self.db.flush()

        # Refresh to pick up new stage from the stored procedure
        await self.db.refresh(wf)
        await self.db.refresh(sheet)

        return wf

    # ── Get Pending for User ────────────────────────────────────────────

    async def get_pending_for_user(
        self,
        user_id: UUID,
        role: str,
    ) -> list[ApprovalWorkflow]:
        """Return workflows that need action from a user based on stage+role.

        Looks at the ROLE_STAGE_MATRIX to determine which stages the role
        can act on, then returns workflows at those stages.
        """
        # Determine which stages this role can act on
        actionable_stages: set[str] = set()
        for (stage, act), roles in ROLE_STAGE_MATRIX.items():
            if role in roles:
                actionable_stages.add(stage)

        if not actionable_stages:
            return []

        # Convert to WorkflowStage enum values
        stage_filters = []
        for s in actionable_stages:
            try:
                stage_filters.append(WorkflowStage(s))
            except ValueError:
                continue

        if not stage_filters:
            return []

        query = (
            select(ApprovalWorkflow)
            .options(
                joinedload(ApprovalWorkflow.technical_sheet)
                .joinedload(TechnicalSheet.project),
                joinedload(ApprovalWorkflow.assignee),
            )
            .where(ApprovalWorkflow.current_stage.in_(stage_filters))
            .order_by(ApprovalWorkflow.updated_at.desc())
        )

        # Optionally filter by assignment
        # Include both assigned-to-user and unassigned workflows
        rows = (await self.db.execute(query)).scalars().unique().all()
        return list(rows)

    # ── Assign Workflow ─────────────────────────────────────────────────

    async def assign_workflow(
        self,
        workflow_id: UUID,
        assigned_to: UUID,
        actor_id: UUID,
    ) -> ApprovalWorkflow:
        """Change the assignee of a workflow."""
        wf = await self._get_workflow_or_404(workflow_id)

        # Cannot assign locked workflows
        sheet = await self.db.get(TechnicalSheet, wf.technical_sheet_id)
        if sheet and sheet.is_locked:
            raise SheetLockedError(sheet.sheet_number or str(sheet.id))

        wf.assigned_to = assigned_to
        wf.updated_at = self._now()
        await self.db.flush()

        return wf

    # ── Set Due Date ────────────────────────────────────────────────────

    async def set_due_date(
        self,
        workflow_id: UUID,
        due_date: date,
        actor_id: UUID,
    ) -> ApprovalWorkflow:
        """Set or update the due date on a workflow."""
        wf = await self._get_workflow_or_404(workflow_id)

        # Cannot modify locked workflows
        sheet = await self.db.get(TechnicalSheet, wf.technical_sheet_id)
        if sheet and sheet.is_locked:
            raise SheetLockedError(sheet.sheet_number or str(sheet.id))

        wf.due_date = due_date
        wf.updated_at = self._now()
        await self.db.flush()

        return wf
