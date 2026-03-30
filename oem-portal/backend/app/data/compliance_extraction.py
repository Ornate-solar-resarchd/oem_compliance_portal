"""
Compliance Sheet Extraction Engine
Uses the 5 standard compliance templates (Battery, PCS, EMS, HVAC, Guarantees)
to extract RFQ requirements in the exact format needed for compliance sheets.
Uses Gemini (free) as primary, keyword fallback if unavailable.
ALL 344 parameters are always returned — marked as found/not found.
Case-insensitive matching throughout.
"""
import os
import json
import re
from pathlib import Path

# Load compliance templates
_TEMPLATE_PATH = Path(__file__).parent / "compliance_templates.json"
_TEMPLATES = {}
if _TEMPLATE_PATH.exists():
    with open(_TEMPLATE_PATH) as f:
        _TEMPLATES = json.load(f)


def get_all_template_parameters() -> list:
    """Return flat list of ALL 344 parameters across all compliance sheets."""
    params = []
    for category, info in _TEMPLATES.items():
        for sheet in info["sheets"]:
            for p in sheet["parameters"]:
                params.append({
                    **p,
                    "category": category,
                    "sheet_name": sheet["name"],
                })
    return params


def extract_compliance_from_rfq(document_text: str, categories: list = None) -> dict:
    """
    Extract compliance sheet data from an RFQ document.
    Returns ALL 344 parameters — each marked as found or not found.
    Case-insensitive matching.
    """
    if categories is None:
        categories = list(_TEMPLATES.keys())

    # Try Gemini first (free), then keyword fallback
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key and gemini_key != "sk-placeholder" and len(gemini_key) > 10:
        result = _extract_with_gemini(document_text, categories, gemini_key)
        if result:
            return result

    # Fallback to keyword extraction
    return _extract_with_keywords(document_text, categories)


def _extract_with_gemini(text: str, categories: list, api_key: str) -> dict:
    """Use Gemini to extract compliance data matching template parameters."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        results = {}
        for category in categories:
            if category not in _TEMPLATES:
                continue

            template_info = _TEMPLATES[category]
            all_params = []
            for sheet in template_info["sheets"]:
                for p in sheet["parameters"]:
                    all_params.append(f"- {p['code']}: {p['parameter']} (Template: {p['requirement']})")

            param_list = "\n".join(all_params)

            prompt = f"""You are a BESS compliance analyst. Extract values for ALL parameters below from this document.
Case-insensitive matching — "lfp" matches "LFP", "cycle life" matches "Cycle Life".

For EACH parameter:
- If found in document: set "found": true and extract the exact value
- If NOT found: set "found": false and use the template requirement as rfq_requirement

Return ALL {len(all_params)} parameters — do NOT skip any.

COMPLIANCE PARAMETERS FOR {category.upper()}:
{param_list}

DOCUMENT TEXT:
{text[:15000]}

