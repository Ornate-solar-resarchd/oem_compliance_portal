"""
BESS RFQ Technical Extraction Engine

Priority order:
1. Gemini API (free, powerful, 1M context) — if GEMINI_API_KEY is set
2. Claude API — if ANTHROPIC_API_KEY is set
3. Keyword extraction — always works, no API needed
"""
import os
import json
import re

# ─────────────────────────────────────────────────────────────────────
# STANDARD BESS TECHNICAL PARAMETERS (Based on NTPC REL 1000 MWh RFQ)
# This is the master checklist. AI will try to find values for ALL of these.
# ─────────────────────────────────────────────────────────────────────

STANDARD_PARAMETERS = {
    "BESS System": [
        {"code": "BESS_CAPACITY_MW", "parameter": "BESS Rated Power Capacity", "unit": "MW"},
        {"code": "BESS_CAPACITY_MWH", "parameter": "BESS Energy Capacity (Deliverable)", "unit": "MWh"},
        {"code": "BESS_NAMEPLATE_MWH", "parameter": "Min Nameplate Installed Capacity", "unit": "MWh"},
        {"code": "BESS_DISCHARGE_HRS", "parameter": "Discharge Duration", "unit": "hours"},
        {"code": "BESS_DESIGN_LIFE", "parameter": "Design Life", "unit": "years"},
        {"code": "CELL_CHEMISTRY", "parameter": "Battery Chemistry / Technology", "unit": ""},
        {"code": "BESS_COOLING", "parameter": "Cooling System Type", "unit": ""},
        {"code": "BESS_CONTAINERIZED", "parameter": "Containerized / Enclosure Type", "unit": ""},
        {"code": "BESS_GRID_KV", "parameter": "Grid Interconnection Voltage", "unit": "kV"},
        {"code": "BESS_SCOPE", "parameter": "Scope (EPC / Turnkey / Supply)", "unit": ""},
    ],
    "BESS Performance": [
        {"code": "CELL_ENERGY_EFF", "parameter": "Round-Trip Efficiency (RTE) AC-AC", "unit": "%"},
        {"code": "BESS_AVAILABILITY", "parameter": "Monthly System Availability", "unit": "%"},
        {"code": "BESS_PEAK_SUPPLY", "parameter": "Min Monthly Peak Supply Assurance", "unit": "%"},
        {"code": "BESS_HANDOVER_PCT", "parameter": "Dispatchable Capacity at Handover", "unit": "%"},
        {"code": "BESS_DEGRADATION", "parameter": "Guaranteed Capacity at End of Contract", "unit": "%"},
        {"code": "BESS_AUX_CONSUMPTION", "parameter": "Auxiliary Consumption Consideration", "unit": ""},
        {"code": "BESS_TRAFO_LOSS", "parameter": "Transformer Losses", "unit": "%"},
        {"code": "BESS_LINE_LOSS", "parameter": "Transmission Line Losses", "unit": "%"},
    ],
    "Cell / Battery Specs": [
        {"code": "CELL_CYCLE_LIFE", "parameter": "Minimum Rated Cycle Life", "unit": "cycles"},
        {"code": "CELL_CALENDAR_LIFE", "parameter": "Calendar Life", "unit": "years"},
        {"code": "CELL_CAPACITY_AH", "parameter": "Cell Nominal Capacity", "unit": "Ah"},
        {"code": "CELL_VOLTAGE_V", "parameter": "Cell Nominal Voltage", "unit": "V"},
        {"code": "CELL_ENERGY_DENSITY", "parameter": "Energy Density", "unit": "Wh/kg"},
        {"code": "CELL_SELF_DISCHARGE", "parameter": "Self Discharge Rate", "unit": "%/month"},
        {"code": "CELL_EOL_CAPACITY", "parameter": "End-of-Life Capacity Retention", "unit": "%"},
        {"code": "CELL_NEW_ONLY", "parameter": "New Cells Only (No Refurbished)", "unit": ""},
    ],
    "Certifications & Standards": [
        {"code": "CERT_IEC62619", "parameter": "IEC 62619 (Cell Safety)", "unit": ""},
        {"code": "CERT_UL1973", "parameter": "UL 1973 (Stationary Batteries)", "unit": ""},
        {"code": "CERT_UL9540", "parameter": "UL 9540 (ESS System Level)", "unit": ""},
        {"code": "CERT_UL9540A", "parameter": "UL 9540A (Thermal Runaway Test)", "unit": ""},
        {"code": "CERT_UN383", "parameter": "UN 38.3 (Transport Test)", "unit": ""},
        {"code": "CERT_IEC62933", "parameter": "IEC 62933 Series (ESS Standards)", "unit": ""},
        {"code": "CERT_IEC62477", "parameter": "IEC 62477 (Power Electronics)", "unit": ""},
        {"code": "CERT_IEC61000", "parameter": "IEC 61000 (EMC Compatibility)", "unit": ""},
        {"code": "CELL_BIS_CERT", "parameter": "BIS Registration / Certification", "unit": ""},
        {"code": "CERT_CEA_CERC", "parameter": "CEA / CERC / Indian Grid Code Compliance", "unit": ""},
        {"code": "CERT_IS_IEC_IEEE", "parameter": "IS / IEC / IEEE Standards Compliance", "unit": ""},
    ],
    "Fire Safety": [
        {"code": "FIRE_DETECTION", "parameter": "Fire Detection & Alarm System", "unit": ""},
        {"code": "FIRE_SUPPRESSION", "parameter": "Fire Suppression System", "unit": ""},
        {"code": "FIRE_CEA_NORMS", "parameter": "CEA / State Fire Safety Norms", "unit": ""},
        {"code": "FIRE_NFPA", "parameter": "NFPA Standards Compliance", "unit": ""},
    ],
    "EMS / SCADA": [
        {"code": "EMS_REQUIRED", "parameter": "Energy Management System Required", "unit": ""},
        {"code": "EMS_HYBRID", "parameter": "Hybrid EMS (Solar + BESS Control)", "unit": ""},
        {"code": "EMS_ORIGIN", "parameter": "EMS Software Origin (Indigenous / Make in India)", "unit": ""},
        {"code": "EMS_REFRESH", "parameter": "SCADA Data Refresh Rate", "unit": "seconds"},
        {"code": "EMS_AVAILABILITY", "parameter": "EMS System Availability", "unit": "%"},
        {"code": "EMS_PROTOCOL", "parameter": "Communication Protocols", "unit": ""},
        {"code": "EMS_CYBERSEC", "parameter": "Cyber Security Compliance", "unit": ""},
        {"code": "EMS_REDUNDANT", "parameter": "Redundant Server Configuration", "unit": ""},
        {"code": "EMS_SLDC", "parameter": "SLDC / RLDC Communication", "unit": ""},
        {"code": "EMS_MODES", "parameter": "Operation Modes (Grid Scheduling / Peak / Freq)", "unit": ""},
    ],
    "Grid Support Services": [
        {"code": "GRID_PFR", "parameter": "Primary Frequency Response (PFR)", "unit": ""},
        {"code": "GRID_SFR", "parameter": "Secondary Frequency Response (SFR)", "unit": ""},
        {"code": "GRID_TFR", "parameter": "Tertiary Frequency Response", "unit": ""},
        {"code": "GRID_INERTIA", "parameter": "Synthetic / Virtual Inertia", "unit": ""},
        {"code": "GRID_BLACK_START", "parameter": "Black Start Capability", "unit": ""},
        {"code": "GRID_REACTIVE", "parameter": "Reactive Power Compensation", "unit": ""},
        {"code": "GRID_POWER_QUALITY", "parameter": "Power Quality Compliance at POI", "unit": ""},
    ],
    "O&M / Warranty": [
        {"code": "OM_PERIOD", "parameter": "O&M / AMC Period", "unit": "years"},
        {"code": "OM_WARRANTY", "parameter": "Comprehensive Warranty Period", "unit": "years"},
        {"code": "OM_AUGMENTATION", "parameter": "Augmentation Included in Scope", "unit": ""},
        {"code": "OM_PERF_GUARANTEE", "parameter": "Performance / Energy Throughput Guarantee", "unit": ""},
        {"code": "OM_INSURANCE", "parameter": "Insurance Included", "unit": ""},
        {"code": "OM_TRAINING", "parameter": "Operator Training Required", "unit": ""},
    ],
    "Solar Integration": [
        {"code": "SOLAR_CAPACITY", "parameter": "Solar PV Capacity", "unit": "MWp"},
        {"code": "SOLAR_CUF", "parameter": "Annual Solar CUF Requirement", "unit": "%"},
        {"code": "SOLAR_CHARGING", "parameter": "BESS Charging Mode (Solar Only / Grid)", "unit": ""},
        {"code": "SOLAR_DISPATCH", "parameter": "Dispatch Schedule (SLDC / Peak Hours)", "unit": ""},
    ],
    "Commercial / Qualification": [
        {"code": "BID_SECURITY", "parameter": "Bid Security / EMD Amount", "unit": "INR"},
        {"code": "QUAL_EXPERIENCE", "parameter": "Min Experience Required (MWh)", "unit": "MWh"},
        {"code": "QUAL_TURNOVER", "parameter": "Min Annual Turnover Required", "unit": "INR"},
        {"code": "DELIVERY_TIMELINE", "parameter": "Project Delivery Timeline", "unit": "months"},
    ],
}


