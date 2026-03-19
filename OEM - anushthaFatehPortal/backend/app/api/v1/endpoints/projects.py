from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.data.seed import PROJECTS, SHEETS

router = APIRouter(prefix="/projects")


@router.get("/")
async def list_projects():
    return {"items": PROJECTS, "total": len(PROJECTS), "page": 1, "per_page": 20}


class ProjectCreate(BaseModel):
    name: str
    client_name: str
    project_type: str = "utility"
    kwh: Optional[int] = 0
    kw: Optional[int] = 0
    location: Optional[str] = ""


@router.post("/")
async def create_project(body: ProjectCreate):
    new_id = f"proj-{len(PROJECTS)+1:03d}"
    proj = {
        "id": new_id,
        "name": body.name,
        "client_name": body.client_name,
        "project_type": body.project_type,
        "kwh": body.kwh,
        "kw": body.kw,
        "location": body.location,
        "status": "active",
        "progress": 0,
    }
    PROJECTS.append(proj)
    return proj


@router.get("/{project_id}")
async def get_project(project_id: str):
    proj = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not proj:
        return {"error": "Project not found"}
    proj_sheets = [s for s in SHEETS if s["project_id"] == project_id]
    return {**proj, "sheets": proj_sheets}
