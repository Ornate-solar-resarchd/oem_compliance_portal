"""Common/shared Pydantic schemas and re-exported enums."""
from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# Re-export enums from models so endpoint files can import from schemas
from app.models.user import UserRole
from app.models.oem import ComponentCategory
from app.models.parameter import ParameterDataType, ExtractionSource
from app.models.project import ProjectType, ProjectStatus
from app.models.sheet import WorkflowStage, ComplianceStatus
from app.models.workflow import ApprovalAction
from app.models.document import DocumentFormat, DocumentType

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
