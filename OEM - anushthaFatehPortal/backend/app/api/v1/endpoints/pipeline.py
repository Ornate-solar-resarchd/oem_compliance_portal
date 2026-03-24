from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from app.data.seed import PIPELINE, PIPELINE_STAGES, PIPELINE_STAGE_LABELS

router = APIRouter(prefix="/pipeline")


@router.get("/")
async def list_deals():
    return {
        "items": PIPELINE,
        "total": len(PIPELINE),
        "stages": PIPELINE_STAGES,
        "stage_labels": PIPELINE_STAGE_LABELS,
    }


@router.get("/stats")
async def pipeline_stats():
    stage_counts = {}
    total_value = 0
    for stage in PIPELINE_STAGES:
        stage_deals = [d for d in PIPELINE if d["stage"] == stage]
        stage_counts[stage] = len(stage_deals)

    won = len([d for d in PIPELINE if d.get("outcome") == "won"])
    lost = len([d for d in PIPELINE if d.get("outcome") == "lost"])

    return {
        "total_deals": len(PIPELINE),
        "stage_counts": stage_counts,
        "stage_labels": PIPELINE_STAGE_LABELS,
        "stages": PIPELINE_STAGES,
        "won": won,
        "lost": lost,
        "active": len(PIPELINE) - won - lost,
    }


@router.get("/{deal_id}")
async def get_deal(deal_id: str):
    deal = next((d for d in PIPELINE if d["id"] == deal_id), None)
    if not deal:
        return {"error": "Deal not found"}
    return deal


class DealCreate(BaseModel):
    title: str
    customer: str
    contact_person: Optional[str] = ""
    contact_email: Optional[str] = ""
    contact_phone: Optional[str] = ""
    capacity: Optional[str] = ""
    location: Optional[str] = ""
    project_type: Optional[str] = "utility"
    estimated_value: Optional[str] = ""
    notes: Optional[str] = ""
    priority: Optional[str] = "medium"


@router.post("/")
async def create_deal(body: DealCreate):
    new_id = f"deal-{len(PIPELINE) + 1:03d}"
    deal = {
        "id": new_id,
        "title": body.title,
        "customer": body.customer,
        "contact_person": body.contact_person,
        "contact_email": body.contact_email,
        "contact_phone": body.contact_phone,
        "stage": "enquiry",
        "capacity": body.capacity,
        "location": body.location,
        "project_type": body.project_type,
        "estimated_value": body.estimated_value,
        "rfq_id": None,
        "priority": body.priority,
        "created_at": "2026-03-19T10:00:00Z",
        "updated_at": "2026-03-19T10:00:00Z",
        "notes": body.notes,
        "activities": [
            {"date": "2026-03-19", "type": "enquiry", "note": "New lead created"},
        ],
    }
    PIPELINE.append(deal)
    return deal


class StageAdvance(BaseModel):
    stage: str
    note: Optional[str] = ""


@router.post("/{deal_id}/advance")
async def advance_deal(deal_id: str, body: StageAdvance):
    deal = next((d for d in PIPELINE if d["id"] == deal_id), None)
    if not deal:
        return {"error": "Deal not found"}

    prev_stage = deal["stage"]
    deal["stage"] = body.stage
    deal["updated_at"] = "2026-03-19T12:00:00Z"
    deal["activities"].append({
        "date": "2026-03-19",
        "type": body.stage,
        "note": body.note or f"Moved to {PIPELINE_STAGE_LABELS.get(body.stage, body.stage)}",
    })

    if body.stage == "final":
        deal["outcome"] = "won"

    return {
        "status": "ok",
        "deal_id": deal_id,
        "previous_stage": prev_stage,
        "current_stage": body.stage,
    }
