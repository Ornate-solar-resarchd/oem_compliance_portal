"""
AuditService — append-only audit trail for every mutation in the portal.

Design contract:
  - `log()` NEVER raises exceptions that propagate to callers.  Audit
    failures are printed to stderr so they surface in container logs
    but never break a business operation.
  - Query methods (`list_logs`, `get_entity_history`) raise normally.
"""
from __future__ import annotations

import sys
import traceback
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog
from app.services.base import BaseService


class AuditService(BaseService):
    """Read/write access to the partitioned audit_logs table."""

    # ------------------------------------------------------------------
    # WRITE — fire-and-forget style (never propagates exceptions)
    # ------------------------------------------------------------------

    async def log(
        self,
        actor_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Insert a single audit entry.  Swallows all exceptions."""
        try:
            entry = AuditLog(
                actor_id=actor_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.add(entry)
            await self.db.flush()
        except Exception:
            # Roll back the failed INSERT so the session stays usable,
            # but NEVER let the exception escape.
            await self.db.rollback()
            print(
                f"[AUDIT-ERROR] Failed to write audit log "
                f"(action={action!r}, entity_type={entity_type!r}, "
                f"entity_id={entity_id!r}):\n"
                f"{traceback.format_exc()}",
                file=sys.stderr,
            )

    # ------------------------------------------------------------------
    # READ — admin-oriented queries
    # ------------------------------------------------------------------

    async def list_logs(
        self,
        page: int = 1,
        per_page: int = 20,
        *,
        actor_id: UUID | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict[str, Any]:
        """Paginated, filterable audit log listing (admin use)."""
        query: Select = select(AuditLog)

        # Dynamic filters
        if actor_id is not None:
            query = query.where(AuditLog.actor_id == actor_id)
        if entity_type is not None:
            query = query.where(AuditLog.entity_type == entity_type)
        if entity_id is not None:
            query = query.where(AuditLog.entity_id == entity_id)
        if date_from is not None:
            query = query.where(AuditLog.created_at >= date_from)
        if date_to is not None:
            query = query.where(AuditLog.created_at <= date_to)

        # Total count (before pagination)
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Order + paginate
        query = query.order_by(AuditLog.created_at.desc())
        query = self._paginate(query, page=page, per_page=per_page)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": max(1, -(-total // per_page)),  # ceil division
        }

    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: UUID,
    ) -> list[AuditLog]:
        """Return every audit entry for a specific entity, newest first."""
        query = (
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type)
            .where(AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