def _build_ai_prompt(document_text: str) -> str:
    """Build the AI prompt for extracting technical requirements."""
    all_params = []
    for section, params in STANDARD_PARAMETERS.items():
        all_params.append(f"\n[{section}]")
        for p in params:
            all_params.append(f"  - {p['code']}: {p['parameter']} ({p['unit']})" if p['unit'] else f"  - {p['code']}: {p['parameter']}")

    param_list = "\n".join(all_params)

    return f"""You are a BESS (Battery Energy Storage System) technical analyst expert.
Your job: Extract ALL technical requirements, specifications, and compliance criteria from this RFQ/tender document.

INSTRUCTIONS:
1. For EACH parameter below, find the value mentioned in the document
2. If a parameter is mentioned but no specific value is given, use "Required" or "Yes"
3. If not mentioned at all, SKIP it
4. Use ">=" prefix for minimum values (e.g., ">=80" for "minimum 80%")
5. Use "<=" prefix for maximum values (e.g., "<=1" for "within 1 second")
6. Also extract ANY additional technical parameters NOT in the list below

STANDARD PARAMETERS TO CHECK:
{param_list}

DOCUMENT TEXT:
{document_text[:30000]}

Return a JSON array of objects. Each object must have:
- "parameter": string (parameter name)
- "code": string (code from above, or new code like "CUSTOM_xxx" for additional params)
- "required_value": string (the extracted value)
- "unit": string (unit of measurement)
- "section": string (category)

Return ONLY the JSON array, no markdown, no explanation. Start with [ and end with ]."""


