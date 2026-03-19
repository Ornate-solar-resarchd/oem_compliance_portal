from fastapi import APIRouter
from app.data.seed import SHEETS, PARAMETERS

router = APIRouter(prefix="/sheets")


@router.get("/")
async def list_sheets():
    return {"items": SHEETS, "total": len(SHEETS), "page": 1, "per_page": 20}


@router.get("/{sheet_id}")
async def get_sheet(sheet_id: str):
    sheet = next((s for s in SHEETS if s["id"] == sheet_id), None)
    if not sheet:
        return {"error": "Sheet not found"}
    params = PARAMETERS.get(sheet.get("component_id", ""), [])
    return {**sheet, "compliance_results": params}
