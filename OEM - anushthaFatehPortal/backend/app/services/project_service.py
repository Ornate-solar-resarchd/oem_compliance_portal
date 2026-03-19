"""
ProjectService — business logic for project CRUD, status transitions, and progress.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.project import Project, ProjectStatus, ProjectType
from app.models.sheet import TechnicalSheet, WorkflowStage
from app.models.user import User
from app.services.base import BaseService

# Weighted progress per workflow stage (percentage)
_STAGE_WEIGHT: dict[WorkflowStage, Decimal] = {
    WorkflowStage.draft: Decimal("0"),
    WorkflowStage.engineering_review: Decimal("16.67"),
    WorkflowStage.technical_lead: Decimal("33.33"),
    WorkflowStage.management: Decimal("50"),
    WorkflowStage.customer_submission: Decimal("66.67"),
    WorkflowStage.customer_signoff: Decimal("83.33"),
    WorkflowStage.locked: Decimal("100"),
}

# Valid status transitions: current_status -> set of allowed target statuses
_STATUS_TRANSITIONS: dict[ProjectStatus, set[ProjectStatus]] = {
    ProjectStatus.active: {
        ProjectStatus.on_hold,
        ProjectStatus.completed,
        ProjectStatus.cancelled,
    },
    ProjectStatus.on_hold: {ProjectStatus.active},
    ProjectStatus.completed: set(),
    ProjectStatus.cancelled: set(),
}


class ProjectService(BaseService):
    """Manages project lifecycle, querying, and progress computation."""

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------
    async def list_projects(
        self,
        page: int = 1,
        per_page: int = 20,
        status: ProjectStatus | None = None,
        project_type: ProjectType | None = None,
        search: str | None = None,
        customer_user_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Return a paginated list of projects with sheet count and progress."""

        # ----- count sub-query for sheets per project --------------------
        sheet_count_sq = (
            select(
                TechnicalSheet.project_id,
                func.count(TechnicalSheet.id).label("sheet_count"),
            )
            .group_by(TechnicalSheet.project_id)
            .subquery()
        )

        # ----- base query ------------------------------------------------
        query = select(Project).outerjoin(
            sheet_count_sq, Project.id == sheet_count_sq.c.project_id
        )

        # ----- filters ---------------------------------------------------
        if status is not None:
            query = query.where(Project.status == status)
        if project_type is not None:
            query = query.where(Project.project_type == project_type)
        if customer_user_id is not None:
            query = query.where(Project.customer_user_id == customer_user_id)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                Project.name.ilike(pattern) | Project.client_name.ilike(pattern)
            )

        # ----- total count -----------------------------------------------
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # ----- paginate & fetch ------------------------------------------
        query = query.order_by(Project.created_at.desc())
        query = self._paginate(query, page, per_page)
        result = await self.db.execute(query)
        projects = result.scalars().all()

        # ----- attach sheet count + progress per project -----------------
        items: list[dict[str, Any]] = []
        for proj in projects:
            progress = await self._compute_progress_for_project(proj.id)
            sheet_count = await self._sheet_count(proj.id)
            items.append(
                {
                    "project": proj,
                    "sheet_count": sheet_count,
                    "progress": progress,
                }
            )

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    # ------------------------------------------------------------------
    # Detail
    # ------------------------------------------------------------------
    async def get_project(self, project_id: UUID) -> Project:
        """Return a single project with all its technical sheets eagerly loaded."""
        query = (
            select(Project)
            .options(selectinload(Project.technical_sheets))
            .where(Project.id == project_id)
        )
        result = await self.db.execute(query)
        project = result.scalar_one_or_none()
        if project is None:
            raise NotFoundError("Project", project_id)
        return project

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    async def create_project(self, data: dict[str, Any], actor_id: UUID) -> Project:
        """Create a new project. Validates customer_user_id if supplied."""

        # Validate customer exists when provided
        customer_user_id = data.get("customer_user_id")
        if customer_user_id is not None:
            await self._validate_customer(customer_user_id)

        project = Project(
            name=data["name"],
            client_name=data["client_name"],
            project_type=data["project_type"],
            status=data.get("status", ProjectStatus.active),
            capacity_kwh=data.get("capacity_kwh"),
            power_kw=data.get("power_kw"),
            location=data.get("location"),
            state=data.get("state"),
            customer_user_id=customer_user_id,
            created_by=actor_id,
        )
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    # ------------------------------------------------------------------
    # Update (partial)
    # ------------------------------------------------------------------
    async def update_project(
        self, project_id: UUID, data: dict[str, Any]
    ) -> Project:
        """Apply a partial update to an existing project."""
        project = await self.get_project(project_id)

        # Validate customer if changing it
        if "customer_user_id" in data and data["customer_user_id"] is not None:
            await self._validate_customer(data["customer_user_id"])

        updatable_fields = {
            "name",
            "client_name",
            "project_type",
            "capacity_kwh",
            "power_kw",
            "location",
            "state",
            "customer_user_id",
        }
        for field, value in data.items():
            if field in updatable_fields:
                setattr(project, field, value)

        project.updated_at = self._now()
        await self.db.flush()
        await self.db.refresh(project)
        return project

    # ------------------------------------------------------------------
    # Status transition
    # ------------------------------------------------------------------
    async def update_status(
        self, project_id: UUID, new_status: ProjectStatus, actor_id: UUID
    ) -> Project:
        """Transition a project to a new status after validating the transition."""
        project = await self.get_project(project_id)
        current = project.status
        allowed = _STATUS_TRANSITIONS.get(current, set())

        if new_status not in allowed:
            raise ConflictError(
                f"Cannot transition project from '{current.value}' to '{new_status.value}'"
            )

        project.status = new_status
        project.updated_at = self._now()
        await self.db.flush()
        await self.db.refresh(project)
        return project

    # ------------------------------------------------------------------
    # Progress computation
    # ------------------------------------------------------------------
    async def compute_progress(self, project_id: UUID) -> Decimal:
        """Public entry-point: compute project progress and return a percentage."""
        # Ensure project exists
        await self.get_project(project_id)
        return await self._compute_progress_for_project(project_id)

    # ------------------------------------------------------------------
    # Helpers (private)
    # ------------------------------------------------------------------
    async def _compute_progress_for_project(self, project_id: UUID) -> Decimal:
        """Average of per-sheet stage weights. Returns 0 when there are no sheets."""
        query = select(TechnicalSheet.stage).where(
            TechnicalSheet.project_id == project_id
        )
        result = await self.db.execute(query)
        stages = result.scalars().all()

        if not stages:
            return Decimal("0")

        total = sum(_STAGE_WEIGHT.get(s, Decimal("0")) for s in stages)
        return (total / len(stages)).quantize(Decimal("0.01"))

    async def _sheet_count(self, project_id: UUID) -> int:
        query = select(func.count(TechnicalSheet.id)).where(
            TechnicalSheet.project_id == project_id
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def _validate_customer(self, user_id: UUID) -> None:
        """Ensure the given user_id exists and has the customer role."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundError("User", user_id)
        if user.role.value != "customer":
            raise ValidationError(
                "customer_user_id",
                f"User {user_id} does not have the 'customer' role",
            )