def extract_with_gemini(document_text: str, api_key: str) -> list:
    """Use Google Gemini API (FREE) to extract technical requirements."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = _build_ai_prompt(document_text)

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Clean markdown code blocks if present
        if response_text.startswith("```"):
            response_text = re.sub(r'^```(?:json)?\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)

        # Parse JSON
        if response_text.startswith("["):
            return json.loads(response_text)

        # Try to find JSON array in response
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            return json.loads(match.group())

    except Exception as e:
        print(f"Gemini extraction error: {e}")

    return []


def extract_with_claude(document_text: str, api_key: str) -> list:
    """Use Claude API to extract technical requirements (paid fallback)."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = _build_ai_prompt(document_text)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text.strip()
        if response_text.startswith("["):
            return json.loads(response_text)
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            return json.loads(match.group())

    except Exception as e:
        print(f"Claude extraction error: {e}")

    return []


def extract_from_text(document_text: str) -> list:
    """
    Extract technical requirements from document text.

    Priority:
    1. Gemini API (free, fast, 1M context) — if GEMINI_API_KEY is set
    2. Claude API (paid) — if ANTHROPIC_API_KEY is set
    3. Keyword extraction — always works, no API needed
    """

    # 1. Try Gemini first (FREE)
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key and gemini_key != "YOUR_GEMINI_KEY_HERE" and len(gemini_key) > 10:
        print("[RFQ Extraction] Using Gemini AI...")
        results = extract_with_gemini(document_text, gemini_key)
        if results:
            print(f"[RFQ Extraction] Gemini extracted {len(results)} requirements")
            return results
        print("[RFQ Extraction] Gemini failed, trying fallback...")

    # 2. Try Claude (paid)
    claude_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if claude_key and claude_key != "sk-placeholder" and len(claude_key) > 20:
        print("[RFQ Extraction] Using Claude AI...")
        results = extract_with_claude(document_text, claude_key)
        if results:
            print(f"[RFQ Extraction] Claude extracted {len(results)} requirements")
            return results
        print("[RFQ Extraction] Claude failed, trying fallback...")

    # 3. Keyword extraction (always works)
    print("[RFQ Extraction] Using keyword extraction...")
    results = _keyword_extraction(document_text)
    print(f"[RFQ Extraction] Keywords extracted {len(results)} requirements")
    return results


