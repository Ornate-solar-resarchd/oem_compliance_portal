"""
OEMService — business logic for OEM management.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError
from app.models.oem import ComponentModel, OEM
from app.services.base import BaseService


class OEMService(BaseService):
    """CRUD + domain operations for OEMs."""

    # ── List ────────────────────────────────────────────────────────────
    async def list_oems(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        country: str | None = None,
        is_approved: bool | None = None,
    ) -> dict[str, Any]:
        """Return a paginated list of OEMs with optional filters.

        Trigram search (pg_trgm) is used when *search* is provided so that
        partial / fuzzy matches against OEM name are supported.
        """
        query = select(OEM).order_by(OEM.name)

        if search:
            # pg_trgm similarity — requires CREATE EXTENSION pg_trgm
            query = query.where(
                func.similarity(OEM.name, search) > 0.15
            ).order_by(func.similarity(OEM.name, search).desc())

        if country is not None:
            query = query.where(OEM.country_of_origin == country)

        if is_approved is not None:
            query = query.where(OEM.is_approved == is_approved)

        # Total count (before pagination)
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Paginate
        paginated = self._paginate(query, page, per_page)
        rows = (await self.db.execute(paginated)).scalars().all()

        return {
            "items": rows,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": max(1, -(-total // per_page)),  # ceil division
        }

    # ── Get single ──────────────────────────────────────────────────────
    async def get_oem(self, oem_id: UUID) -> dict[str, Any]:
        """Return an OEM together with computed aggregates."""
        oem = await self.db.get(OEM, oem_id)
        if oem is None:
            raise NotFoundError("OEM", oem_id)

        # Computed: total models & average compliance score
        agg_query = select(
            func.count(ComponentModel.id).label("total_models"),
            func.coalesce(func.avg(ComponentModel.compliance_score), Decimal(0)).label("avg_compliance_score"),
        ).where(ComponentModel.oem_id == oem_id)

        row = (await self.db.execute(agg_query)).one()

        return {
            "oem": oem,
            "total_models": row.total_models,
            "avg_compliance_score": round(row.avg_compliance_score, 2),
        }

    # ── Create ──────────────────────────────────────────────────────────
    async def create_oem(self, data: dict[str, Any], actor_id: UUID) -> OEM:
        """Create a new OEM. Raises ConflictError on duplicate name."""
        # Pre-check uniqueness for a cleaner error message
        exists = (
            await self.db.execute(
                select(OEM.id).where(func.lower(OEM.name) == func.lower(data["name"]))
            )
        ).scalar_one_or_none()

        if exists:
            raise ConflictError(f"OEM with name '{data['name']}' already exists")

        oem = OEM(
            name=data["name"],
            country_of_origin=data["country_of_origin"],
            website=data.get("website"),
            contact_email=data.get("contact_email"),
            notes=data.get("notes"),
            created_by=actor_id,
        )
        self.db.add(oem)

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ConflictError(f"OEM with name '{data['name']}' already exists")

        return oem

    # ── Update ──────────────────────────────────────────────────────────
    async def update_oem(self, oem_id: UUID, data: dict[str, Any]) -> OEM:
        """Partial update of mutable OEM fields."""
        oem = await self.db.get(OEM, oem_id)
        if oem is None:
            raise NotFoundError("OEM", oem_id)

        allowed = {"name", "country_of_origin", "website", "contact_email", "notes"}
        for key, value in data.items():
            if key in allowed:
                setattr(oem, key, value)

        oem.updated_at = self._now()

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ConflictError(f"OEM with name '{data.get('name')}' already exists")

        return oem

    # ── Approve ─────────────────────────────────────────────────────────
    async def approve_oem(self, oem_id: UUID, actor_id: UUID) -> OEM:
        """Mark an OEM as approved."""
        oem = await self.db.get(OEM, oem_id)
        if oem is None:
            raise NotFoundError("OEM", oem_id)

        oem.is_approved = True
        oem.updated_at = self._now()
        await self.db.flush()
        return oem

    # ── Compliance Score ────────────────────────────────────────────────
    async def compute_oem_score(self, oem_id: UUID) -> Decimal:
        """Compute the average compliance_score across all component models
        belonging to this OEM and return the value."""
        oem = await self.db.get(OEM, oem_id)
        if oem is None:
            raise NotFoundError("OEM", oem_id)

        result = (
            await self.db.execute(
                select(
                    func.coalesce(func.avg(ComponentModel.compliance_score), Decimal(0))
                ).where(ComponentModel.oem_id == oem_id)
            )
        ).scalar_one()

        score = round(Decimal(result), 2)
        return score
