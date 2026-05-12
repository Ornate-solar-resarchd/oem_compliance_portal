from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from typing import Optional
import json, os, pathlib
from app.data.seed import COMPONENTS, PARAMETERS, OEMS

router = APIRouter(prefix="/components")

# ─── Custom parameters persistence ───────────────────────────────────────────
CUSTOM_PARAMS_PATH = pathlib.Path("/app/storage/custom_parameters.json")
CUSTOM_PARAMS_PATH.parent.mkdir(parents=True, exist_ok=True)

def _load_custom_params():
    """Load custom params from disk and merge into PARAMETERS dict.
    Honors _deleted tombstones so removed-seed-params stay removed."""
    if not CUSTOM_PARAMS_PATH.exists():
        return
    try:
        overrides = json.loads(CUSTOM_PARAMS_PATH.read_text())
        deleted = overrides.pop("_deleted", {}) or {}
        # Strip deleted codes from seed defaults
        for comp_id, codes in deleted.items():
            if comp_id in PARAMETERS:
                PARAMETERS[comp_id] = [p for p in PARAMETERS[comp_id] if p.get("code") not in codes]
        # Apply additions / edits
        for comp_id, params in overrides.items():
            existing = list(PARAMETERS.get(comp_id, []))
            existing_codes = {p.get("code") for p in existing}
            for p in params:
                if p.get("code") in existing_codes:
                    for idx, e in enumerate(existing):
                        if e.get("code") == p.get("code"):
                            existing[idx] = p
                            break
                else:
                    existing.append(p)
            PARAMETERS[comp_id] = existing
        # Put _deleted back for the writer (don't mutate file contents)
        overrides["_deleted"] = deleted
    except Exception as e:
        print(f"[custom_params] load error: {e}")

def _save_custom_params(custom: dict):
    CUSTOM_PARAMS_PATH.write_text(json.dumps(custom, indent=2, ensure_ascii=False))

def _read_custom_file() -> dict:
    if CUSTOM_PARAMS_PATH.exists():
        try:
            return json.loads(CUSTOM_PARAMS_PATH.read_text())
        except Exception:
            return {}
    return {}

# Load overrides at import time
_load_custom_params()

CATEGORIES = ["Cell", "DC Block", "PCS", "EMS"]

from app.api.v1.completeness import completeness as _completeness


