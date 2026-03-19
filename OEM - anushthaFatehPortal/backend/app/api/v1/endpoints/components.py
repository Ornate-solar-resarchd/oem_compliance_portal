from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from app.data.seed import COMPONENTS, PARAMETERS, OEMS

router = APIRouter(prefix="/components")


@router.get("/")
async def list_components():
    return {"items": COMPONENTS, "total": len(COMPONENTS), "page": 1, "per_page": 20}


@router.post("/upload-datasheet")
async def upload_datasheet(
    file: UploadFile = File(...),
    oem_name: str = Form(...),
    model_name: str = Form(...),
):
    """Accept PDF/XLS upload of OEM technical datasheet.
    In production this would trigger AI extraction via Claude API.
    For now, returns a simulated extraction result."""

    contents = await file.read()
    file_size = len(contents)
    file_ext = (file.filename or "").rsplit(".", 1)[-1].lower()

    # Find or create OEM
    oem = next((o for o in OEMS if o["name"].lower() == oem_name.lower()), None)
    oem_id = oem["id"] if oem else f"oem-new-{len(OEMS)+1:03d}"

    # Create component ID
    comp_id = f"comp-upload-{len(COMPONENTS)+1:03d}"

    # Simulated extraction result (in production: Claude API parses the PDF/XLS)
    new_comp = {
        "id": comp_id,
        "oem_id": oem_id,
        "oem_name": oem_name,
        "model_name": model_name,
        "sku": f"UPLOAD-{len(COMPONENTS)+1:03d}",
        "component_type_name": "Cell",
        "fill_rate": 0,
        "compliance_score": 0,
        "is_active": True,
        "pass": 0, "fail": 0, "waived": 0,
        "datasheet": file.filename or "uploaded.pdf",
    }
    COMPONENTS.append(new_comp)
    PARAMETERS[comp_id] = []

    return {
        "status": "uploaded",
        "component_id": comp_id,
        "oem_name": oem_name,
        "model_name": model_name,
        "file_name": file.filename,
        "file_size_bytes": file_size,
        "file_type": file_ext,
        "message": f"Datasheet '{file.filename}' uploaded for {model_name}. AI extraction will populate parameters.",
        "extraction_status": "pending",
    }


@router.post("/upload-compliance-sheet")
async def upload_compliance_sheet(
    file: UploadFile = File(...),
    oem_name: str = Form(...),
    model_name: str = Form(...),
):
    """Upload an OEM compliance sheet (Excel/PDF) and simulate AI extraction of parameter values.
    In production: Claude API would parse the sheet. For now, returns simulated data based on OEM name."""

    contents = await file.read()
    file_size = len(contents)

    # Find existing OEM or create new
    oem = next((o for o in OEMS if o["name"].lower() == oem_name.lower()), None)
    oem_id = oem["id"] if oem else f"oem-new-{len(OEMS)+1:03d}"

    # Check if this OEM already has a model with similar name
    existing = next((c for c in COMPONENTS if c["oem_name"].lower() == oem_name.lower() and model_name.lower() in c["model_name"].lower()), None)
    if existing:
        params = PARAMETERS.get(existing["id"], [])
        return {
            "status": "matched_existing",
            "component_id": existing["id"],
            "oem_name": existing["oem_name"],
            "model_name": existing["model_name"],
            "compliance_score": existing["compliance_score"],
            "parameters_count": len(params),
            "parameters": params,
            "file_name": file.filename,
            "message": f"Found existing model '{existing['model_name']}'. {len(params)} parameters loaded.",
        }

    # Simulate AI extraction: create new component with extracted params
    comp_id = f"comp-upload-{len(COMPONENTS)+1:03d}"

    # Generate realistic params based on OEM
    _base = PARAMETERS.get("comp-catl-280", [])
    import random
    extracted_params = []
    pass_count = 0
    fail_count = 0
    for p in _base:
        new_p = dict(p)
        new_p["confidence"] = round(random.uniform(0.85, 0.99), 2)
        # Slight random variation in values
        try:
            val = float(p["value"])
            variation = val * random.uniform(-0.05, 0.05)
            new_p["value"] = str(round(val + variation, 1) if "." in p["value"] else int(val + variation))
        except (ValueError, TypeError):
            pass
        if random.random() < 0.9:
            new_p["status"] = "pass"
            pass_count += 1
        else:
            new_p["status"] = "fail"
            fail_count += 1
        extracted_params.append(new_p)

    total = len(extracted_params)
    score = round((pass_count / total) * 100, 1) if total > 0 else 0

    new_comp = {
        "id": comp_id,
        "oem_id": oem_id,
        "oem_name": oem_name,
        "model_name": model_name,
        "sku": f"SHEET-{len(COMPONENTS)+1:03d}",
        "component_type_name": "Cell",
        "fill_rate": 100,
        "compliance_score": score,
        "is_active": True,
        "pass": pass_count, "fail": fail_count, "waived": 0,
        "datasheet": file.filename or "compliance-sheet.xlsx",
    }
    COMPONENTS.append(new_comp)
    PARAMETERS[comp_id] = extracted_params

    return {
        "status": "extracted",
        "component_id": comp_id,
        "oem_name": oem_name,
        "model_name": model_name,
        "compliance_score": score,
        "parameters_count": total,
        "pass": pass_count,
        "fail": fail_count,
        "parameters": extracted_params,
        "file_name": file.filename,
        "file_size_bytes": file_size,
        "message": f"Extracted {total} parameters from '{file.filename}'. Compliance score: {score}%",
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
