from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.data.seed import DOCUMENTS, COMPONENTS, PARAMETERS

router = APIRouter(prefix="/documents")


@router.get("/")
async def list_documents():
    return {"items": DOCUMENTS, "total": len(DOCUMENTS), "page": 1, "per_page": 20}


class TechnicalSignalRequest(BaseModel):
    component_id: str
    format: Optional[str] = "PDF"


@router.post("/technical-signal")
async def generate_technical_signal(req: TechnicalSignalRequest):
    comp = next((c for c in COMPONENTS if c["id"] == req.component_id), None)
    if not comp:
        return {"error": "Component not found"}

    params = PARAMETERS.get(req.component_id, [])

    return {
        "status": "generated",
        "document_type": "Technical Signal",
        "model_name": comp["model_name"],
        "oem_name": comp["oem_name"],
        "format": req.format,
        "parameters_count": len(params),
        "compliance_score": comp.get("compliance_score", 0),
        "file_size": "3.2 MB",
        "message": f"Technical Signal for {comp['model_name']} generated successfully",
    }
