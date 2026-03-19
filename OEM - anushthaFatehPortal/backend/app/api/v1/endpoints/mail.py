from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from app.data.seed import COMPONENTS, PARAMETERS

router = APIRouter(prefix="/mail")


class TechnicalMailRequest(BaseModel):
    to: str
    subject: Optional[str] = None
    component_id: str
    sections: Optional[List[str]] = None


@router.post("/technical")
async def send_technical_mail(req: TechnicalMailRequest):
    comp = next((c for c in COMPONENTS if c["id"] == req.component_id), None)
    if not comp:
        return {"error": "Component not found"}

    params = PARAMETERS.get(req.component_id, [])
    subject = req.subject or f"Technical Data: {comp['model_name']} ({comp['oem_name']})"

    # Filter by sections if specified
    if req.sections:
        params = [p for p in params if p.get("section") in req.sections]

    return {
        "status": "sent",
        "to": req.to,
        "subject": subject,
        "model_name": comp["model_name"],
        "oem_name": comp["oem_name"],
        "parameters_included": len(params),
        "message": f"Technical data for {comp['model_name']} sent to {req.to}",
    }


class ApprovalMailRequest(BaseModel):
    to: str
    sheet_id: str
    action: str
    comment: Optional[str] = None


@router.post("/approval")
async def send_approval_mail(req: ApprovalMailRequest):
    return {
        "status": "sent",
        "to": req.to,
        "action": req.action,
        "sheet_id": req.sheet_id,
        "message": f"Approval notification ({req.action}) sent to {req.to}",
    }