def _keyword_extraction(text: str) -> list:
    """Extract all technical requirements using keyword scanning."""
    text_lower = text.lower()
    extracted = []

    # ── BESS System ──
    _try_extract(extracted, text, text_lower, "BESS_CAPACITY_MW", "BESS Rated Power Capacity", "MW", "BESS System",
                 [r"(\d+)\s*MW\s*/", r"(\d+)\s*MW\b(?!\s*h)"])
    _try_extract(extracted, text, text_lower, "BESS_CAPACITY_MWH", "BESS Energy Capacity", "MWh", "BESS System",
                 [r"(\d+)\s*MWh"])
    _try_extract(extracted, text, text_lower, "BESS_NAMEPLATE_MWH", "Min Nameplate Capacity", "MWh", "BESS System",
                 [r"nameplate.*?(\d+)\s*MWh", r"min.*nameplate.*?(\d+)"])
    _try_extract(extracted, text, text_lower, "BESS_DISCHARGE_HRS", "Discharge Duration", "hours", "BESS System",
                 [r"(\d+)[\s-]*hour\s*discharge", r"single\s*cycle\s*(\d+)[\s-]*hour"])
    _try_extract(extracted, text, text_lower, "BESS_DESIGN_LIFE", "Design Life", "years", "BESS System",
                 [r"design\s*life.*?(\d+)\s*years", r"(\d+)\s*years.*design\s*life"], prefix=">=")
    _try_keyword(extracted, text_lower, "CELL_CHEMISTRY", "Battery Chemistry", "", "BESS System",
                 {"lfp": "LFP", "lithium iron phosphate": "LFP", "nmc": "NMC", "lithium": "Lithium-ion"})
    _try_keyword(extracted, text_lower, "BESS_COOLING", "Cooling System", "", "BESS System",
                 {"liquid cool": "Liquid Cooled", "air cool": "Air Cooled"})
    _try_extract(extracted, text, text_lower, "BESS_GRID_KV", "Grid Voltage Level", "kV", "BESS System",
                 [r"(\d+)\s*(?:kV|KV)"])
    if "turnkey" in text_lower or "epc" in text_lower:
        extracted.append({"parameter": "Scope", "code": "BESS_SCOPE", "required_value": "Turnkey EPC" if "turnkey" in text_lower else "EPC", "unit": "", "section": "BESS System"})

    # ── BESS Performance ──
    _try_extract(extracted, text, text_lower, "CELL_ENERGY_EFF", "Round-Trip Efficiency (RTE)", "%", "BESS Performance",
                 [r"(?:RTE|round[\s-]*trip[\s-]*efficiency).*?(\d+)\s*%", r"(\d+)\s*%.*?(?:RTE|round[\s-]*trip)"], prefix=">=")
    _try_extract(extracted, text, text_lower, "BESS_AVAILABILITY", "Monthly Availability", "%", "BESS Performance",
                 [r"(?:monthly\s*)?availability.*?(\d+(?:\.\d+)?)\s*%"], prefix=">=")
    _try_extract(extracted, text, text_lower, "BESS_PEAK_SUPPLY", "Min Monthly Peak Supply", "%", "BESS Performance",
                 [r"(\d+)\s*%.*?(?:peak|assured|dispatchable)"], prefix=">=")
    _try_extract(extracted, text, text_lower, "BESS_HANDOVER_PCT", "Dispatchable Capacity at Handover", "%", "BESS Performance",
                 [r"handover.*?(\d+)\s*%", r"(\d+)\s*%.*?handover"], prefix=">=")
    _try_extract(extracted, text, text_lower, "BESS_DEGRADATION", "Guaranteed Capacity End of Contract", "%", "BESS Performance",
                 [r"(\d+)\s*%.*?(?:dispatchable|degraded).*?(?:15|25)\s*year"])
    _try_extract(extracted, text, text_lower, "BESS_TRAFO_LOSS", "Transformer Losses", "%", "BESS Performance",
                 [r"(?:trafo|transformer)\s*loss.*?(\d+(?:\.\d+)?)\s*%"])
    _try_extract(extracted, text, text_lower, "BESS_LINE_LOSS", "Transmission Line Losses", "%", "BESS Performance",
                 [r"(?:transmission|line)\s*loss.*?(\d+(?:\.\d+)?)\s*%"])

    # ── Cell Specs ──
    _try_extract(extracted, text, text_lower, "CELL_CYCLE_LIFE", "Minimum Cycle Life", "cycles", "Cell Specs",
                 [r"(?:minimum|min|rated for).*?(\d[\d,]*)\s*cycles", r"(\d[\d,]*)\s*cycles"], prefix=">=")
    if "new" in text_lower and ("refurbished" in text_lower or "prohibit" in text_lower):
        extracted.append({"parameter": "New Cells Only (No Refurbished)", "code": "CELL_NEW_ONLY", "required_value": "Yes — Refurbished Prohibited", "unit": "", "section": "Cell Specs"})

    # ── Certifications (check ALL) ──
    cert_checks = [
        ("CERT_IEC62619", "IEC 62619 (Cell Safety)", ["iec 62619", "62619"]),
        ("CERT_UL1973", "UL 1973 (Stationary Batteries)", ["ul 1973", "ul1973"]),
        ("CERT_UL9540", "UL 9540 (ESS System)", ["ul 9540 ", "ul9540 "]),  # space to avoid 9540A
        ("CERT_UL9540A", "UL 9540A (Thermal Runaway Test)", ["ul 9540a", "9540a", "thermal runaway fire propagation"]),
        ("CERT_UN383", "UN 38.3 (Transport Test)", ["un 38.3", "un38.3"]),
        ("CERT_IEC62933", "IEC 62933 (ESS Standards)", ["iec 62933", "62933"]),
        ("CERT_IEC62477", "IEC 62477 (Power Electronics)", ["iec 62477", "62477"]),
        ("CERT_IEC61000", "IEC 61000 (EMC)", ["iec 61000", "61000"]),
        ("CELL_BIS_CERT", "BIS Registration", ["bis", "bureau of indian standards"]),
        ("CERT_CEA_CERC", "CEA / CERC / Grid Code Compliance", ["cea", "cerc", "indian grid code", "grid code"]),
    ]
    for code, param, keywords in cert_checks:
        for kw in keywords:
            if kw in text_lower:
                extracted.append({"parameter": param, "code": code, "required_value": "Required", "unit": "", "section": "Certifications"})
                break

    # ── Fire Safety ──
    if any(kw in text_lower for kw in ["fire detection", "fire alarm"]):
        extracted.append({"parameter": "Fire Detection & Alarm System", "code": "FIRE_DETECTION", "required_value": "Required", "unit": "", "section": "Fire Safety"})
    if any(kw in text_lower for kw in ["fire suppression", "fire protection"]):
        extracted.append({"parameter": "Fire Suppression System", "code": "FIRE_SUPPRESSION", "required_value": "Required", "unit": "", "section": "Fire Safety"})
    if "nfpa" in text_lower:
        extracted.append({"parameter": "NFPA Standards", "code": "FIRE_NFPA", "required_value": "Required", "unit": "", "section": "Fire Safety"})

    # ── EMS / SCADA ──
    if any(kw in text_lower for kw in ["energy management system", "ems", "scada"]):
        extracted.append({"parameter": "Energy Management System", "code": "EMS_REQUIRED", "required_value": "Required", "unit": "", "section": "EMS / SCADA"})
    if "hybrid ems" in text_lower or ("solar" in text_lower and "ems" in text_lower and "bess" in text_lower):
        extracted.append({"parameter": "Hybrid EMS (Solar + BESS)", "code": "EMS_HYBRID", "required_value": "Required", "unit": "", "section": "EMS / SCADA"})
    if "indigenous" in text_lower or "make in india" in text_lower:
        extracted.append({"parameter": "EMS Software — Indigenous / Make in India", "code": "EMS_ORIGIN", "required_value": "Mandatory — Developed in India", "unit": "", "section": "EMS / SCADA"})
    _try_extract(extracted, text, text_lower, "EMS_REFRESH", "SCADA Data Refresh Rate", "seconds", "EMS / SCADA",
                 [r"(?:refresh|data).*?(?:≤|<=)?\s*(\d+)\s*second"])
    _try_extract(extracted, text, text_lower, "EMS_AVAILABILITY", "EMS System Availability", "%", "EMS / SCADA",
                 [r"(?:system\s*)?availability.*?(\d+(?:\.\d+)?)\s*%"], prefix=">=")
    # Protocols
    protocols = []
    if "iec 61850" in text_lower: protocols.append("IEC 61850")
    if "modbus" in text_lower: protocols.append("Modbus TCP/IP")
    if "dnp3" in text_lower: protocols.append("DNP3")
    if protocols:
        extracted.append({"parameter": "Communication Protocols", "code": "EMS_PROTOCOL", "required_value": ", ".join(protocols), "unit": "", "section": "EMS / SCADA"})
    if any(kw in text_lower for kw in ["cyber security", "cybersecurity"]):
        extracted.append({"parameter": "Cyber Security Compliance", "code": "EMS_CYBERSEC", "required_value": "CEA / GoI Regulations", "unit": "", "section": "EMS / SCADA"})
    if any(kw in text_lower for kw in ["sldc", "rldc", "state load dispatch"]):
        extracted.append({"parameter": "SLDC / RLDC Communication", "code": "EMS_SLDC", "required_value": "Required", "unit": "", "section": "EMS / SCADA"})

    # ── Grid Support ──
    grid_checks = [
        ("GRID_PFR", "Primary Frequency Response (PFR)", ["primary frequency", "pfr"]),
        ("GRID_SFR", "Secondary Frequency Response (SFR)", ["secondary frequency", "sfr"]),
        ("GRID_TFR", "Tertiary Frequency Response", ["tertiary frequency"]),
        ("GRID_INERTIA", "Synthetic / Virtual Inertia", ["synthetic inertia", "virtual inertia"]),
        ("GRID_BLACK_START", "Black Start Capability", ["black start"]),
        ("GRID_REACTIVE", "Reactive Power Compensation", ["reactive power"]),
    ]
    for code, param, keywords in grid_checks:
        for kw in keywords:
            if kw in text_lower:
                extracted.append({"parameter": param, "code": code, "required_value": "Mandatory", "unit": "", "section": "Grid Support"})
                break

    # ── O&M / Warranty ──
    _try_extract(extracted, text, text_lower, "OM_PERIOD", "O&M / AMC Period", "years", "O&M / Warranty",
                 [r"O&M.*?(\d+)\s*years", r"(\d+)\s*years.*?(?:O&M|maintenance|AMC)"])
    _try_extract(extracted, text, text_lower, "OM_WARRANTY", "Comprehensive Warranty", "years", "O&M / Warranty",
                 [r"(?:comprehensive\s*)?warranty.*?(\d+)\s*years?", r"(\d+)\s*year.*?(?:comprehensive\s*)?warranty"])
    if "augmentation" in text_lower:
        extracted.append({"parameter": "Augmentation in Scope", "code": "OM_AUGMENTATION", "required_value": "Included in bidder scope", "unit": "", "section": "O&M / Warranty"})
    if any(kw in text_lower for kw in ["performance guarantee", "energy throughput warranty"]):
        extracted.append({"parameter": "Performance Guarantee", "code": "OM_PERF_GUARANTEE", "required_value": "Required for full design life", "unit": "", "section": "O&M / Warranty"})
    if "insurance" in text_lower:
        extracted.append({"parameter": "Insurance", "code": "OM_INSURANCE", "required_value": "Included in scope", "unit": "", "section": "O&M / Warranty"})
    if "training" in text_lower:
        extracted.append({"parameter": "Operator Training", "code": "OM_TRAINING", "required_value": "Required", "unit": "", "section": "O&M / Warranty"})

    # ── Solar Integration ──
    _try_extract(extracted, text, text_lower, "SOLAR_CAPACITY", "Solar PV Capacity", "MWp", "Solar Integration",
                 [r"(\d+)\s*MWp"])
    _try_extract(extracted, text, text_lower, "SOLAR_CUF", "Annual Solar CUF", "%", "Solar Integration",
                 [r"CUF.*?(\d+)\s*%", r"(\d+)\s*%.*CUF"], prefix=">=")
    if "solar" in text_lower and ("charg" in text_lower):
        extracted.append({"parameter": "BESS Charging via Solar", "code": "SOLAR_CHARGING", "required_value": "Solar power during daytime", "unit": "", "section": "Solar Integration"})
    if "sldc" in text_lower and "dispatch" in text_lower:
        extracted.append({"parameter": "Dispatch per SLDC Schedule", "code": "SOLAR_DISPATCH", "required_value": "As per SLDC instructions", "unit": "", "section": "Solar Integration"})

    # ── Commercial / Qualification ──
    _try_extract(extracted, text, text_lower, "BID_SECURITY", "Bid Security / EMD", "INR", "Commercial",
                 [r"(?:bid\s*security|EMD).*?INR\s*([\d,]+)", r"INR\s*([\d,]+).*?(?:bid\s*security|EMD)"])
    _try_extract(extracted, text, text_lower, "QUAL_EXPERIENCE", "Min BESS Experience", "MWh", "Commercial",
                 [r"(?:minimum|min).*?(\d+(?:\.\d+)?)\s*MWh.*?(?:experience|supplied|commissioned)"])
    _try_extract(extracted, text, text_lower, "QUAL_TURNOVER", "Min Annual Turnover", "INR Million", "Commercial",
                 [r"turnover.*?INR\s*([\d,]+)\s*Million", r"INR\s*([\d,]+)\s*Million.*?turnover"])

    return extracted


def _try_extract(results: list, text: str, text_lower: str, code: str, parameter: str, unit: str, section: str, patterns: list, prefix: str = ""):
    """Try regex patterns to extract a value. Add to results if found."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).replace(",", "")
            results.append({
                "parameter": parameter,
                "code": code,
                "required_value": f"{prefix}{val}" if prefix else val,
                "unit": unit,
                "section": section,
            })
            return


def _try_keyword(results: list, text_lower: str, code: str, parameter: str, unit: str, section: str, keyword_map: dict):
    """Check for keywords and map to values."""
    for keyword, value in keyword_map.items():
        if keyword in text_lower:
            results.append({
                "parameter": parameter,
                "code": code,
                "required_value": value,
                "unit": unit,
                "section": section,
            })
            return
