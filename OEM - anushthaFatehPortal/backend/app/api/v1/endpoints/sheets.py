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
    pass_count = sum(1 for p in params if p.get("status") == "pass")
    fail_count = sum(1 for p in params if p.get("status") == "fail")
    waived_count = sum(1 for p in params if p.get("status") == "waived")
    total = pass_count + fail_count + waived_count
    score = round((pass_count / total) * 100, 1) if total > 0 else 0

    new_sheet = {
        "id": sheet_id,
        "sheet_number": sheet_num,
        "project_id": body.project_id,
        "project_name": project["name"],
        "component_id": body.component_id,
        "component_model_name": component["model_name"],
        "workflow_stage": "draft",
        "compliance_score": score,
        "revision": "r1",
        "pass": pass_count,
        "fail": fail_count,
        "waived": waived_count,
    }
    SHEETS.append(new_sheet)

    # Also add to workflows (pending approval)
    new_workflow = {
        "id": sheet_id,
        "sheet_number": sheet_num,
        "project_name": project["name"],
        "workflow_stage": "draft",
        "compliance_score": score,
        "component_model_name": component["model_name"],
        "waiting_hours": 0,
        "revision": "r1",
        "pass": pass_count,
        "fail": fail_count,
        "waived": waived_count,
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
