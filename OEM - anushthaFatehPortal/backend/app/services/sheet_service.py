"""
SheetService — business logic for Technical Compliance Sheets.

Handles sheet CRUD, compliance evaluation, version snapshots,
and parameter waiver management.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from sqlalchemy import func, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import text as sa_text

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    SheetLockedError,
    ValidationError,
    WorkflowTransitionError,
)
from app.models.oem import ComponentModel
from app.models.parameter import ParameterValue, StandardParameter
from app.models.project import Project, ProjectStatus
from app.models.sheet import (
    ComplianceStatus,
    SheetComplianceResult,
    SheetVersion,
    TechnicalSheet,
    WorkflowStage,
)
from app.models.template import ComplianceTemplate, ComplianceTemplateParameter
from app.models.workflow import ApprovalWorkflow
from app.services.base import BaseService


class SheetService(BaseService):
    """Domain operations for technical compliance sheets."""

    # ── Compliance Evaluation Engine ────────────────────────────────────

    @staticmethod
    def _evaluate(
        data_type: str,
        oem_value: str | None,
        acceptance_min: Decimal | None,
        acceptance_max: Decimal | None,
        acceptance_enum: list[str] | None,
        value_jsonb: dict | None = None,
    ) -> ComplianceStatus:
        """Evaluate a single parameter value against its acceptance criteria.

        Returns the compliance status: pass, fail, or pending.
        """
        if oem_value is None or str(oem_value).strip() == "":
            return ComplianceStatus.pending

        try:
            if data_type == "numeric":
                numeric_val = Decimal(str(oem_value))
                if acceptance_min is not None and numeric_val < acceptance_min:
                    return ComplianceStatus.fail
                if acceptance_max is not None and numeric_val > acceptance_max:
                    return ComplianceStatus.fail
                return ComplianceStatus.pass_

            elif data_type == "range":
                # oem_value might be raw text; prefer value_jsonb if available
                range_data = value_jsonb or {}
                range_min = range_data.get("min")
                range_max = range_data.get("max")
                if range_min is None and range_max is None:
                    # Try parsing oem_value as a single numeric
                    try:
                        numeric_val = Decimal(str(oem_value))
                        if acceptance_min is not None and numeric_val < acceptance_min:
                            return ComplianceStatus.fail
                        if acceptance_max is not None and numeric_val > acceptance_max:
                            return ComplianceStatus.fail
                        return ComplianceStatus.pass_
                    except (InvalidOperation, ValueError):
                        return ComplianceStatus.pending
                # Check that the range min/max fall within acceptance bounds
                try:
                    r_min = Decimal(str(range_min)) if range_min is not None else None
                    r_max = Decimal(str(range_max)) if range_max is not None else None
                except (InvalidOperation, ValueError):
                    return ComplianceStatus.pending
                if acceptance_min is not None and r_min is not None and r_min < acceptance_min:
                    return ComplianceStatus.fail
                if acceptance_max is not None and r_max is not None and r_max > acceptance_max:
                    return ComplianceStatus.fail
                return ComplianceStatus.pass_

            elif data_type == "boolean":
                normalised = str(oem_value).strip().lower()
                if acceptance_enum:
                    return (
                        ComplianceStatus.pass_
                        if normalised in [v.lower() for v in acceptance_enum]
                        else ComplianceStatus.fail
                    )
                # No acceptance criteria -> pass if truthy
                return (
                    ComplianceStatus.pass_
                    if normalised in ("true", "yes", "1")
                    else ComplianceStatus.fail
                )

            elif data_type == "enum":
                if acceptance_enum:
                    return (
                        ComplianceStatus.pass_
                        if str(oem_value).strip() in acceptance_enum
                        else ComplianceStatus.fail
                    )
                return ComplianceStatus.pass_

            elif data_type == "text":
                if acceptance_enum:
                    return (
                        ComplianceStatus.pass_
                        if str(oem_value).strip() in acceptance_enum
                        else ComplianceStatus.fail
                    )
                # No acceptance criteria for text -> pass
                return ComplianceStatus.pass_

            else:
                return ComplianceStatus.pending

        except (InvalidOperation, ValueError, TypeError):
            return ComplianceStatus.pending

    # ── Helpers ─────────────────────────────────────────────────────────

    async def _get_sheet_or_404(self, sheet_id: UUID) -> TechnicalSheet:
        """Fetch a sheet by ID or raise NotFoundError."""
        sheet = await self.db.get(TechnicalSheet, sheet_id)
        if sheet is None:
            raise NotFoundError("TechnicalSheet", sheet_id)
        return sheet

    def _assert_not_locked(self, sheet: TechnicalSheet) -> None:
        """Raise SheetLockedError if the sheet is locked."""
        if sheet.is_locked:
            raise SheetLockedError(sheet.sheet_number or str(sheet.id))

    # ── List ────────────────────────────────────────────────────────────

    async def list_sheets(
        self,
        page: int = 1,
        per_page: int = 20,
        project_id: UUID | None = None,
        stage: str | None = None,
        component_model_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Return a paginated list of technical sheets with project and model joins."""
        query = (
            select(TechnicalSheet)
            .options(
                joinedload(TechnicalSheet.project),
                joinedload(TechnicalSheet.component_model),
                joinedload(TechnicalSheet.workflow),
            )
            .order_by(TechnicalSheet.created_at.desc())
        )

        if project_id is not None:
            query = query.where(TechnicalSheet.project_id == project_id)
        if stage is not None:
            query = query.where(TechnicalSheet.stage == stage)
        if component_model_id is not None:
            query = query.where(TechnicalSheet.component_model_id == component_model_id)

        # Total count before pagination
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

    async def get_sheet(self, sheet_id: UUID) -> dict[str, Any]:
        """Return full sheet detail with compliance results grouped by section
        and a version count."""
        query = (
            select(TechnicalSheet)
            .options(
                joinedload(TechnicalSheet.project),
                joinedload(TechnicalSheet.component_model),
                joinedload(TechnicalSheet.workflow),
                selectinload(TechnicalSheet.compliance_results)
                .joinedload(SheetComplianceResult.standard_parameter),
            )
            .where(TechnicalSheet.id == sheet_id)
        )
        result = (await self.db.execute(query)).scalars().unique().first()
        if result is None:
            raise NotFoundError("TechnicalSheet", sheet_id)

        # Group compliance results by section
        grouped: dict[str, list[SheetComplianceResult]] = defaultdict(list)
        for cr in result.compliance_results:
            section = cr.standard_parameter.section if cr.standard_parameter else "Other"
            grouped[section].append(cr)

        # Version count
        version_count_q = select(func.count()).where(
            SheetVersion.technical_sheet_id == sheet_id
        )
        version_count = (await self.db.execute(version_count_q)).scalar_one()

        return {
            "sheet": result,
            "compliance_by_section": dict(grouped),
            "version_count": version_count,
        }

    # ── Create ──────────────────────────────────────────────────────────

    async def create_sheet(
        self,
        project_id: UUID,
        component_model_id: UUID,
        compliance_template_id: UUID | None,
        actor_id: UUID,
    ) -> TechnicalSheet:
        """Create a new technical sheet with compliance evaluation.

        Steps:
        1. Validate project exists and is active
        2. Validate component model exists
        3. INSERT technical_sheet (trigger auto-assigns sheet_number)
        4. Determine parameters: from template or all standard_parameters for
           the component type
        5. For each param, look up model's parameter_values, run compliance
           evaluation
        6. INSERT sheet_compliance_results
        7. CREATE approval_workflow row
        8. Return created sheet
        """
        # 1. Validate project
        project = await self.db.get(Project, project_id)
        if project is None:
            raise NotFoundError("Project", project_id)
        if project.status != ProjectStatus.active:
            raise ValidationError(
                "project_id",
                f"Project '{project.name}' is not active (status: {project.status.value})",
            )

        # 2. Validate component model
        model = await self.db.get(ComponentModel, component_model_id)
        if model is None:
            raise NotFoundError("ComponentModel", component_model_id)

        # 3. INSERT technical_sheet
        sheet = TechnicalSheet(
            project_id=project_id,
            component_model_id=component_model_id,
            compliance_template_id=compliance_template_id,
            created_by=actor_id,
        )
        self.db.add(sheet)
        await self.db.flush()  # sheet.id and sheet_number now populated

        # 4. Determine which parameters to evaluate
        if compliance_template_id:
            template = await self.db.get(ComplianceTemplate, compliance_template_id)
            if template is None:
                raise NotFoundError("ComplianceTemplate", compliance_template_id)

            # Fetch template parameters with their standard_parameter
            tp_query = (
                select(ComplianceTemplateParameter)
                .options(joinedload(ComplianceTemplateParameter.standard_parameter))
                .where(
                    ComplianceTemplateParameter.compliance_template_id
                    == compliance_template_id
                )
                .order_by(ComplianceTemplateParameter.sort_order)
            )
            template_params = (
                (await self.db.execute(tp_query)).scalars().unique().all()
            )
            std_params = [tp.standard_parameter for tp in template_params]
        else:
            # All standard parameters for the component type
            sp_query = (
                select(StandardParameter)
                .where(StandardParameter.component_type_id == model.component_type_id)
                .order_by(StandardParameter.sort_order)
            )
            std_params = (await self.db.execute(sp_query)).scalars().all()

        # 5. Look up model parameter_values (keyed by standard_parameter_id)
        pv_query = select(ParameterValue).where(
            ParameterValue.component_model_id == component_model_id
        )
        pv_rows = (await self.db.execute(pv_query)).scalars().all()
        pv_map: dict[UUID, ParameterValue] = {
            pv.standard_parameter_id: pv for pv in pv_rows
        }

        # 6. Evaluate and INSERT sheet_compliance_results
        for sp in std_params:
            pv = pv_map.get(sp.id)
            oem_value = pv.value_raw if pv else None
            value_jsonb = pv.value_jsonb if pv else None

            status = self._evaluate(
                data_type=sp.data_type.value,
                oem_value=oem_value,
                acceptance_min=sp.acceptance_min,
                acceptance_max=sp.acceptance_max,
                acceptance_enum=sp.acceptance_enum,
                value_jsonb=value_jsonb,
            )

            result = SheetComplianceResult(
                technical_sheet_id=sheet.id,
                standard_parameter_id=sp.id,
                oem_value=oem_value,
                status=status,
                evaluated_at=self._now() if status != ComplianceStatus.pending else None,
            )
            self.db.add(result)

        await self.db.flush()  # trigger recomputes score on sheet

        # 7. Create approval workflow
        workflow = ApprovalWorkflow(
            technical_sheet_id=sheet.id,
        )
        self.db.add(workflow)
        await self.db.flush()

        # Refresh sheet to pick up computed scores
        await self.db.refresh(sheet)
        return sheet

    # ── Update Compliance Results (bulk) ────────────────────────────────

    async def update_compliance_results(
        self,
        sheet_id: UUID,
        results: list[dict[str, Any]],
        actor_id: UUID,
    ) -> TechnicalSheet:
        """Bulk update oem_values on compliance results and re-evaluate.

        Each item in *results* should have:
          - result_id (UUID) or standard_parameter_id (UUID)
          - oem_value (str)
        """
        sheet = await self._get_sheet_or_404(sheet_id)
        self._assert_not_locked(sheet)

        if sheet.stage != WorkflowStage.draft:
            raise WorkflowTransitionError(
                current_stage=sheet.stage.value,
                action="update_compliance",
                reason="Compliance results can only be updated in draft stage",
            )

        # Load existing compliance results with parameter info
        cr_query = (
            select(SheetComplianceResult)
            .options(joinedload(SheetComplianceResult.standard_parameter))
            .where(SheetComplianceResult.technical_sheet_id == sheet_id)
        )
        existing = (await self.db.execute(cr_query)).scalars().unique().all()

        # Index by both result id and standard_parameter_id
        by_id: dict[UUID, SheetComplianceResult] = {cr.id: cr for cr in existing}
        by_param: dict[UUID, SheetComplianceResult] = {
            cr.standard_parameter_id: cr for cr in existing
        }

        # Also load model parameter_values for value_jsonb
        pv_query = select(ParameterValue).where(
            ParameterValue.component_model_id == sheet.component_model_id
        )
        pv_rows = (await self.db.execute(pv_query)).scalars().all()
        pv_map: dict[UUID, ParameterValue] = {
            pv.standard_parameter_id: pv for pv in pv_rows
        }

        for item in results:
            # Resolve the compliance result row
            cr: SheetComplianceResult | None = None
            if "result_id" in item:
                cr = by_id.get(item["result_id"])
            if cr is None and "standard_parameter_id" in item:
                cr = by_param.get(item["standard_parameter_id"])
            if cr is None:
                continue  # skip unknown entries

            # Skip waived parameters
            if cr.status == ComplianceStatus.waived:
                continue

            new_value = item.get("oem_value")
            cr.oem_value = new_value

            sp = cr.standard_parameter
            pv = pv_map.get(sp.id)
            value_jsonb = pv.value_jsonb if pv else None

            cr.status = self._evaluate(
                data_type=sp.data_type.value,
                oem_value=new_value,
                acceptance_min=sp.acceptance_min,
                acceptance_max=sp.acceptance_max,
                acceptance_enum=sp.acceptance_enum,
                value_jsonb=value_jsonb,
            )
            cr.evaluated_at = self._now()
            cr.updated_at = self._now()

        await self.db.flush()  # trigger recomputes score
        await self.db.refresh(sheet)
        return sheet

    # ── Waive Parameter ─────────────────────────────────────────────────

    async def waive_parameter(
        self,
        sheet_id: UUID,
        param_id: UUID,
        reason: str,
        actor_id: UUID,
    ) -> SheetComplianceResult:
        """Set a compliance result to waived with a reason."""
        sheet = await self._get_sheet_or_404(sheet_id)
        self._assert_not_locked(sheet)

        cr_query = select(SheetComplianceResult).where(
            and_(
                SheetComplianceResult.technical_sheet_id == sheet_id,
                SheetComplianceResult.standard_parameter_id == param_id,
            )
        )
        cr = (await self.db.execute(cr_query)).scalars().first()
        if cr is None:
            raise NotFoundError("SheetComplianceResult", param_id)

        cr.status = ComplianceStatus.waived
        cr.waive_reason = reason
        cr.waived_by = actor_id
        cr.waived_at = self._now()
        cr.updated_at = self._now()

        await self.db.flush()
        return cr

    # ── Compliance Score ────────────────────────────────────────────────

    async def get_compliance_score(self, sheet_id: UUID) -> dict[str, Any]:
        """Read denormalized compliance counts from the technical_sheets row."""
        sheet = await self._get_sheet_or_404(sheet_id)
        return {
            "sheet_id": sheet.id,
            "compliance_score": sheet.compliance_score,
            "pass_count": sheet.pass_count,
            "fail_count": sheet.fail_count,
            "waived_count": sheet.waived_count,
            "pending_count": sheet.pending_count,
            "total": sheet.pass_count + sheet.fail_count + sheet.waived_count + sheet.pending_count,
        }

    # ── Versions ────────────────────────────────────────────────────────

    async def get_versions(self, sheet_id: UUID) -> list[SheetVersion]:
        """List all version snapshots for a sheet."""
        await self._get_sheet_or_404(sheet_id)  # ensure sheet exists

        query = (
            select(SheetVersion)
            .where(SheetVersion.technical_sheet_id == sheet_id)
            .order_by(SheetVersion.created_at.desc())
        )
        return list((await self.db.execute(query)).scalars().all())

    async def create_version_snapshot(
        self,
        sheet_id: UUID,
        actor_id: UUID,
    ) -> None:
        """Call the create_sheet_version stored procedure to capture
        an immutable snapshot of the sheet's current state."""
        await self._get_sheet_or_404(sheet_id)

        await self.db.execute(
            sa_text("CALL create_sheet_version(:sheet_id, :actor_id)"),
            {"sheet_id": sheet_id, "actor_id": actor_id},
        )
        await self.db.flush()

    # ── Refresh Compliance ──────────────────────────────────────────────

    async def refresh_compliance(
        self,
        sheet_id: UUID,
        actor_id: UUID,
    ) -> TechnicalSheet:
        """Re-evaluate all compliance results for a sheet.

        Only permitted when the sheet is in draft stage. Pulls fresh
        parameter_values from the component model and re-runs evaluation.
        """
        sheet = await self._get_sheet_or_404(sheet_id)
        self._assert_not_locked(sheet)

        if sheet.stage != WorkflowStage.draft:
            raise WorkflowTransitionError(
                current_stage=sheet.stage.value,
                action="refresh_compliance",
                reason="Compliance can only be refreshed in draft stage",
            )

        # Load compliance results with parameters
        cr_query = (
            select(SheetComplianceResult)
            .options(joinedload(SheetComplianceResult.standard_parameter))
            .where(SheetComplianceResult.technical_sheet_id == sheet_id)
        )
        results = (await self.db.execute(cr_query)).scalars().unique().all()

        # Load fresh parameter_values from component model
        pv_query = select(ParameterValue).where(
            ParameterValue.component_model_id == sheet.component_model_id
        )
        pv_rows = (await self.db.execute(pv_query)).scalars().all()
        pv_map: dict[UUID, ParameterValue] = {
            pv.standard_parameter_id: pv for pv in pv_rows
        }

        now = self._now()
        for cr in results:
            # Preserve waived status
            if cr.status == ComplianceStatus.waived:
                continue

            sp = cr.standard_parameter
            pv = pv_map.get(sp.id)
            oem_value = pv.value_raw if pv else cr.oem_value
            value_jsonb = pv.value_jsonb if pv else None

            # Update the oem_value from fresh data if available
            if pv and pv.value_raw is not None:
                cr.oem_value = pv.value_raw

            cr.status = self._evaluate(
                data_type=sp.data_type.value,
                oem_value=oem_value,
                acceptance_min=sp.acceptance_min,
                acceptance_max=sp.acceptance_max,
                acceptance_enum=sp.acceptance_enum,
                value_jsonb=value_jsonb,
            )
            cr.evaluated_at = now
            cr.updated_at = now

        await self.db.flush()  # trigger recomputes score
        await self.db.refresh(sheet)
        return sheet
