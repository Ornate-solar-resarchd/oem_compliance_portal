from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.data.seed import OEMS, COMPONENTS, PARAMETERS

router = APIRouter(prefix="/oems")

from app.api.v1.completeness import completeness as _completeness


class OEMCreate(BaseModel):
    name: str
    country_of_origin: str = "China"
    website: Optional[str] = ""
    contact_email: Optional[str] = ""


@router.get("/")
async def list_oems():
    items = []
    for o in OEMS:
        oem_models = [c for c in COMPONENTS if c["oem_id"] == o["id"]]
        completeness_scores = [_completeness(m) for m in oem_models]
        avg_completeness = round(sum(completeness_scores) / len(completeness_scores), 1) if completeness_scores else 0
        items.append({
            **o,
            "score": avg_completeness,
            "models": len(oem_models),
            "model_count": len(oem_models),
            "avg_compliance_score": avg_completeness,
            "data_completeness": avg_completeness,
        })
    return {"items": items, "total": len(items), "page": 1, "per_page": 50}


@router.post("/")
async def create_oem(body: OEMCreate):
    new_id = f"oem-new-{len(OEMS)+1:03d}"
    oem = {
        "id": new_id,
        "name": body.name,
        "country_of_origin": body.country_of_origin,
        "is_approved": False,
        "score": 0,
        "models": 0,
        "model_count": 0,
        "avg_compliance_score": 0,
        "website": body.website,
        "contact_email": body.contact_email,
    }
    OEMS.append(oem)
    return oem


@router.get("/{oem_id}")
async def get_oem(oem_id: str):
    oem = next((o for o in OEMS if o["id"] == oem_id), None)
    if not oem:
        return {"error": "OEM not found"}
    models = [c for c in COMPONENTS if c["oem_id"] == oem_id]
    enriched_models = []
    for m in models:
        comp_score = _completeness(m)
        params = PARAMETERS.get(m["id"], [])
        enriched_models.append({
            **m,
            "compliance_score": comp_score,
            "data_completeness": comp_score,
            "fill_rate": comp_score,
            "pass": len(params),
            "fail": 0,
            "waived": 0,
            "parameters_count": len(params),
        })
    completeness_scores = [m["data_completeness"] for m in enriched_models]
    avg = round(sum(completeness_scores) / len(completeness_scores), 1) if completeness_scores else 0
    return {
        **oem,
        "score": avg,
        "model_count": len(models),
        "avg_compliance_score": avg,
        "data_completeness": avg,
        "models": enriched_models,
    }
