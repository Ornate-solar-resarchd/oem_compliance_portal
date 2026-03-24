"""
Google Drive Fetcher — proxy for the Google Apps Script backend.
Searches company Google Drive and downloads datasheets for extraction.
"""
import os
import httpx
import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/gdrive")

FETCHER_URL = os.environ.get("GDRIVE_FETCHER_URL", "")


def _get_fetcher_url():
    url = os.environ.get("GDRIVE_FETCHER_URL", "")
    if not url:
        raise HTTPException(status_code=503, detail="GDRIVE_FETCHER_URL not configured in .env")
    return url


@router.get("/search")
async def search_drive(q: str, type: str = ""):
    """Search company Google Drive for files matching query."""
    fetcher_url = _get_fetcher_url()

    params = {"q": q}
    if type:
        params["type"] = type

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(fetcher_url, params=params)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Drive search failed")

    return resp.json()


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download a file from Google Drive via the Apps Script proxy.
    Returns the file content as base64 for the frontend to process."""
    fetcher_url = _get_fetcher_url()

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        resp = await client.get(fetcher_url, params={"download": file_id})

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Download failed")

    # The Apps Script returns base64-encoded file content as text
    content_text = resp.text.strip()

    # Check if it's a JSON error response
    if content_text.startswith("{"):
        import json
        data = json.loads(content_text)
        if not data.get("success", True):
            raise HTTPException(status_code=400, detail=data.get("error", "Download failed"))

    return {"file_id": file_id, "content_base64": content_text}


class FetchAndExtractRequest(BaseModel):
    file_id: str
    file_name: str
    oem_name: str
    model_name: str
    category: str = "Cell"


@router.post("/fetch-and-extract")
async def fetch_and_extract(body: FetchAndExtractRequest):
    """Download a file from Google Drive and extract technical specs.
    This combines download + AI extraction in one call."""
    fetcher_url = _get_fetcher_url()

    # Step 1: Download via Apps Script proxy
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        resp = await client.get(fetcher_url, params={"download": body.file_id})

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Download failed")

    content_text = resp.text.strip()

    # Check for error
    if content_text.startswith("{"):
        import json
        data = json.loads(content_text)
        if not data.get("success", True):
            raise HTTPException(status_code=400, detail=data.get("error", "Download failed"))

    # Step 2: Decode base64 content
    try:
        file_bytes = base64.b64decode(content_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode file: {e}")

    # Step 3: Extract specs using the datasheet extraction engine
    from app.data.datasheet_extraction import extract_from_datasheet
    from app.data.seed import COMPONENTS, PARAMETERS, OEMS

    extracted_params = extract_from_datasheet(file_bytes, body.file_name, body.category)

    # Step 4: Calculate compliance
    pass_count = sum(1 for p in extracted_params if p.get("status") == "pass")
    fail_count = sum(1 for p in extracted_params if p.get("status") == "fail")
    total = len(extracted_params)
    score = round((pass_count / total) * 100, 1) if total > 0 else 0

    for p in extracted_params:
        if "confidence" not in p:
            p["confidence"] = 0.90

    # Step 5: Find or create OEM
    oem = next((o for o in OEMS if o["name"].lower() == body.oem_name.lower()), None)
    oem_id = oem["id"] if oem else f"oem-new-{len(OEMS)+1:03d}"

    if not oem:
        new_oem = {
            "id": oem_id, "name": body.oem_name, "country_of_origin": "Unknown",
            "is_approved": False, "score": 0, "models": 0, "model_count": 0,
            "avg_compliance_score": 0, "website": "", "contact_email": "",
        }
        OEMS.append(new_oem)

    # Step 6: Create component
    comp_id = f"comp-gdrive-{len(COMPONENTS)+1:03d}"
    new_comp = {
        "id": comp_id, "oem_id": oem_id, "oem_name": body.oem_name,
        "model_name": body.model_name,
        "sku": f"{body.oem_name[:3].upper()}-{body.category[:3].upper()}-{len(COMPONENTS)+1:03d}",
        "component_type_name": body.category,
        "fill_rate": 100 if total > 0 else 0,
        "compliance_score": score, "is_active": True,
        "pass": pass_count, "fail": fail_count, "waived": 0,
        "datasheet": body.file_name, "source": "gdrive", "gdrive_file_id": body.file_id,
    }
    COMPONENTS.append(new_comp)
    PARAMETERS[comp_id] = extracted_params

    # Step 7: Update OEM stats
    oem_obj = next((o for o in OEMS if o["id"] == oem_id), None)
    if oem_obj:
        oem_models = [c for c in COMPONENTS if c["oem_id"] == oem_id]
        oem_obj["models"] = len(oem_models)
        oem_obj["model_count"] = len(oem_models)
        scores = [c["compliance_score"] for c in oem_models if c["compliance_score"] > 0]
        oem_obj["avg_compliance_score"] = round(sum(scores) / len(scores), 1) if scores else 0
        oem_obj["score"] = oem_obj["avg_compliance_score"]

    return {
        "status": "extracted",
        "component_id": comp_id,
        "oem_name": body.oem_name,
        "model_name": body.model_name,
        "category": body.category,
        "file_name": body.file_name,
        "source": "gdrive",
        "parameters_extracted": total,
        "compliance_score": score,
        "pass": pass_count,
        "fail": fail_count,
        "parameters": extracted_params,
        "message": f"Fetched '{body.file_name}' from Drive and extracted {total} {body.category} specs",
    }