@router.get("/")
async def list_components():
    items = []
    for c in COMPONENTS:
        comp_score = _completeness(c)
        params = PARAMETERS.get(c["id"], [])
        items.append({
            **c,
            "compliance_score": comp_score,
            "data_completeness": comp_score,
            "fill_rate": comp_score,
            "pass": len(params),
            "fail": 0,
            "waived": 0,
            "parameters_count": len(params),
        })
    return {"items": items, "total": len(items), "page": 1, "per_page": 50, "categories": CATEGORIES}


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

    # Save uploaded file to Google Drive so it's accessible later
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

    total = len(extracted_params)
    verified_count = sum(1 for p in extracted_params if p.get("verified"))

    # Ensure all params have verified field
    for p in extracted_params:
        if "verified" not in p:
            p["verified"] = True

    comp_id = f"comp-upload-{len(COMPONENTS)+1:03d}"
    new_comp = {
        "id": comp_id,
        "oem_id": oem_id,
        "oem_name": oem_name,
        "model_name": model_name,
        "sku": f"{oem_name[:3].upper()}-{category[:3].upper()}-{len(COMPONENTS)+1:03d}",
        "component_type_name": category,
        "is_active": True,
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
        oem_obj["model_count"] = oem_obj.get("model_count", 0)

    return {
        "status": "extracted",
        "component_id": comp_id,
        "oem_name": oem_name,
        "model_name": model_name,
        "category": category,
        "file_name": file.filename,
        "file_size_bytes": file_size,
        "parameters_extracted": total,
        "verified": verified_count,
        "parameters": extracted_params,
        "message": f"Extracted {total} {category} specs — {verified_count} verified",
        "gdrive_url": gdrive_url,
        "gdrive_saved": bool(gdrive_url),
    }


@router.get("/{component_id}")
async def get_component(component_id: str):
    comp = next((c for c in COMPONENTS if c["id"] == component_id), None)
    if not comp:
        return {"error": "Component not found"}
    params = PARAMETERS.get(component_id, [])
    comp_score = _completeness(comp)
    return {
        **comp,
        "compliance_score": comp_score,
        "data_completeness": comp_score,
        "fill_rate": comp_score,
        "pass": len(params),
        "fail": 0,
        "waived": 0,
        "parameters_count": len(params),
        "parameters": params,
    }


@router.get("/{component_id}/parameters")
async def get_component_params(component_id: str):
    params = PARAMETERS.get(component_id, [])
    return {"items": params, "total": len(params), "page": 1, "per_page": 50}


# ─── User-editable custom parameters ─────────────────────────────────────────

@router.post("/{component_id}/parameters")
async def add_component_param(component_id: str, body: dict = Body(...)):
    """Add a new parameter to a specific component (persisted across restarts)."""
    code = (body.get("code") or "").strip().upper()
    name = (body.get("name") or "").strip()
    value = body.get("value", "")
    unit = body.get("unit", "")
    section = (body.get("section") or "General").strip()
    if not code or not name:
        raise HTTPException(status_code=400, detail="code and name are required")
    # Find component
    comp = next((c for c in COMPONENTS if c["id"] == component_id), None)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    # Reject duplicate codes
    existing = PARAMETERS.get(component_id, [])
    if any(p.get("code") == code for p in existing):
        raise HTTPException(status_code=409, detail=f"Parameter code '{code}' already exists")
    new_param = {"code": code, "name": name, "value": str(value), "unit": unit, "section": section}
    # Persist to JSON
    custom = _read_custom_file()
    custom.setdefault(component_id, [])
    custom[component_id].append(new_param)
    _save_custom_params(custom)
    # Update in-memory
    PARAMETERS.setdefault(component_id, []).append(new_param)
    return {"ok": True, "parameter": new_param}


@router.patch("/{component_id}/parameters/{code}")
async def edit_component_param(component_id: str, code: str, body: dict = Body(...)):
    """Edit an existing parameter (creates an override; original seed remains)."""
    code = code.upper()
    params = PARAMETERS.get(component_id, [])
    target = next((p for p in params if p.get("code") == code), None)
    if not target:
        raise HTTPException(status_code=404, detail="Parameter not found")
    updated = {**target}
    for key in ("name", "value", "unit", "section"):
        if key in body and body[key] is not None:
            updated[key] = str(body[key]) if key == "value" else body[key]
    # Persist override
    custom = _read_custom_file()
    custom.setdefault(component_id, [])
    if any(p.get("code") == code for p in custom[component_id]):
        for idx, p in enumerate(custom[component_id]):
            if p.get("code") == code:
                custom[component_id][idx] = updated
                break
    else:
        custom[component_id].append(updated)
    _save_custom_params(custom)
    # Update in-memory
    for idx, p in enumerate(params):
        if p.get("code") == code:
            params[idx] = updated
            break
    return {"ok": True, "parameter": updated}


@router.delete("/{component_id}/parameters/{code}")
async def delete_component_param(component_id: str, code: str):
    """Delete a parameter from a component. Persisted in override file with a
    'deleted' marker so seed defaults stay removed across restarts."""
    code = code.upper()
    params = PARAMETERS.get(component_id, [])
    target = next((p for p in params if p.get("code") == code), None)
    if not target:
        raise HTTPException(status_code=404, detail="Parameter not found")
    custom = _read_custom_file()
    custom.setdefault(component_id, [])
    # Remove from override list if present
    custom[component_id] = [p for p in custom[component_id] if p.get("code") != code]
    # Add tombstone so reload doesn't re-add the seed default
    custom.setdefault("_deleted", {}).setdefault(component_id, [])
    if code not in custom["_deleted"][component_id]:
        custom["_deleted"][component_id].append(code)
    _save_custom_params(custom)
    # Remove from in-memory
    PARAMETERS[component_id] = [p for p in params if p.get("code") != code]
    return {"ok": True, "deleted_code": code}
