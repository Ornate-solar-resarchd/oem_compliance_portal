"""
ParameterService — CRUD for standard parameters + the compliance evaluation engine.

The `evaluate_compliance` method is the core deterministic engine that maps
(StandardParameter definition, raw OEM value) -> 'pass' | 'fail' | 'pending'.
It is a pure function (no DB, no I/O) so it can be unit-tested in isolation.
"""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ComponentType, StandardParameter, ParameterDataType
from app.services.base import BaseService


class ParameterService(BaseService):
    """Standard-parameter CRUD and compliance evaluation."""

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    async def list_standard_parameters(
        self,
        component_type_id: UUID | None = None,
        section: str | None = None,
    ) -> list[StandardParameter]:
        """Filtered list of standard parameters, ordered by sort_order."""
        query = select(StandardParameter)

        if component_type_id is not None:
            query = query.where(
                StandardParameter.component_type_id == component_type_id
            )
        if section is not None:
            query = query.where(StandardParameter.section == section)

        query = query.order_by(
            StandardParameter.sort_order.asc(),
            StandardParameter.code.asc(),
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_standard_parameter(
        self, param_id: UUID
    ) -> StandardParameter | None:
        """Fetch a single standard parameter by primary key."""
        return await self.db.get(StandardParameter, param_id)

    async def list_component_types(self) -> list[ComponentType]:
        """Return all component types, ordered by name."""
        query = select(ComponentType).order_by(ComponentType.name.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # WRITE
    # ------------------------------------------------------------------

    async def create_standard_parameter(
        self, data: dict[str, Any]
    ) -> StandardParameter:
        """
        Create a new standard parameter.

        Validates uniqueness on (component_type_id, code) — the DB has a
        UNIQUE constraint but we catch the IntegrityError and re-raise a
        friendlier ValueError so the API layer can return 409.
        """
        param = StandardParameter(**data)
        self.db.add(param)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(
                f"A parameter with code {data.get('code')!r} already exists "
                f"for component_type_id {data.get('component_type_id')!r}."
            )
        return param

    async def update_standard_parameter(
        self, param_id: UUID, data: dict[str, Any]
    ) -> StandardParameter | None:
        """
        Partial update of an existing standard parameter.

        Returns the updated object, or None if not found.
        """
        param = await self.db.get(StandardParameter, param_id)
        if param is None:
            return None

        for key, value in data.items():
            if hasattr(param, key):
                setattr(param, key, value)

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(
                f"A parameter with code {data.get('code')!r} already exists "
                f"for this component type."
            )
        return param

    # ------------------------------------------------------------------
    # COMPLIANCE EVALUATION ENGINE (pure function — no DB access)
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate_compliance(
        param: StandardParameter,
        value_raw: str | None,
        value_jsonb: dict[str, Any] | None = None,
    ) -> str:
        """
        Deterministic compliance check.

        Returns
        -------
        'pass'    — OEM value satisfies the acceptance criteria
        'fail'    — OEM value violates the acceptance criteria
        'pending' — value is missing or cannot be parsed

        Logic per data_type
        -------------------
        numeric : parse value_raw -> float; check acceptance_min / max
        range   : parse value_jsonb {"min", "max"}; OEM range must fit
                  within acceptance_min / max
        boolean : value_raw must match acceptance_enum (first element)
        enum    : value_raw must be in acceptance_enum (case-insensitive)
        text    : if acceptance_enum is set, must match; otherwise pass
        """
        # NULL / empty → pending
        if value_raw is None or str(value_raw).strip() == "":
            if param.data_type != ParameterDataType.range:
                return "pending"
            # For range type, value_jsonb is the primary source
            if value_jsonb is None:
                return "pending"

        data_type = param.data_type

        # ----- NUMERIC -----
        if data_type == ParameterDataType.numeric:
            return _evaluate_numeric(param, value_raw)

        # ----- RANGE -----
        if data_type == ParameterDataType.range:
            return _evaluate_range(param, value_jsonb)

        # ----- BOOLEAN -----
        if data_type == ParameterDataType.boolean:
            return _evaluate_boolean(param, value_raw)

        # ----- ENUM -----
        if data_type == ParameterDataType.enum:
            return _evaluate_enum(param, value_raw)

        # ----- TEXT -----
        if data_type == ParameterDataType.text:
            return _evaluate_text(param, value_raw)

        # Unknown data_type → pending (defensive)
        return "pending"


# ======================================================================
# Private helper functions (module-level for clarity)
# ======================================================================


def _evaluate_numeric(param: StandardParameter, value_raw: str | None) -> str:
    """Numeric: parse to float, check against acceptance_min / acceptance_max."""
    try:
        val = float(value_raw)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return "pending"

    if param.acceptance_min is not None and val < float(param.acceptance_min):
        return "fail"
    if param.acceptance_max is not None and val > float(param.acceptance_max):
        return "fail"

    return "pass"


def _evaluate_range(
    param: StandardParameter, value_jsonb: dict[str, Any] | None
) -> str:
    """Range: OEM min/max (from value_jsonb) must sit within acceptance range."""
    if value_jsonb is None:
        return "pending"

    try:
        oem_min = float(value_jsonb["min"])
        oem_max = float(value_jsonb["max"])
    except (KeyError, ValueError, TypeError):
        return "pending"

    # OEM range must be fully contained within the acceptance window
    if param.acceptance_min is not None and oem_min < float(param.acceptance_min):
        return "fail"
    if param.acceptance_max is not None and oem_max > float(param.acceptance_max):
        return "fail"

    return "pass"


def _evaluate_boolean(param: StandardParameter, value_raw: str | None) -> str:
    """Boolean: value_raw must match the expected value in acceptance_enum."""
    if value_raw is None:
        return "pending"

    accepted = param.acceptance_enum
    if not accepted:
        # No acceptance criteria defined — any boolean value passes
        return "pass"

    # Case-insensitive comparison against the accepted value(s)
    normalised = value_raw.strip().lower()
    accepted_lower = [v.lower() for v in accepted]
    return "pass" if normalised in accepted_lower else "fail"


def _evaluate_enum(param: StandardParameter, value_raw: str | None) -> str:
    """Enum: value_raw must appear in acceptance_enum (case-insensitive)."""
    if value_raw is None:
        return "pending"

    accepted = param.acceptance_enum
    if not accepted:
        return "pass"

    normalised = value_raw.strip().lower()
    accepted_lower = [v.lower() for v in accepted]
    return "pass" if normalised in accepted_lower else "fail"


def _evaluate_text(param: StandardParameter, value_raw: str | None) -> str:
    """Text: if acceptance_enum set, must match; otherwise always pass."""
    if value_raw is None:
        return "pending"

    accepted = param.acceptance_enum
    if not accepted:
        return "pass"

    normalised = value_raw.strip().lower()
    accepted_lower = [v.lower() for v in accepted]
    return "pass" if normalised in accepted_lower else "fail"
