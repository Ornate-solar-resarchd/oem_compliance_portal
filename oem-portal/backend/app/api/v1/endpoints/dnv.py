"""DNV Intelligence — BESS evaluation reports from DNV assessments."""
from fastapi import APIRouter, UploadFile, File, Form
from app.data.dnv_seed import DNV_REPORTS, DNV_PRIMER
import io, os, json, re

router = APIRouter(prefix="/dnv")


@router.get("/")
async def list_dnv_reports(type: str = ""):
    items = DNV_REPORTS
    if type:
        items = [r for r in items if r["type"] == type]
    stats = {
        "total": len(DNV_REPORTS),
        "systems": sum(1 for r in DNV_REPORTS if r["type"] == "system"),
        "cells": sum(1 for r in DNV_REPORTS if r["type"] == "cell"),
    }
    return {"items": items, "stats": stats}


@router.get("/primer")
async def get_primer(cat: str = ""):
    items = DNV_PRIMER
    if cat and cat != "all":
        items = [p for p in items if p["cat"] == cat]
    categories = sorted(set(p["cat"] for p in DNV_PRIMER))
    return {"items": items, "total": len(items), "categories": categories}


@router.get("/{report_id}")
async def get_dnv_report(report_id: str):
    report = next((r for r in DNV_REPORTS if r["id"] == report_id), None)
    if not report:
        return {"error": "Report not found"}
    return report


@router.post("/upload")
async def upload_dnv_report(
    file: UploadFile = File(...),
    name: str = Form(...),
    model: str = Form(""),
    report_type: str = Form("system"),
):
    """Upload a DNV report PDF and extract BESS evaluation data."""
    contents = await file.read()
    file_ext = (file.filename or "").rsplit(".", 1)[-1].lower()

    # Extract text using PyMuPDF + Camelot (shared engine)
    from app.data.datasheet_extraction import extract_text_from_file
    text = extract_text_from_file(contents, file.filename or "report.pdf")

    # Keyword extraction — no AI needed
    extracted = _extract_dnv_keywords(text, name) if text else {}

    # Build report structure
    new_id = name.lower().replace(" ", "_") + f"_{len(DNV_REPORTS)+1}"
    new_report = {
        "id": new_id,
        "name": name,
        "fullName": extracted.get("fullName", name),
        "type": report_type,
        "model": model or extracted.get("model", ""),
        "capacity_kwh": extracted.get("capacity_kwh"),
        "power_kw": extracted.get("power_kw"),
        "cell": extracted.get("cell", {"chemistry": "LFP", "format": "Prismatic", "voltage_v": 3.2, "capacity_ah": None, "config": None, "total_cells": None}),
        "perf": extracted.get("perf", {"rte": None, "dod": None, "cycle_life": None, "calendar_life": None, "deg_per_year": None, "aux_kw": None}),
        "pcs": extracted.get("pcs"),
        "thermal": extracted.get("thermal", {"cooling": None, "cooling_kw": None, "t_chg_min": None, "t_chg_max": None, "t_dis_min": None, "t_dis_max": None, "alt_m": None}),
        "safety": extracted.get("safety", {"ip": None, "certs": [], "fire": None, "tr": None}),
        "bms": extracted.get("bms"),
        "phys": extracted.get("phys", {"container": None, "dims": None, "wt_t": None}),
        "company": extracted.get("company", {"loc": None, "founded": None, "iso": [], "warranty": None, "deployments": None, "deployed_gwh": None}),
        "dnv": extracted.get("dnv", {"company": None, "battery": None, "pcs": None, "safety": None, "quality": None, "service": None}),
        "summary": extracted.get("summary", f"DNV report for {name} {model}"),
        "source_file": file.filename,
    }
    DNV_REPORTS.append(new_report)

    return {
        "status": "imported",
        "id": new_id,
        "name": name,
        "model": new_report["model"],
        "type": report_type,
        "message": f"DNV report for {name} imported successfully",
    }


def _extract_dnv_with_ai(text: str, name: str) -> dict:
    """Use Claude (primary) or Gemini (fallback) to extract DNV report data."""

    # Try Claude first
    claude_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if claude_key and claude_key != "sk-placeholder" and len(claude_key) > 20:
        try:
            return _extract_dnv_claude(text, name, claude_key)
        except Exception as e:
            print(f"DNV Claude extraction error: {e}")

    # Fallback to Gemini
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key or gemini_key == "YOUR_GEMINI_KEY_HERE" or len(gemini_key) < 10:
        return _extract_dnv_keywords(text, name)

    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""Extract ALL technical data from this DNV BESS evaluation report for {name}.

