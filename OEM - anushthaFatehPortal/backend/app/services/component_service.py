"""
ComponentService — business logic for ComponentModel and ParameterValue management.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError
from app.models.oem import ComponentModel, ComponentType, OEM
from app.models.parameter import (
    ExtractionSource,
    ParameterDataType,
    ParameterValue,
    StandardParameter,
)
from app.services.base import BaseService


class ComponentService(BaseService):
    """CRUD + domain operations for ComponentModels and ParameterValues."""

    # ── List Models ─────────────────────────────────────────────────────
    async def list_models(
        self,
        page: int = 1,
        per_page: int = 20,
        oem_id: UUID | None = None,
        component_type_id: UUID | None = None,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        """Paginated list of component models, joining OEM and type names."""
        query = (
            select(
                ComponentModel,
                OEM.name.label("oem_name"),
                ComponentType.name.label("component_type_name"),
            )
            .join(OEM, ComponentModel.oem_id == OEM.id)
            .join(ComponentType, ComponentModel.component_type_id == ComponentType.id)
            .order_by(ComponentModel.created_at.desc())
        )

        if oem_id is not None:
            query = query.where(ComponentModel.oem_id == oem_id)

        if component_type_id is not None:
            query = query.where(ComponentModel.component_type_id == component_type_id)

        if search:
            query = query.where(
                func.similarity(ComponentModel.model_name, search) > 0.15
            ).order_by(func.similarity(ComponentModel.model_name, search).desc())

        if is_active is not None:
            query = query.where(ComponentModel.is_active == is_active)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Paginate
        paginated = self._paginate(query, page, per_page)
        rows = (await self.db.execute(paginated)).all()

        items = []
        for row in rows:
            model = row[0]
            items.append({
                "model": model,
                "oem_name": row.oem_name,
                "component_type_name": row.component_type_name,
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": max(1, -(-total // per_page)),
        }

    # ── Get Single Model ────────────────────────────────────────────────
    async def get_model(self, model_id: UUID) -> dict[str, Any]:
        """Full detail for one component model, including OEM info and
        parameter values grouped by section."""
        query = (
            select(ComponentModel)
            .options(
                selectinload(ComponentModel.oem),
                selectinload(ComponentModel.component_type),
                selectinload(ComponentModel.parameter_values).selectinload(
                    ParameterValue.standard_parameter
                ),
            )
            .where(ComponentModel.id == model_id)
        )
        result = (await self.db.execute(query)).scalar_one_or_none()

        if result is None:
            raise NotFoundError("ComponentModel", model_id)

        model: ComponentModel = result

        # Group parameter values by section
        sections: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for pv in model.parameter_values:
            sp = pv.standard_parameter
            sections[sp.section].append({
                "parameter_value_id": pv.id,
                "parameter_id": sp.id,
                "code": sp.code,
                "display_name": sp.display_name,
                "data_type": sp.data_type.value,
                "unit": sp.unit,
                "is_mandatory": sp.is_mandatory,
                "value_raw": pv.value_raw,
                "value_jsonb": pv.value_jsonb,
                "confidence": pv.confidence,
                "source": pv.source.value,
                "is_verified": pv.is_verified,
            })

        return {
            "model": model,
            "oem": model.oem,
            "component_type": model.component_type,
            "parameter_sections": dict(sections),
        }

    # ── Create Model ────────────────────────────────────────────────────
    async def create_model(self, data: dict[str, Any], actor_id: UUID) -> ComponentModel:
        """Create a new component model. Validates OEM exists and enforces
        UNIQUE(oem_id, model_name)."""
        # Validate OEM
        oem = await self.db.get(OEM, data["oem_id"])
        if oem is None:
            raise NotFoundError("OEM", data["oem_id"])

        # Pre-check uniqueness
        exists = (
            await self.db.execute(
                select(ComponentModel.id).where(
                    and_(
                        ComponentModel.oem_id == data["oem_id"],
                        func.lower(ComponentModel.model_name) == func.lower(data["model_name"]),
                    )
                )
            )
        ).scalar_one_or_none()

        if exists:
            raise ConflictError(
                f"Model '{data['model_name']}' already exists for this OEM"
            )

        model = ComponentModel(
            oem_id=data["oem_id"],
            component_type_id=data["component_type_id"],
            model_name=data["model_name"],
            datasheet_url=data.get("datasheet_url"),
            datasheet_minio_key=data.get("datasheet_minio_key"),
            created_by=actor_id,
        )
        self.db.add(model)

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ConflictError(
                f"Model '{data['model_name']}' already exists for this OEM"
            )

        return model

    # ── Update Model ────────────────────────────────────────────────────
    async def update_model(self, model_id: UUID, data: dict[str, Any]) -> ComponentModel:
        """Partial update of mutable component model fields."""
        model = await self.db.get(ComponentModel, model_id)
        if model is None:
            raise NotFoundError("ComponentModel", model_id)

        allowed = {"model_name", "datasheet_url", "datasheet_minio_key", "is_active"}
        for key, value in data.items():
            if key in allowed:
                setattr(model, key, value)

        model.updated_at = self._now()

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ConflictError(
                f"Model '{data.get('model_name')}' already exists for this OEM"
            )

        return model

    # ── Parameter Values ────────────────────────────────────────────────
    async def get_parameter_values(self, model_id: UUID) -> list[dict[str, Any]]:
        """All parameter values for a model, joined with standard_parameters."""
        model = await self.db.get(ComponentModel, model_id)
        if model is None:
            raise NotFoundError("ComponentModel", model_id)

        query = (
            select(ParameterValue, StandardParameter)
            .join(
                StandardParameter,
                ParameterValue.standard_parameter_id == StandardParameter.id,
            )
            .where(ParameterValue.component_model_id == model_id)
            .order_by(StandardParameter.section, StandardParameter.sort_order)
        )
        rows = (await self.db.execute(query)).all()

        return [
            {
                "parameter_value": pv,
                "standard_parameter": sp,
            }
            for pv, sp in rows
        ]

    # ── Upsert Parameter Value ──────────────────────────────────────────
    async def upsert_parameter_value(
        self,
        model_id: UUID,
        param_id: UUID,
        value_raw: str | None,
        source: ExtractionSource,
        confidence: Decimal | None,
        actor_id: UUID,
    ) -> ParameterValue:
        """Insert or update a single parameter value for a model."""
        # Ensure model exists
        model = await self.db.get(ComponentModel, model_id)
        if model is None:
            raise NotFoundError("ComponentModel", model_id)

        # Ensure parameter exists
        param = await self.db.get(StandardParameter, param_id)
        if param is None:
            raise NotFoundError("StandardParameter", param_id)

        # Look for existing value
        existing = (
            await self.db.execute(
                select(ParameterValue).where(
                    and_(
                        ParameterValue.component_model_id == model_id,
                        ParameterValue.standard_parameter_id == param_id,
                    )
                )
            )
        ).scalar_one_or_none()

        now = self._now()

        if existing:
            existing.value_raw = value_raw
            existing.source = source
            existing.confidence = confidence
            existing.updated_at = now
            if source == ExtractionSource.ai:
                existing.extracted_at = now
            await self.db.flush()
            return existing

        pv = ParameterValue(
            component_model_id=model_id,
            standard_parameter_id=param_id,
            value_raw=value_raw,
            source=source,
            confidence=confidence,
        )
        if source == ExtractionSource.ai:
            pv.extracted_at = now
        self.db.add(pv)
        await self.db.flush()
        return pv

    # ── Fill Rate ───────────────────────────────────────────────────────
    async def compute_fill_rate(self, model_id: UUID) -> Decimal:
        """(non-null values / total params for component type) * 100.

        Persists the computed value on the model row and returns it."""
        model = await self.db.get(ComponentModel, model_id)
        if model is None:
            raise NotFoundError("ComponentModel", model_id)

        # Total standard parameters for this component type
        total_params = (
            await self.db.execute(
                select(func.count(StandardParameter.id)).where(
                    StandardParameter.component_type_id == model.component_type_id
                )
            )
        ).scalar_one()

        if total_params == 0:
            model.fill_rate = Decimal(0)
            model.updated_at = self._now()
            await self.db.flush()
            return Decimal(0)

        # Count non-null values
        filled = (
            await self.db.execute(
                select(func.count(ParameterValue.id)).where(
                    and_(
                        ParameterValue.component_model_id == model_id,
                        ParameterValue.value_raw.isnot(None),
                    )
                )
            )
        ).scalar_one()

        fill_rate = round(Decimal(filled) / Decimal(total_params) * 100, 2)
        model.fill_rate = fill_rate
        model.updated_at = self._now()
        await self.db.flush()
        return fill_rate

    # ── Compliance Score ────────────────────────────────────────────────
    async def compute_model_compliance_score(self, model_id: UUID) -> Decimal:
        """Evaluate each parameter value against the acceptance criteria
        defined on its standard_parameter and compute an overall score.

        Score = (passing parameters / total evaluated parameters) * 100

        Acceptance rules by data_type:
        - numeric: acceptance_min <= value <= acceptance_max
        - range:   both bounds of the value range must fall within acceptance
        - boolean: value_raw in ('true', '1', 'yes') treated as True
        - enum:    value_raw must be in acceptance_enum list
        - text:    considered passing if value_raw is non-empty

        Persists the score on the model row and returns it.
        """
        model = await self.db.get(ComponentModel, model_id)
        if model is None:
            raise NotFoundError("ComponentModel", model_id)

        # Fetch all parameter values with their standard_parameter
        query = (
            select(ParameterValue, StandardParameter)
            .join(
                StandardParameter,
                ParameterValue.standard_parameter_id == StandardParameter.id,
            )
            .where(ParameterValue.component_model_id == model_id)
        )
        rows = (await self.db.execute(query)).all()

        if not rows:
            model.compliance_score = Decimal(0)
            model.updated_at = self._now()
            await self.db.flush()
            return Decimal(0)

        passing = 0
        evaluated = 0

        for pv, sp in rows:
            if pv.value_raw is None:
                continue  # skip unfilled parameters

            evaluated += 1

            if sp.data_type == ParameterDataType.numeric:
                try:
                    val = Decimal(pv.value_raw)
                except Exception:
                    continue
                in_min = sp.acceptance_min is None or val >= sp.acceptance_min
                in_max = sp.acceptance_max is None or val <= sp.acceptance_max
                if in_min and in_max:
                    passing += 1

            elif sp.data_type == ParameterDataType.range:
                # Expect value_jsonb with {"min": ..., "max": ...} or
                # value_raw as "min-max"
                try:
                    if pv.value_jsonb and "min" in pv.value_jsonb and "max" in pv.value_jsonb:
                        lo = Decimal(str(pv.value_jsonb["min"]))
                        hi = Decimal(str(pv.value_jsonb["max"]))
                    else:
                        parts = pv.value_raw.split("-")
                        lo, hi = Decimal(parts[0].strip()), Decimal(parts[1].strip())
                except Exception:
                    continue
                lo_ok = sp.acceptance_min is None or lo >= sp.acceptance_min
                hi_ok = sp.acceptance_max is None or hi <= sp.acceptance_max
                if lo_ok and hi_ok:
                    passing += 1

            elif sp.data_type == ParameterDataType.boolean:
                # No acceptance criteria needed — presence is enough
                passing += 1

            elif sp.data_type == ParameterDataType.enum:
                if sp.acceptance_enum and pv.value_raw in sp.acceptance_enum:
                    passing += 1
                elif not sp.acceptance_enum:
                    # No restricted set defined — any value passes
                    passing += 1

            elif sp.data_type == ParameterDataType.text:
                if pv.value_raw.strip():
                    passing += 1

        score = (
            round(Decimal(passing) / Decimal(evaluated) * 100, 2)
            if evaluated > 0
            else Decimal(0)
        )

        model.compliance_score = score
        model.updated_at = self._now()
        await self.db.flush()
        return score
