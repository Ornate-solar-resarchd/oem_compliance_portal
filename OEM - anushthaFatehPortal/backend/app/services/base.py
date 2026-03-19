"""
BaseService — shared foundation for all service-layer classes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Select, func, text
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """Thin base that holds a database session and actor context."""

    def __init__(self, db: AsyncSession, actor: dict[str, Any] | None = None) -> None:
        self.db = db
        self.actor = actor or {}

    async def _set_rls_context(self) -> None:
        """Set PostgreSQL session variables for Row-Level Security."""
        user_id = self.actor.get("user_id", "")
        role = self.actor.get("role", "")
        await self.db.execute(
            text(f"SET LOCAL app.current_user_id = '{user_id}'")
        )
        await self.db.execute(
            text(f"SET LOCAL app.current_user_role = '{role}'")
        )

    @staticmethod
    def _paginate(query: Select, page: int = 1, per_page: int = 20) -> Select:
        """Apply LIMIT / OFFSET to a SELECT statement."""
        offset = (max(page, 1) - 1) * per_page
        return query.limit(per_page).offset(offset)

    @staticmethod
    def _now() -> datetime:
        """Return timezone-aware UTC now."""
        return datetime.now(timezone.utc)
