from fastapi import APIRouter
from app.data.seed import TEMPLATES

router = APIRouter(prefix="/templates")


@router.get("/")
async def list_templates():
    return {"items": TEMPLATES, "total": len(TEMPLATES), "page": 1, "per_page": 20}


@router.get("/{template_id}")
async def get_template(template_id: str):
    tmpl = next((t for t in TEMPLATES if t["id"] == template_id), None)
    if not tmpl:
        return {"error": "Template not found"}
    return tmpl
