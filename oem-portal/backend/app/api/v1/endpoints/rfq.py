"""
RFQ endpoints — Upload any BESS RFQ document (PDF/Excel) and extract technical requirements.
Uses keyword-based extraction from actual document text. No hardcoded templates.
PDF parsing: PyMuPDF (fitz) for text + Camelot for table extraction.
"""
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import io
from app.data.seed import RFQS, COMPONENTS, PARAMETERS
from app.data.datasheet_extraction import extract_text_from_file

router = APIRouter(prefix="/rfq")


# ─── Text Extraction (delegates to shared engine) ───

def _extract_text(contents: bytes, filename: str) -> str:
    """Extract text from uploaded file — uses PyMuPDF + Camelot for PDFs."""
    return extract_text_from_file(contents, filename)


def _extract_project_meta(text: str) -> dict:
    """Extract project-level metadata from document text."""
    import re
    meta = {}

    # Capacity patterns
    mw_match = re.search(r"(\d+)\s*MW\s*/\s*(\d+)\s*MWh", text)
    if mw_match:
        meta["capacity"] = f"{mw_match.group(1)} MW / {mw_match.group(2)} MWh"

    # Location
    locations = re.findall(r"(?:Tamil Nadu|Rajasthan|Bihar|Kerala|Maharashtra|Gujarat|Uttar Pradesh|Madhya Pradesh|Karnataka|Andhra Pradesh|Telangana|Haryana|Punjab|West Bengal|Odisha|Jharkhand|Chhattisgarh|Bikaner|Chennai|Barh|Patna|Sitapur|Kochi)", text, re.IGNORECASE)
    if locations:
        meta["location"] = f"{locations[0]}, India"

    # RFQ reference
    ref_match = re.search(r"(?:RFQ|IFB|Tender)\s*(?:Reference|No\.?|Number)[\s:]*([A-Z0-9\-/]+)", text)
    if ref_match:
        meta["rfq_ref"] = ref_match.group(1)

    # Solar PV
    solar_match = re.search(r"(\d+)\s*MWp", text)
    if solar_match:
        meta["solar_pv"] = f"{solar_match.group(1)} MWp"

    # Design life
    life_match = re.search(r"design\s*life.*?(\d+)\s*years", text, re.IGNORECASE)
    if life_match:
        meta["design_life"] = f"{life_match.group(1)} Years"

    # Issuer
    issuers = re.findall(r"(NTPC|Evolve Energy|BSPGCL|TNGECL|Eagle Infra|NHPC|SECI|PGCIL)", text, re.IGNORECASE)
    if issuers:
        meta["issuer"] = issuers[0].upper()

    return meta


# ─── Endpoints ───

@router.get("/")
async def list_rfqs():
    return {"items": RFQS, "total": len(RFQS), "page": 1, "per_page": 20}


@router.post("/upload-multi")
async def upload_rfq_multi(
    files: List[UploadFile] = File(...),
    customer_name: str = Form(...),
    project_name: str = Form(...),
):
    """Upload multiple RFQ documents into ONE RFQ.
    All files are parsed, extracted directly via keyword/regex, merged, and deduplicated."""
    from app.data.rfq_extraction import extract_from_text

    all_requirements = []
    all_text = ""
    file_names = []
    total_size = 0

    for f in files:
        contents = await f.read()
        total_size += len(contents)
        file_names.append(f.filename or "unknown")

        doc_text = _extract_text(contents, f.filename or "")
        all_text += " " + doc_text

        reqs = extract_from_text(doc_text)
        all_requirements.extend(reqs)

    # Deduplicate by code
    seen_codes = set()
    final_reqs = []
    for r in all_requirements:
        code = r.get("code", "")
        if code and code in seen_codes:
            continue
        if code:
            seen_codes.add(code)
        final_reqs.append(r)

    project_meta = _extract_project_meta(all_text)
    if not project_meta.get("issuer"):
        project_meta["issuer"] = customer_name

    new_id = f"rfq-{len(RFQS) + 1:03d}"
    new_rfq = {
        "id": new_id,
        "customer_name": customer_name,
        "project_name": project_name,
        "status": "active",
        "created_at": "2026-03-30T10:00:00Z",
        "requirements": final_reqs,
        "source_file": ", ".join(file_names),
        "file_names": file_names,
        "files_count": len(files),
        "file_size": total_size,
        "file_type": "multi",
        "extraction_method": "keyword_regex",
        "text_extracted": len(all_text) > 0,
        "text_length": len(all_text),
        "gdrive_url": "",
    }
    if project_meta:
        new_rfq["project_meta"] = project_meta
    RFQS.append(new_rfq)

    return {
        "status": "extracted",
        "rfq_id": new_id,
        "customer_name": customer_name,
        "project_name": project_name,
        "file_names": file_names,
        "files_processed": len(files),
        "total_size_bytes": total_size,
        "text_extracted": len(all_text) > 0,
        "text_length": len(all_text),
        "requirements_extracted": len(final_reqs),
        "requirements": final_reqs,
        "project_meta": project_meta,
        "message": f"Extracted {len(final_reqs)} parameters from {len(files)} file(s)",
    }


