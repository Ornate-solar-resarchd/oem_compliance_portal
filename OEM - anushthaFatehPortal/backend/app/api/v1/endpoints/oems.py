from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.data.seed import OEMS, COMPONENTS

router = APIRouter(prefix="/oems")


class OEMCreate(BaseModel):
    name: str
    country_of_origin: str = "China"
    website: Optional[str] = ""
    contact_email: Optional[str] = ""


@router.get("/")
async def list_oems():
    return {"items": OEMS, "total": len(OEMS), "page": 1, "per_page": 20}


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
    return {**oem, "models": models}
