"""
TemplateService — business logic for compliance templates and their parameters.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.parameter import StandardParameter
from app.models.template import ComplianceTemplate, ComplianceTemplateParameter
from app.services.base import BaseService


class TemplateService(BaseService):
    """Manages compliance template CRUD, parameter linking, and cloning."""

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------
    async def list_templates(
        self,
        page: int = 1,
        per_page: int = 20,
        component_type_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        """Return a paginated list of compliance templates."""
        query = select(ComplianceTemplate)

        if component_type_id is not None:
            query = query.where(
                ComplianceTemplate.component_type_id == component_type_id
            )
        if is_active is not None:
            query = query.where(ComplianceTemplate.is_active == is_active)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Paginate & fetch
        query = query.order_by(ComplianceTemplate.created_at.desc())
        query = self._paginate(query, page, per_page)
        result = await self.db.execute(query)
        templates = result.scalars().all()

        return {
            "items": templates,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    # ------------------------------------------------------------------
    # Detail
    # ------------------------------------------------------------------
    async def get_template(self, template_id: UUID) -> ComplianceTemplate:
        """Return a template with all parameters joined with standard_parameter info."""
        query = (
            select(ComplianceTemplate)
            .options(
                selectinload(ComplianceTemplate.template_parameters).selectinload(
                    ComplianceTemplateParameter.standard_parameter
                )
            )
            .where(ComplianceTemplate.id == template_id)
        )
        result = await self.db.execute(query)
        template = result.scalar_one_or_none()
        if template is None:
            raise NotFoundError("ComplianceTemplate", template_id)
        return template

    # ------------------------------------------------------------------
    # Create (template + parameters in one transaction)
    # ------------------------------------------------------------------
    async def create_template(
        self, data: dict[str, Any], actor_id: UUID
    ) -> ComplianceTemplate:
        """Create a template and optionally attach parameters atomically."""

        # Check for duplicate name
        await self._assert_name_unique(data["name"])

        template = ComplianceTemplate(
            name=data["name"],
            component_type_id=data["component_type_id"],
            description=data.get("description"),
            is_active=data.get("is_active", True),
            created_by=actor_id,
        )
        self.db.add(template)
        await self.db.flush()

        # Attach parameters if supplied
        parameters: list[dict[str, Any]] = data.get("parameters", [])
        for idx, param in enumerate(parameters):
            tp = ComplianceTemplateParameter(
                compliance_template_id=template.id,
                standard_parameter_id=param["standard_parameter_id"],
                is_mandatory_override=param.get("is_mandatory_override"),
                sort_order=param.get("sort_order", idx),
            )
            self.db.add(tp)

        await self.db.flush()
        await self.db.refresh(template)
        return template

    # ------------------------------------------------------------------
    # Update (partial)
    # ------------------------------------------------------------------
    async def update_template(
        self, template_id: UUID, data: dict[str, Any]
    ) -> ComplianceTemplate:
        """Apply a partial update to an existing template."""
        template = await self.get_template(template_id)

        # If renaming, ensure uniqueness
        if "name" in data and data["name"] != template.name:
            await self._assert_name_unique(data["name"])

        updatable_fields = {"name", "description", "is_active", "component_type_id"}
        for field, value in data.items():
            if field in updatable_fields:
                setattr(template, field, value)

        template.updated_at = self._now()
        await self.db.flush()
        await self.db.refresh(template)
        return template

    # ------------------------------------------------------------------
    # Add parameter
    # ------------------------------------------------------------------
    async def add_parameter(
        self,
        template_id: UUID,
        param_id: UUID,
        is_mandatory_override: bool | None = None,
        sort_order: int = 0,
    ) -> ComplianceTemplateParameter:
        """Link a standard parameter to a template. Errors on duplicate."""
        # Ensure template exists
        await self.get_template(template_id)

        # Ensure standard parameter exists
        sp = await self.db.get(StandardParameter, param_id)
        if sp is None:
            raise NotFoundError("StandardParameter", param_id)

        # Check for duplicate link
        existing = await self.db.execute(
            select(ComplianceTemplateParameter).where(
                ComplianceTemplateParameter.compliance_template_id == template_id,
                ComplianceTemplateParameter.standard_parameter_id == param_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ConflictError(
                f"Parameter {param_id} is already linked to template {template_id}"
            )

        tp = ComplianceTemplateParameter(
            compliance_template_id=template_id,
            standard_parameter_id=param_id,
            is_mandatory_override=is_mandatory_override,
            sort_order=sort_order,
        )
        self.db.add(tp)
        await self.db.flush()
        await self.db.refresh(tp)
        return tp

    # ------------------------------------------------------------------
    # Remove parameter
    # ------------------------------------------------------------------
    async def remove_parameter(
        self, template_id: UUID, param_id: UUID
    ) -> None:
        """Unlink a standard parameter from a template."""
        result = await self.db.execute(
            select(ComplianceTemplateParameter).where(
                ComplianceTemplateParameter.compliance_template_id == template_id,
                ComplianceTemplateParameter.standard_parameter_id == param_id,
            )
        )
        link = result.scalar_one_or_none()
        if link is None:
            raise NotFoundError(
                "ComplianceTemplateParameter",
                f"{template_id}/{param_id}",
            )
        await self.db.delete(link)
        await self.db.flush()

    # ------------------------------------------------------------------
    # Resolve parameters (mandatory flag resolution)
    # ------------------------------------------------------------------
    async def resolve_parameters(
        self, template_id: UUID
    ) -> list[dict[str, Any]]:
        """Return the final parameter list with the mandatory flag resolved.

        Resolution rule: if ``is_mandatory_override`` is set on the
        template-parameter link, it takes precedence over the standard
        parameter's own ``is_mandatory`` flag.
        """
        template = await self.get_template(template_id)

        resolved: list[dict[str, Any]] = []
        for tp in sorted(template.template_parameters, key=lambda t: t.sort_order):
            sp = tp.standard_parameter
            is_mandatory = (
                tp.is_mandatory_override
                if tp.is_mandatory_override is not None
                else sp.is_mandatory
            )
            resolved.append(
                {
                    "template_parameter_id": tp.id,
                    "standard_parameter_id": sp.id,
                    "code": sp.code,
                    "display_name": sp.display_name,
                    "section": sp.section,
                    "data_type": sp.data_type.value,
                    "unit": sp.unit,
                    "is_mandatory": is_mandatory,
                    "sort_order": tp.sort_order,
                    "acceptance_min": sp.acceptance_min,
                    "acceptance_max": sp.acceptance_max,
                    "acceptance_enum": sp.acceptance_enum,
                    "regulatory_ref": sp.regulatory_ref,
                }
            )
        return resolved

    # ------------------------------------------------------------------
    # Clone
    # ------------------------------------------------------------------
    async def clone_template(
        self, template_id: UUID, new_name: str, actor_id: UUID
    ) -> ComplianceTemplate:
        """Deep-copy a template (including all parameter links) under a new name."""
        source = await self.get_template(template_id)
        await self._assert_name_unique(new_name)

        clone = ComplianceTemplate(
            name=new_name,
            component_type_id=source.component_type_id,
            description=source.description,
            is_active=source.is_active,
            created_by=actor_id,
        )
        self.db.add(clone)
        await self.db.flush()

        for tp in source.template_parameters:
            new_tp = ComplianceTemplateParameter(
                compliance_template_id=clone.id,
                standard_parameter_id=tp.standard_parameter_id,
                is_mandatory_override=tp.is_mandatory_override,
                sort_order=tp.sort_order,
            )
            self.db.add(new_tp)

        await self.db.flush()
        await self.db.refresh(clone)
        return clone

    # ------------------------------------------------------------------
    # Helpers (private)
    # ------------------------------------------------------------------
    async def _assert_name_unique(self, name: str) -> None:
        """Raise ConflictError if a template with this name already exists."""
        result = await self.db.execute(
            select(ComplianceTemplate.id).where(ComplianceTemplate.name == name)
        )
        if result.scalar_one_or_none() is not None:
            raise ConflictError(f"A template named '{name}' already exists")
