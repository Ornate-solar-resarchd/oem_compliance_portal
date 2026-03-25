from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.data.seed import WORKFLOWS

router = APIRouter(prefix="/workflow")


@router.get("/pending")
async def pending_workflows():
    return {"items": WORKFLOWS, "total": len(WORKFLOWS), "page": 1, "per_page": 20}


@router.get("/count")
async def workflow_count():
    return {"pending": len(WORKFLOWS)}


class AdvanceRequest(BaseModel):
    action: str
    comment: Optional[str] = None
    signatory_name: Optional[str] = None
    project_id: Optional[str] = None
    waived_params: Optional[list] = None


@router.post("/{sheet_id}/advance")
async def advance_workflow(sheet_id: str, req: AdvanceRequest):
    wf = next((w for w in WORKFLOWS if w["id"] == sheet_id), None)
    if not wf:
        return {"status": "ok", "message": f"Workflow {sheet_id} advanced with action={req.action}"}

    stage_order = ["draft", "engineering_review", "technical_lead", "management", "customer_submission", "customer_signoff", "locked"]
    current = wf["workflow_stage"]
    current_idx = stage_order.index(current) if current in stage_order else 0

    if req.action == "reject":
        new_stage = "draft"
    elif req.action == "sign":
        new_stage = "locked"
    else:
        new_stage = stage_order[min(current_idx + 1, len(stage_order) - 1)]

    return {
        "status": "ok",
        "previous_stage": current,
        "current_stage": new_stage,
        "action": req.action,
        "sheet_id": sheet_id,
    }