Return a JSON object with this exact structure:
{{
  "fullName": "Full company name",
  "model": "Model name",
  "capacity_kwh": number or null,
  "power_kw": number or null,
  "cell": {{"chemistry": "LFP", "format": "Prismatic", "voltage_v": 3.2, "capacity_ah": number, "config": "string", "total_cells": number}},
  "perf": {{"rte": number (%), "dod": number, "cycle_life": number, "calendar_life": number (years), "deg_per_year": number, "aux_kw": "string"}},
  "pcs": {{"eff_peak": number (%), "eff_weighted": number, "ac_v": "string", "freq": "string", "dc_v_nom": number, "dc_v_range": "string", "grid": ["list"]}},
  "thermal": {{"cooling": "string", "cooling_kw": number, "t_chg_min": number, "t_chg_max": number, "t_dis_min": number, "t_dis_max": number, "alt_m": number}},
  "safety": {{"ip": "IP55", "certs": ["UL 9540A", "IEC 62619"], "fire": "string", "tr": "string"}},
  "bms": {{"supplier": "string", "protocols": ["CAN", "Modbus"], "soc_acc": number, "soh": true}},
  "phys": {{"container": "string", "dims": "string mm", "wt_t": number (tonnes)}},
  "company": {{"loc": "string", "founded": number, "iso": ["list"], "warranty": number, "deployments": number, "deployed_gwh": number}},
  "dnv": {{"company": "4 — Very Good" or null, "battery": "string" or null, "pcs": null, "safety": null, "quality": null, "service": null}},
  "summary": "2-3 sentence summary"
}}

Use null for missing values. Return ONLY JSON.

DOCUMENT TEXT:
{text[:30000]}"""

        response = model.generate_content(prompt)
        resp_text = response.text.strip()
        if resp_text.startswith("```"):
            resp_text = re.sub(r'^```(?:json)?\s*', '', resp_text)
            resp_text = re.sub(r'\s*```$', '', resp_text)
        return json.loads(resp_text)

    except Exception as e:
        print(f"DNV Gemini extraction error: {e}")
        return _extract_dnv_keywords(text, name)


def _extract_dnv_claude(text: str, name: str, api_key: str) -> dict:
    """Use Claude API to extract DNV report data."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Extract ALL technical data from this DNV BESS evaluation report for {name}.

Return a JSON object with this exact structure:
{{
  "fullName": "Full company name",
  "model": "Model name",
  "capacity_kwh": number or null,
  "power_kw": number or null,
  "cell": {{"chemistry": "LFP", "format": "Prismatic", "voltage_v": 3.2, "capacity_ah": number, "config": "string", "total_cells": number}},
  "perf": {{"rte": number (%), "dod": number, "cycle_life": number, "calendar_life": number (years), "deg_per_year": number, "aux_kw": "string"}},
  "pcs": {{"eff_peak": number (%), "eff_weighted": number, "ac_v": "string", "freq": "string", "dc_v_nom": number, "dc_v_range": "string", "grid": ["list"]}},
  "thermal": {{"cooling": "string", "cooling_kw": number, "t_chg_min": number, "t_chg_max": number, "t_dis_min": number, "t_dis_max": number, "alt_m": number}},
  "safety": {{"ip": "IP55", "certs": ["UL 9540A", "IEC 62619"], "fire": "string", "tr": "string"}},
  "bms": {{"supplier": "string", "protocols": ["CAN", "Modbus"], "soc_acc": number, "soh": true}},
  "phys": {{"container": "string", "dims": "string mm", "wt_t": number (tonnes)}},
  "company": {{"loc": "string", "founded": number, "iso": ["list"], "warranty": number, "deployments": number, "deployed_gwh": number}},
  "dnv": {{"company": "4 — Very Good" or null, "battery": "string" or null, "pcs": null, "safety": null, "quality": null, "service": null}},
  "summary": "2-3 sentence summary"
}}

Use null for missing values. Return ONLY JSON.

DOCUMENT TEXT:
{text[:30000]}"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    resp_text = message.content[0].text.strip()
    if resp_text.startswith("```"):
        resp_text = re.sub(r'^```(?:json)?\s*', '', resp_text)
        resp_text = re.sub(r'\s*```$', '', resp_text)
    return json.loads(resp_text)


def _extract_dnv_keywords(text: str, name: str) -> dict:
    """Fallback keyword extraction for DNV reports."""
    result = {"fullName": name, "summary": f"DNV evaluation report for {name}"}

    # Basic extractions
    rte_match = re.search(r'(?:RTE|round[\s-]*trip).*?(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)
    if rte_match:
        result.setdefault("perf", {})["rte"] = float(rte_match.group(1))

    cycle_match = re.search(r'(\d[\d,]*)\s*(?:cycle|cycles)', text, re.IGNORECASE)
    if cycle_match:
        result.setdefault("perf", {})["cycle_life"] = int(cycle_match.group(1).replace(",", ""))

    cap_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kWh|MWh)', text, re.IGNORECASE)
    if cap_match:
        val = float(cap_match.group(1))
        result["capacity_kwh"] = val if "kwh" in text[cap_match.start():cap_match.end()].lower() else val * 1000

    return result
