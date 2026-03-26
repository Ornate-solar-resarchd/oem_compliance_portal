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
        "gdrive_url": f"https://drive.google.com/file/d/{body.file_id}/view",
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


class BatchImportRequest(BaseModel):
    """Batch import all datasheets for specific OEMs from Google Drive."""
    oem_searches: list  # e.g. [{"search": "Hopewind_PCS", "oem_name": "Hopewind", "category": "PCS"}]


@router.post("/batch-import")
async def batch_import(body: BatchImportRequest):
    """Search Drive for multiple OEMs, download all PDF datasheets, extract specs.

    Example request:
    {
        "oem_searches": [
            {"search": "Hopewind_PCS", "oem_name": "Hopewind", "category": "PCS"},
            {"search": "Elecod_PCS", "oem_name": "Elecod", "category": "PCS"},
            {"search": "Fimer_PCS", "oem_name": "Fimer", "category": "PCS"}
        ]
    }
    """
    fetcher_url = _get_fetcher_url()

    results = []
    errors = []

    for item in body.oem_searches:
        search_query = item.get("search", "")
        oem_name = item.get("oem_name", "Unknown")
        category = item.get("category", "Cell")

        if not search_query:
            errors.append({"oem": oem_name, "error": "No search query"})
            continue

        # Step 1: Search Drive for files
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(fetcher_url, params={"q": search_query, "type": "pdf"})

            if resp.status_code != 200:
                errors.append({"oem": oem_name, "error": f"Search failed: HTTP {resp.status_code}"})
                continue

            search_data = resp.json()
            if not search_data.get("success"):
                errors.append({"oem": oem_name, "error": search_data.get("error", "Search failed")})
                continue

            files = search_data.get("results", [])

            # Filter: only PDFs, skip duplicates, skip non-datasheet files
            seen_names = set()
            pdf_files = []
            skip_keywords = ["protocol", "communication", "rfq", "quotation", "invoice", "po ", "purchase"]

            for f in files:
                name_lower = f["name"].lower()
                # Skip non-datasheet files
                if any(kw in name_lower for kw in skip_keywords):
                    continue
                # Skip duplicates (same name)
                if f["name"] in seen_names:
                    continue
                # Only PDFs
                if f.get("type", "").upper() != "PDF":
                    continue
                seen_names.add(f["name"])
                pdf_files.append(f)

            if not pdf_files:
                errors.append({"oem": oem_name, "error": f"No PDF datasheets found for '{search_query}'"})
                continue

            # Step 2: Process each file
            for pdf_file in pdf_files:
                try:
                    # Download
                    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                        dl_resp = await client.get(fetcher_url, params={"download": pdf_file["id"]})

                    if dl_resp.status_code != 200:
                        errors.append({"oem": oem_name, "file": pdf_file["name"], "error": "Download failed"})
                        continue

                    content_text = dl_resp.text.strip()
                    if content_text.startswith("{"):
                        import json
                        err_data = json.loads(content_text)
                        if not err_data.get("success", True):
                            errors.append({"oem": oem_name, "file": pdf_file["name"], "error": err_data.get("error")})
                            continue

                    # Decode
                    file_bytes = base64.b64decode(content_text)

                    # Extract specs
                    from app.data.datasheet_extraction import extract_from_datasheet
                    from app.data.seed import COMPONENTS, PARAMETERS, OEMS

                    extracted_params = extract_from_datasheet(file_bytes, pdf_file["name"], category)

                    if not extracted_params:
                        errors.append({"oem": oem_name, "file": pdf_file["name"], "error": "No specs extracted"})
                        continue

                    # Calculate compliance
                    pass_count = sum(1 for p in extracted_params if p.get("status") == "pass")
                    fail_count = sum(1 for p in extracted_params if p.get("status") == "fail")
                    total = len(extracted_params)
                    score = round((pass_count / total) * 100, 1) if total > 0 else 0

                    for p in extracted_params:
                        if "confidence" not in p:
                            p["confidence"] = 0.90

                    # Find or create OEM
                    oem = next((o for o in OEMS if o["name"].lower() == oem_name.lower()), None)
                    oem_id = oem["id"] if oem else f"oem-new-{len(OEMS)+1:03d}"

                    if not oem:
                        new_oem = {
                            "id": oem_id, "name": oem_name, "country_of_origin": "China",
                            "is_approved": False, "score": 0, "models": 0, "model_count": 0,
                            "avg_compliance_score": 0, "website": "", "contact_email": "",
                        }
                        OEMS.append(new_oem)
                        oem = new_oem

                    # Derive model name from filename
                    model_name = pdf_file["name"].replace(".pdf", "").replace(".PDF", "")

                    # Check if already imported (by filename)
                    existing = next((c for c in COMPONENTS if c.get("datasheet") == pdf_file["name"] and c.get("oem_name", "").lower() == oem_name.lower()), None)
                    if existing:
                        results.append({
                            "oem": oem_name, "file": pdf_file["name"], "status": "skipped",
                            "message": "Already imported"
                        })
                        continue

                    # Create component
                    comp_id = f"comp-batch-{len(COMPONENTS)+1:03d}"
                    new_comp = {
                        "id": comp_id, "oem_id": oem_id, "oem_name": oem_name,
                        "model_name": model_name,
                        "sku": f"{oem_name[:3].upper()}-{category[:3].upper()}-{len(COMPONENTS)+1:03d}",
                        "component_type_name": category,
                        "fill_rate": 100 if total > 0 else 0,
                        "compliance_score": score, "is_active": True,
                        "pass": pass_count, "fail": fail_count, "waived": 0,
                        "datasheet": pdf_file["name"], "source": "gdrive",
                        "gdrive_file_id": pdf_file["id"],
                        "gdrive_url": f"https://drive.google.com/file/d/{pdf_file['id']}/view",
                    }
                    COMPONENTS.append(new_comp)
                    PARAMETERS[comp_id] = extracted_params

                    # Update OEM stats
                    oem_models = [c for c in COMPONENTS if c["oem_id"] == oem_id]
                    oem["models"] = len(oem_models)
                    oem["model_count"] = len(oem_models)
                    oem_scores = [c["compliance_score"] for c in oem_models if c["compliance_score"] > 0]
                    oem["avg_compliance_score"] = round(sum(oem_scores) / len(oem_scores), 1) if oem_scores else 0
                    oem["score"] = oem["avg_compliance_score"]

                    results.append({
                        "oem": oem_name, "file": pdf_file["name"], "status": "imported",
                        "component_id": comp_id, "params": total, "score": score,
                    })

                    print(f"[Batch Import] {oem_name}/{category}: {pdf_file['name']} → {total} params, {score}%")

                except Exception as e:
                    errors.append({"oem": oem_name, "file": pdf_file.get("name", "?"), "error": str(e)})

        except Exception as e:
            errors.append({"oem": oem_name, "error": str(e)})

    imported_count = sum(1 for r in results if r["status"] == "imported")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")

    return {
        "status": "complete",
        "imported": imported_count,
        "skipped": skipped_count,
        "errors": len(errors),
        "results": results,
        "error_details": errors,
        "message": f"Batch import complete: {imported_count} imported, {skipped_count} skipped, {len(errors)} errors",
    }
