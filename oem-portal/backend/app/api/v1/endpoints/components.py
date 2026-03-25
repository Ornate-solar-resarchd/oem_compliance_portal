from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from app.data.seed import COMPONENTS, PARAMETERS, OEMS

router = APIRouter(prefix="/components")

CATEGORIES = ["Cell", "DC Block", "PCS", "EMS"]


@router.get("/")
async def list_components():
    return {"items": COMPONENTS, "total": len(COMPONENTS), "page": 1, "per_page": 50, "categories": CATEGORIES}


@router.get("/categories")
async def list_categories():
    return {"categories": CATEGORIES}


@router.post("/upload-datasheet")
async def upload_datasheet(
    file: UploadFile = File(...),
    oem_name: str = Form(...),
    model_name: str = Form(...),
    category: str = Form("Cell"),
):
    """Upload a PDF/Excel datasheet for any category (Cell, DC Block, PCS, EMS).
    AI extracts all technical specs from the document."""

    contents = await file.read()
    file_size = len(contents)
    file_ext = (file.filename or "").rsplit(".", 1)[-1].lower()

    # Save to Google Drive (async, non-blocking)
    from app.data.gdrive_upload import upload_to_gdrive
    gdrive_result = await upload_to_gdrive(contents, file.filename or "datasheet.pdf")
    gdrive_url = ""
    gdrive_file_id = ""
    if gdrive_result.get("success"):
        gdrive_url = gdrive_result["file"]["url"]
        gdrive_file_id = gdrive_result["file"]["id"]

    # Find or create OEM
    oem = next((o for o in OEMS if o["name"].lower() == oem_name.lower()), None)
    oem_id = oem["id"] if oem else f"oem-new-{len(OEMS)+1:03d}"

    # If OEM doesn't exist, create it
    if not oem:
        new_oem = {
            "id": oem_id,
            "name": oem_name,
            "country_of_origin": "Unknown",
            "is_approved": False,
            "score": 0,
            "models": 0,
            "model_count": 0,
            "avg_compliance_score": 0,
            "website": "",
            "contact_email": "",
        }
        OEMS.append(new_oem)

    # Extract specs from the datasheet using AI
    from app.data.datasheet_extraction import extract_from_datasheet
    extracted_params = extract_from_datasheet(contents, file.filename or "", category)

    # Calculate compliance
    pass_count = sum(1 for p in extracted_params if p.get("status") == "pass")
    fail_count = sum(1 for p in extracted_params if p.get("status") == "fail")
    total = len(extracted_params)
    score = round((pass_count / total) * 100, 1) if total > 0 else 0
    fill_rate = 100 if total > 0 else 0

    # Add confidence if missing
    for p in extracted_params:
        if "confidence" not in p:
            p["confidence"] = 0.90

    comp_id = f"comp-upload-{len(COMPONENTS)+1:03d}"
    new_comp = {
        "id": comp_id,
        "oem_id": oem_id,
        "oem_name": oem_name,
        "model_name": model_name,
        "sku": f"{oem_name[:3].upper()}-{category[:3].upper()}-{len(COMPONENTS)+1:03d}",
        "component_type_name": category,
        "fill_rate": fill_rate,
        "compliance_score": score,
        "is_active": True,
        "pass": pass_count,
        "fail": fail_count,
        "waived": 0,
        "datasheet": file.filename or "uploaded.pdf",
        "gdrive_url": gdrive_url,
        "gdrive_file_id": gdrive_file_id,
    }
    COMPONENTS.append(new_comp)
    PARAMETERS[comp_id] = extracted_params

    # Update OEM model count
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
        "oem_name": oem_name,
        "model_name": model_name,
        "category": category,
        "file_name": file.filename,
        "file_size_bytes": file_size,
        "parameters_extracted": total,
        "compliance_score": score,
        "pass": pass_count,
        "fail": fail_count,
        "parameters": extracted_params,
        "message": f"Extracted {total} {category} specs from '{file.filename}'",
        "gdrive_url": gdrive_url,
        "gdrive_saved": bool(gdrive_url),
    }


@router.get("/{component_id}")
async def get_component(component_id: str):
    comp = next((c for c in COMPONENTS if c["id"] == component_id), None)
    if not comp:
        return {"error": "Component not found"}
    params = PARAMETERS.get(component_id, [])
    return {**comp, "parameters": params}


@router.get("/{component_id}/parameters")
async def get_component_params(component_id: str):
    params = PARAMETERS.get(component_id, [])
    return {"items": params, "total": len(params), "page": 1, "per_page": 50}
