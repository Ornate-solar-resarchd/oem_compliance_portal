"""
UnityESS Technical Compliance Portal — FastAPI Application
In-memory seed data mode — no database required.
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import (
    auth, oems, components, projects, sheets,
    workflow, documents, templates,
    dashboard, rfq, mail, comparison, pipeline, gdrive,
)

app = FastAPI(
    title="UnityESS Technical Compliance Portal",
    version="2.2.0",
    description="BESS component technical approval lifecycle management",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = "/api/v1"

app.include_router(auth.router, prefix=prefix, tags=["Auth"])
app.include_router(oems.router, prefix=prefix, tags=["OEMs"])
app.include_router(components.router, prefix=prefix, tags=["Components"])
app.include_router(projects.router, prefix=prefix, tags=["Projects"])
app.include_router(sheets.router, prefix=prefix, tags=["Sheets"])
app.include_router(workflow.router, prefix=prefix, tags=["Workflow"])
app.include_router(documents.router, prefix=prefix, tags=["Documents"])
app.include_router(templates.router, prefix=prefix, tags=["Templates"])
app.include_router(dashboard.router, prefix=prefix, tags=["Dashboard"])
app.include_router(rfq.router, prefix=prefix, tags=["RFQ"])
app.include_router(mail.router, prefix=prefix, tags=["Mail"])
app.include_router(comparison.router, prefix=prefix, tags=["Comparison"])
app.include_router(pipeline.router, prefix=prefix, tags=["Pipeline"])
app.include_router(gdrive.router, prefix=prefix, tags=["Google Drive"])


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "mode": "in-memory", "version": "2.2.0"}
