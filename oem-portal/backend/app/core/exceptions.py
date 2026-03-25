"""
Custom exception hierarchy for the UnityESS Technical Compliance Portal.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str = "An unexpected error occurred", **context: Any):
        self.detail = detail
        self.context = context
        super().__init__(detail)

    def to_dict(self) -> dict:
        body: dict[str, Any] = {
            "error": self.error_code,
            "detail": self.detail,
        }
        if self.context:
            body["context"] = self.context
        return body


class NotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(self, entity_type: str, entity_id: str | UUID):
        super().__init__(
            detail=f"{entity_type} not found",
            entity_type=entity_type,
            entity_id=str(entity_id),
        )


class ConflictError(AppError):
    status_code = 409
    error_code = "CONFLICT"

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail=detail)


class ForbiddenError(AppError):
    status_code = 403
    error_code = "FORBIDDEN"

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail)


class ValidationError(AppError):
    status_code = 422
    error_code = "VALIDATION_ERROR"

    def __init__(self, field: str, message: str):
        super().__init__(detail=message, field=field)


class WorkflowTransitionError(AppError):
    status_code = 400
    error_code = "WORKFLOW_TRANSITION_ERROR"

    def __init__(self, current_stage: str, action: str, reason: str):
        super().__init__(
            detail=reason,
            current_stage=current_stage,
            action=action,
        )


class SheetLockedError(AppError):
    status_code = 409
    error_code = "SHEET_LOCKED"

    def __init__(self, sheet_number: str):
        super().__init__(
            detail=f"Sheet {sheet_number} is locked and cannot be modified",
            sheet_number=sheet_number,
        )


class ExtractionInProgressError(AppError):
    status_code = 409
    error_code = "EXTRACTION_IN_PROGRESS"

    def __init__(self, model_id: str | UUID):
        super().__init__(
            detail="An AI extraction job is already running for this model",
            model_id=str(model_id),
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach a global handler that converts AppError subclasses to JSON."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )
