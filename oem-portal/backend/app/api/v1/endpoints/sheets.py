from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.data.seed import SHEETS, PARAMETERS, WORKFLOWS, COMPONENTS, PROJECTS

router = APIRouter(prefix="/sheets")


@router.get("/")
async def list_sheets():
    return {"items": SHEETS, "total": len(SHEETS), "page": 1, "per_page": 20}


class SheetCreate(BaseModel):
    project_id: str
    component_id: str


@router.post("/")
async def create_sheet(body: SheetCreate):
    """Create a new compliance sheet linking a project to a component model."""
    project = next((p for p in PROJECTS if p["id"] == body.project_id), None)
    if not project:
        return {"error": "Project not found"}

    component = next((c for c in COMPONENTS if c["id"] == body.component_id), None)
    if not component:
        return {"error": "Component not found"}

    sheet_num = f"TCS-{len(SHEETS) + 1:03d}"
    sheet_id = f"sheet-{len(SHEETS) + 1:03d}"

    # Get component's parameters for compliance data
    params = PARAMETERS.get(body.component_id, [])
    verified_count = sum(1 for p in params if p.get("verified", True))
    total = len(params)

    new_sheet = {
        "id": sheet_id,
        "sheet_number": sheet_num,
        "project_id": body.project_id,
        "project_name": project["name"],
        "component_id": body.component_id,
        "component_model_name": component["model_name"],
        "workflow_stage": "draft",
        "compliance_score": 0,
        "revision": "r1",
        "verified": verified_count,
        "parameters_count": total,
        "pass": 0,
        "fail": 0,
        "waived": 0,
    }
    SHEETS.append(new_sheet)

    new_workflow = {
        "id": sheet_id,
        "sheet_number": sheet_num,
        "project_name": project["name"],
        "workflow_stage": "draft",
        "compliance_score": 0,
        "component_model_name": component["model_name"],
        "waiting_hours": 0,
        "revision": "r1",
        "verified": verified_count,
        "parameters_count": total,
        "pass": 0,
        "fail": 0,
        "waived": 0,
    }
    WORKFLOWS.append(new_workflow)

    return new_sheet


@router.get("/{sheet_id}")
async def get_sheet(sheet_id: str):
    sheet = next((s for s in SHEETS if s["id"] == sheet_id), None)
    if not sheet:
        return {"error": "Sheet not found"}
    params = PARAMETERS.get(sheet.get("component_id", ""), [])
    return {**sheet, "compliance_results": params}