@router.post("/upload")
async def upload_rfq(
    file: UploadFile = File(...),
    customer_name: str = Form(...),
    project_name: str = Form(...),
):
    """Upload any RFQ document (PDF/Excel/CSV) and extract technical requirements.

    The system:
    1. Reads the actual document text (PDF → PyMuPDF + Camelot, Excel → openpyxl)
    2. Scans for 80+ BESS technical parameters using keyword/regex matching
    3. Extracts values (capacities, percentages, certifications, etc.)
    4. Returns structured requirements for OEM comparison
    """
    from app.data.rfq_extraction import extract_from_text

    contents = await file.read()
    file_size = len(contents)
    file_ext = (file.filename or "").rsplit(".", 1)[-1].lower()

    # Step 1: Extract text from the document
    document_text = _extract_text(contents, file.filename or "")
    text_length = len(document_text)

    # Step 2: Direct keyword/regex extraction — no compliance templates
    extracted_requirements = extract_from_text(document_text)

    # Step 3: Extract project metadata
    project_meta = _extract_project_meta(document_text)
    if not project_meta.get("issuer"):
        project_meta["issuer"] = customer_name

    # Step 4: Create and store the RFQ
    new_id = f"rfq-{len(RFQS) + 1:03d}"
    new_rfq = {
        "id": new_id,
        "customer_name": customer_name,
        "project_name": project_name,
        "status": "active",
        "created_at": "2026-03-19T10:00:00Z",
        "requirements": extracted_requirements,
        "source_file": file.filename,
        "file_size": file_size,
        "file_type": file_ext,
        "extraction_method": "keyword_regex",
        "text_extracted": text_length > 0,
        "text_length": text_length,
        "gdrive_url": "",
    }
    if project_meta:
        new_rfq["project_meta"] = project_meta
    RFQS.append(new_rfq)

    return {
        "status": "extracted",
        "rfq_id": new_id,
        "customer_name": customer_name,
        "project_name": project_name,
        "file_name": file.filename,
        "file_size_bytes": file_size,
        "text_extracted": text_length > 0,
        "text_length": text_length,
        "requirements_extracted": len(extracted_requirements),
        "requirements": extracted_requirements,
        "project_meta": project_meta,
        "message": f"Extracted {len(extracted_requirements)} technical requirements from '{file.filename}' ({text_length} chars parsed)",
    }


@router.get("/{rfq_id}")
async def get_rfq(rfq_id: str):
    rfq = next((r for r in RFQS if r["id"] == rfq_id), None)
    if not rfq:
        return {"error": "RFQ not found"}
    return rfq


@router.get("/{rfq_id}/match")
async def match_rfq(rfq_id: str):
    rfq = next((r for r in RFQS if r["id"] == rfq_id), None)
    if not rfq:
        return {"error": "RFQ not found"}

    results = []
    for comp in COMPONENTS:
        params = PARAMETERS.get(comp["id"], [])
        if not params:
            continue

        param_map = {p["code"]: p for p in params}
        total_reqs = len(rfq["requirements"])
        passed = 0
        details = []

        for req in rfq["requirements"]:
            oem_param = param_map.get(req["code"])
            if not oem_param:
                details.append({
                    "parameter": req["parameter"],
                    "required": req["required_value"],
                    "oem_value": "N/A",
                    "match": False,
                    "section": req.get("section", ""),
                })
                continue

            oem_val = oem_param["value"]
            required = req["required_value"]
            match = False

            if required.startswith(">="):
                try:
                    match = float(oem_val) >= float(required[2:])
                except (ValueError, TypeError):
                    match = False
            elif required.startswith("<="):
                try:
                    match = float(oem_val) <= float(required[2:])
                except (ValueError, TypeError):
                    match = False
            elif required.lower() in ("yes", "true", "required"):
                match = oem_val.lower() in ("yes", "true", "certified", "pass")
            else:
                match = (
                    oem_val.strip().lower() == required.strip().lower()
                    or required.lower() in oem_val.lower()
                )

            if match:
                passed += 1

            details.append({
                "parameter": req["parameter"],
                "required": required,
                "oem_value": f"{oem_val} {oem_param['unit']}".strip(),
                "match": match,
                "section": req.get("section", ""),
            })

        match_pct = round((passed / total_reqs) * 100, 1) if total_reqs > 0 else 0
        results.append({
            "component_id": comp["id"],
            "model_name": comp["model_name"],
            "oem_name": comp["oem_name"],
            "match_percentage": match_pct,
            "passed": passed,
            "total": total_reqs,
            "details": details,
        })

    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return {"rfq_id": rfq_id, "customer": rfq["customer_name"], "matches": results}




class RFQCreate(BaseModel):
    customer_name: str
    project_name: str
    requirements: List[dict]


@router.post("/")
async def create_rfq(rfq: RFQCreate):
    new_id = f"rfq-{len(RFQS) + 1:03d}"
    new_rfq = {
        "id": new_id,
        "customer_name": rfq.customer_name,
        "project_name": rfq.project_name,
        "status": "active",
        "created_at": "2026-03-19T10:00:00Z",
        "requirements": rfq.requirements,
    }
    RFQS.append(new_rfq)
    return new_rfq