Return ONLY a JSON array. Each item: {{"code":"...","parameter":"...","rfq_requirement":"...","section":"...","found":true/false}}"""

            response = model.generate_content(prompt)
            response_text = response.text.strip()

            if response_text.startswith("```"):
                response_text = re.sub(r'^```\w*\n?', '', response_text)
                response_text = re.sub(r'\n?```$', '', response_text)

            try:
                extracted = json.loads(response_text)

                # Ensure ALL template params are present
                extracted_codes = {p["code"] for p in extracted}
                for sheet in template_info["sheets"]:
                    for tp in sheet["parameters"]:
                        if tp["code"] not in extracted_codes:
                            extracted.append({
                                "code": tp["code"],
                                "parameter": tp["parameter"],
                                "rfq_requirement": tp["requirement"],
                                "section": tp.get("section", ""),
                                "found": False,
                            })

                results[category] = {
                    "sheets": [],
                    "total_found": sum(1 for p in extracted if p.get("found")),
                    "total_params": len(extracted),
                }

                for sheet in template_info["sheets"]:
                    sheet_codes = {p["code"].lower() for p in sheet["parameters"]}
                    sheet_params = [p for p in extracted if p["code"].lower() in sheet_codes]
                    results[category]["sheets"].append({
                        "name": sheet["name"],
                        "parameters": sheet_params,
                    })

            except json.JSONDecodeError:
                print(f"[Compliance] Failed to parse Gemini response for {category}")
                continue

        return results if results else None

    except Exception as e:
        print(f"[Compliance] Gemini extraction error: {e}")
        return None


def _extract_with_keywords(text: str, categories: list) -> dict:
    """Keyword-based fallback extraction. Case-insensitive. Returns ALL parameters."""
    text_lower = text.lower()
    results = {}

    for category in categories:
        if category not in _TEMPLATES:
            continue

        template_info = _TEMPLATES[category]
        results[category] = {"sheets": [], "total_found": 0, "total_params": 0}

        for sheet in template_info["sheets"]:
            sheet_params = []
            for p in sheet["parameters"]:
                param_name_lower = p["parameter"].lower()
                template_req = p["requirement"]

                # Try to find a value in the text (case-insensitive)
                found_value = _keyword_search(text, text_lower, param_name_lower, p["code"])

                sheet_params.append({
                    "code": p["code"],
                    "parameter": p["parameter"],
                    "rfq_requirement": found_value if found_value else template_req,
                    "section": p.get("section", ""),
                    "found": bool(found_value),
                })

                if found_value:
                    results[category]["total_found"] += 1
                results[category]["total_params"] += 1

            results[category]["sheets"].append({
                "name": sheet["name"],
                "parameters": sheet_params,
            })

    return results


def _keyword_search(text: str, text_lower: str, param_name_lower: str, code: str) -> str:
    """Search for a parameter value in text using keywords. Case-insensitive."""

    # Numeric patterns (case-insensitive via re.IGNORECASE)
    patterns = {
        "nominal voltage": [r"(\d+\.?\d*)\s*V\b"],
        "rated capacity": [r"(\d+)\s*Ah\b", r"capacity.*?(\d+)\s*Ah"],
        "energy density": [r"(\d+\.?\d*)\s*Wh/kg", r"(\d+\.?\d*)\s*wh/kg"],
        "volumetric energy density": [r"(\d+\.?\d*)\s*Wh/L", r"(\d+\.?\d*)\s*wh/l"],
        "cycle life": [r"[≥>=]*\s*(\d[\d,]*)\s*cycles", r"cycle\s*life.*?(\d[\d,]*)"],
        "calendar life": [r"(\d+)\s*years?\s*calendar", r"calendar.*?(\d+)\s*year"],
        "design life": [r"design\s*life.*?(\d+)\s*year", r"[≥>=]*\s*(\d+)\s*year.*?design"],
        "operating temperature": [r"(-?\d+)\s*°?\s*C?\s*to\s*(-?\d+)\s*°?\s*C"],
        "charge rate": [r"[≥>=]*\s*(\d+\.?\d*)\s*C\b.*?charge", r"charge.*?(\d+\.?\d*)\s*C"],
        "discharge rate": [r"[≥>=]*\s*(\d+\.?\d*)\s*C\b.*?discharge", r"discharge.*?(\d+\.?\d*)\s*C"],
        "c-rate": [r"(\d+\.?\d*)\s*C\b"],
        "self.discharge": [r"(\d+\.?\d*)\s*%\s*/?\s*month"],
        "round.trip efficiency": [r"[≥>=]*\s*(\d+\.?\d*)\s*%.*?(?:rte|efficiency|round)"],
        "rte": [r"[≥>=]*\s*(\d+\.?\d*)\s*%.*?(?:rte|round.trip)"],
        "efficiency": [r"efficiency.*?[≥>=]*\s*(\d+\.?\d*)\s*%", r"[≥>=]*\s*(\d+\.?\d*)\s*%.*?efficiency"],
        "availability": [r"availability.*?[≥>=]*\s*(\d+\.?\d*)\s*%", r"[≥>=]*\s*(\d+\.?\d*)\s*%.*?availability"],
        "ip rating": [r"IP\s*(\d{2})", r"ip\s*(\d{2})"],
        "rated power": [r"(\d+)\s*(?:MW|kW)", r"rated\s*power.*?(\d+)"],
        "rated energy": [r"(\d+)\s*MWh", r"(\d+)\s*mwh"],
        "discharge duration": [r"(\d+)\s*hour", r"(\d+)\s*hr"],
        "thd": [r"THD.*?<?[≤<=]*\s*(\d+\.?\d*)\s*%", r"thd.*?(\d+\.?\d*)\s*%"],
        "frequency": [r"(\d+\.?\d*)\s*Hz", r"(\d+\.?\d*)\s*hz"],
        "power factor": [r"power\s*factor.*?(\d+\.?\d*)", r"[≥>=]*\s*(\d+\.?\d*).*?power\s*factor"],
        "communication protocol": [r"(Modbus|IEC\s*61850|CAN|RS485|DNP3|modbus|iec\s*61850)"],
        "weight": [r"(\d+\.?\d*)\s*kg", r"weight.*?(\d+\.?\d*)"],
        "dimension": [r"(\d+)\s*[×xX]\s*(\d+)\s*[×xX]\s*(\d+)\s*mm"],
        "internal resistance": [r"(\d+\.?\d*)\s*m[Ωω]", r"internal\s*resist.*?(\d+\.?\d*)"],
        "cooling capacity": [r"(\d+\.?\d*)\s*kW.*?cool", r"cool.*?(\d+\.?\d*)\s*kW"],
        "noise level": [r"(\d+\.?\d*)\s*dB"],
        "altitude": [r"(\d[\d,]*)\s*m.*?altitude", r"altitude.*?(\d[\d,]*)\s*m"],
        "humidity": [r"(\d+)\s*%.*?humidity", r"humidity.*?(\d+)\s*%"],
        "cells per module": [r"(\d+)\s*cells?\s*per\s*module"],
        "modules per rack": [r"(\d+)\s*modules?\s*per\s*rack"],
        "dc voltage": [r"(\d+)\s*V\s*DC", r"DC\s*voltage.*?(\d+)"],
        "ac voltage": [r"(\d+)\s*V\s*AC", r"AC\s*voltage.*?(\d+)"],
        "response time": [r"(\d+)\s*ms.*?response", r"response.*?(\d+)\s*ms"],
        "data refresh": [r"[≤<=]*\s*(\d+)\s*s(?:ec)?.*?refresh", r"refresh.*?(\d+)\s*s"],
        "warranty": [r"warranty.*?(\d+)\s*year", r"(\d+)\s*year.*?warranty"],
        "degradation": [r"(\d+\.?\d*)\s*%.*?(?:degradation|fade)", r"(?:degradation|fade).*?(\d+\.?\d*)\s*%"],
        "dod": [r"[≥>=]*\s*(\d+)\s*%.*?(?:dod|depth)", r"(?:dod|depth).*?(\d+)\s*%"],
        "soc": [r"soc.*?(\d+)\s*%\s*to\s*(\d+)\s*%"],
        "augmentation": [r"(augmentation)"],
        "capacity retention": [r"[≥>=]*\s*(\d+)\s*%.*?(?:retention|remaining|eol)"],
    }

    for key, regexes in patterns.items():
        if key in param_name_lower:
            for regex in regexes:
                try:
                    match = re.search(regex, text, re.IGNORECASE)
                    if match and match.groups():
                        groups = match.groups()
                        if len(groups) == 3:  # dimensions
                            return f"{groups[0]} × {groups[1]} × {groups[2]} mm"
                        if len(groups) == 2:
                            return f"{groups[0]} to {groups[1]}"
                        if len(groups) >= 1 and groups[0]:
                            val = groups[0].replace(",", "")
                            return val
                except Exception:
                    continue

    # Check for specific certifications (case-insensitive)
    cert_keywords = {
        "iec 62619": "IEC 62619",
        "ul 1973": "UL 1973",
        "ul 9540a": "UL 9540A",
        "ul 9540": "UL 9540",
        "un 38.3": "UN 38.3",
        "un38.3": "UN 38.3",
        "iso 9001": "ISO 9001",
        "iso 14001": "ISO 14001",
        "iso 45001": "ISO 45001",
        "iec 61850": "IEC 61850",
        "iec 62933": "IEC 62933",
        "iec 61000": "IEC 61000",
        "nfpa": "NFPA",
        "bis": "BIS Certified",
        "cea": "CEA Compliant",
        "cerc": "CERC Compliant",
        "modbus": "Modbus TCP/IP",
        "dnp3": "DNP3",
        "can bus": "CAN Bus",
        "rs485": "RS485",
    }

    for cert_key, cert_val in cert_keywords.items():
        if cert_key in param_name_lower and cert_key in text_lower:
            return f"Required — {cert_val}"

    # Check for specific technology keywords (case-insensitive)
    tech_keywords = {
        "lfp": "LFP",
        "lithium iron phosphate": "LFP (Lithium Iron Phosphate)",
        "nmc": "NMC",
        "prismatic": "Prismatic",
        "cylindrical": "Cylindrical",
        "pouch": "Pouch",
        "liquid cool": "Liquid Cooling",
        "air cool": "Air Cooling",
        "active balance": "Active Balancing",
        "passive balance": "Passive Balancing",
        "aerosol": "Aerosol Suppression",
        "water sprinkler": "Water Sprinkler",
        "novec": "Novec 1230",
        "fm200": "FM200",
        "black start": "Black Start Capable",
        "grid forming": "Grid-Forming",
        "grid following": "Grid-Following",
    }

    for tech_key, tech_val in tech_keywords.items():
        if tech_key in param_name_lower and tech_key in text_lower:
            return tech_val

    # Generic "required/mandatory" check (case-insensitive)
    # Check if the parameter topic appears near "required", "mandatory", "shall", "must"
    param_words = [w for w in param_name_lower.split() if len(w) > 3]
    required_words = ["required", "mandatory", "shall", "must", "minimum", "≥", ">="]

    for pw in param_words:
        if pw in text_lower:
            # Find all positions of this word
            start = 0
            while True:
                idx = text_lower.find(pw, start)
                if idx < 0:
                    break
                context = text_lower[max(0, idx - 150):idx + 150]
                for rw in required_words:
                    if rw in context:
                        # Try to extract a nearby number
                        num_match = re.search(r'[≥>=]*\s*(\d+\.?\d*)\s*(%|MW|MWh|kW|kWh|V|A|Ah|°C|years?|cycles?|kg|mm|m|Hz|dB|kW|mΩ)', context)
                        if num_match:
                            return f"≥{num_match.group(1)} {num_match.group(2)}"
                        return "Required"
                start = idx + 1

    return ""
