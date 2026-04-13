"""
BESS RFQ Technical Extraction Engine
Uses comprehensive keyword/regex pattern matching against STANDARD_PARAMETERS.
No AI API dependency — works offline with deterministic results.
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
- "page": number or null (approximate page number where this was found, if determinable from context)
- "source_text": string (the exact sentence or phrase from the document where this value was found, max 100 chars)

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
            model="claude-haiku-4-5-20251001",
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


def extract_from_text(document_text: str, pages: list = None) -> list:
    """
    Extract technical requirements from document text using keyword matching.
    Uses comprehensive regex patterns against STANDARD_PARAMETERS — no AI needed.
    """
    print("[RFQ Extraction] Using keyword extraction engine...")
    results = _keyword_extraction(document_text)
    print(f"[RFQ Extraction] Extracted {len(results)} requirements from {len(document_text)} chars")
    return results


def _keyword_extraction(text: str) -> list:
    """Extract all technical requirements using keyword scanning."""
    text_lower = text.lower()
    extracted = []

    # ── BESS System ──
    _try_extract(extracted, text, text_lower, "BESS_CAPACITY_MW", "BESS Rated Power Capacity", "MW", "BESS System",
                 [r"(\d[\d,]+)\s*MW\s*/", r"(\d[\d,]+)\s*MW\b(?!\s*h)"])
    # MWh — prefer MW/MWh format first (most precise), then BESS context
    _try_extract(extracted, text, text_lower, "BESS_CAPACITY_MWH", "BESS Energy Capacity", "MWh", "BESS System",
                 [r"MW\s*/\s*(\d[\d,.]+)\s*MWh",
                  r"(\d[\d,]+)\s*MWh\s*(?:BESS|ESS|storage|battery)",
                  r"(?:BESS|ESS|storage|battery)\s*(?:project|system|plant|capacity).*?(\d[\d,]+)\s*MWh"])
    _try_extract(extracted, text, text_lower, "BESS_NAMEPLATE_MWH", "Min Nameplate Capacity", "MWh", "BESS System",
                 [r"(?:nameplate|installed|gross|initial|day[\s-]*one|day\s*1|BOL)\s*(?:capacity|energy|rating)?.*?(\d[\d,]*)\s*MWh",
                  r"min.*?(?:nameplate|installed).*?(\d[\d,]*)\s*MWh"])
    _try_extract(extracted, text, text_lower, "BESS_DISCHARGE_HRS", "Discharge Duration", "hours", "BESS System",
                 [r"(\d+(?:\.\d+)?)[\s-]*(?:hour|hr|h)\s*(?:discharge|duration|storage|backup)",
                  r"(?:discharge|duration|storage)\s*(?:duration|time|of)?.*?(\d+(?:\.\d+)?)\s*(?:hour|hr|h)\b",
                  r"single\s*cycle\s*(\d+)[\s-]*hour",
                  r"(\d+)[\s-]*(?:hour|hr|h)\s*BESS"])
    _try_extract(extracted, text, text_lower, "BESS_DESIGN_LIFE", "Design Life", "years", "BESS System",
                 [r"(?:design|service|operational|useful|expected|project|plant|system|asset|economic)\s*life.*?(\d+)\s*years?",
                  r"(\d+)\s*years?\s*(?:design|service|operational|useful|expected|project|plant|system)\s*life",
                  r"life\s*(?:of|expectancy).*?(\d+)\s*years?"], prefix=">=")
    _try_keyword(extracted, text_lower, "CELL_CHEMISTRY", "Battery Chemistry", "", "BESS System",
                 {"lfp": "LFP", "lifepo4": "LFP", "lithium iron phosphate": "LFP",
                  "li-fepo4": "LFP", "iron phosphate": "LFP",
                  "nmc": "NMC", "nickel manganese cobalt": "NMC",
                  "lto": "LTO", "lithium titanate": "LTO",
                  "sodium-ion": "Sodium-ion", "sodium ion": "Sodium-ion",
                  "lithium-ion": "Lithium-ion", "lithium ion": "Lithium-ion", "li-ion": "Lithium-ion",
                  "lithium": "Lithium-ion"})
    _try_keyword(extracted, text_lower, "BESS_COOLING", "Cooling System", "", "BESS System",
                 {"liquid cool": "Liquid Cooled", "liquid-cool": "Liquid Cooled", "water cool": "Liquid Cooled",
                  "glycol cool": "Liquid Cooled", "immersion cool": "Immersion Cooled",
                  "air cool": "Air Cooled", "air-cool": "Air Cooled", "forced air": "Forced Air Cooled",
                  "hvac": "HVAC Cooled"})
    _try_extract(extracted, text, text_lower, "BESS_GRID_KV", "Grid Voltage Level", "kV", "BESS System",
                 [r"(?:grid|interconnection|POI|point\s*of\s*interconnection|HV|MV|evacuation|transmission)\s*(?:level|voltage)?.*?(\d+)\s*(?:kV|KV)",
                  r"(\d+)\s*(?:kV|KV)\s*(?:grid|interconnection|level|line|substation|busbar)"])
    if any(kw in text_lower for kw in ["turnkey", "engineering procurement construction", "engineering, procurement"]):
        extracted.append({"parameter": "Scope", "code": "BESS_SCOPE", "required_value": "Turnkey EPC", "unit": "", "section": "BESS System"})
    elif any(kw in text_lower for kw in ["epc", "epcm", "design build", "design-build", "supply install commission"]):
        extracted.append({"parameter": "Scope", "code": "BESS_SCOPE", "required_value": "EPC", "unit": "", "section": "BESS System"})

    # ── BESS Performance ──
    _try_extract(extracted, text, text_lower, "CELL_ENERGY_EFF", "Round-Trip Efficiency (RTE)", "%", "BESS Performance",
                 [r"(?:round[\s-]*trip|roundtrip|AC[\s-]*to[\s-]*AC|DC[\s-]*to[\s-]*DC|energy|cycle|system)\s*efficiency.*?[≥>=]*\s*((?:8|9)\d(?:\.\d+)?)\s*%",
                  r"RTE.*?[≥>=]*\s*((?:8|9)\d(?:\.\d+)?)\s*%",
                  r"η.*?[≥>=]*\s*((?:8|9)\d(?:\.\d+)?)\s*%"], prefix=">=")
    _try_extract(extracted, text, text_lower, "BESS_AVAILABILITY", "Monthly Availability", "%", "BESS Performance",
                 [r"(?:monthly|annual|system|plant|guaranteed|minimum|min)\s*availability.*?(\d+(?:\.\d+)?)\s*%",
                  r"availability\s*(?:factor|guarantee|target)?.*?[≥>=]*\s*(\d+(?:\.\d+)?)\s*%",
                  r"uptime.*?[≥>=]*\s*(\d+(?:\.\d+)?)\s*%"], prefix=">=")
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

    # ── Cell / Battery Specs ──
    _try_extract(extracted, text, text_lower, "CELL_CYCLE_LIFE", "Minimum Cycle Life", "cycles", "Cell Specs",
                 [r"(?:cycle\s*life|equivalent\s*full\s*cycles?|EFC|life\s*cycles?|charge[\s-]*discharge\s*cycles?).*?(\d[\d,]{3,})",
                  r"(?:minimum|min|guaranteed|rated\s*for|at\s*least).*?(\d[\d,]{3,})\s*cycles?",
                  r"(\d{4,})\s*(?:cycles?|EFC)"], prefix=">=")
    _try_extract(extracted, text, text_lower, "CELL_CAPACITY_AH", "Cell Nominal Capacity", "Ah", "Cell Specs",
                 [r"(?:cell\s*)?(?:nominal|rated|typical|minimum)\s*capacity.*?(\d+(?:\.\d+)?)\s*Ah",
                  r"(\d+(?:\.\d+)?)\s*Ah\s*(?:cell|capacity|nominal|rated)",
                  r"capacity\s*(?:of|=)?\s*(\d+(?:\.\d+)?)\s*Ah"])
    _try_extract(extracted, text, text_lower, "CELL_VOLTAGE_V", "Cell Nominal Voltage", "V", "Cell Specs",
                 [r"cell\s*(?:nominal\s*)?voltage.*?(\d+(?:\.\d+)?)\s*V\b",
                  r"(?:nominal\s*)?voltage.*?(\d+(?:\.\d+)?)\s*V\b.*?cell",
                  r"(\d\.\d+)\s*V\s*(?:and|,)\s*\d+\s*Ah"])
    _try_extract(extracted, text, text_lower, "CELL_DOD", "Depth of Discharge (DOD)", "%", "Cell Specs",
                 [r"(?:DOD|depth[\s-]*of[\s-]*discharge|usable\s*capacity|usable\s*DOD).*?(\d+)\s*%",
                  r"(\d+)\s*%\s*(?:DOD|depth)"])
    # SOC range needs special handling - capture both min and max
    soc_match = re.search(r"SOC.*?(\d+)\s*%?\s*(?:to|–|-|~)\s*(\d+)\s*%", text, re.IGNORECASE)
    if soc_match:
        extracted.append({"parameter": "SOC Operating Range", "code": "CELL_SOC_RANGE",
                         "required_value": f"{soc_match.group(1)}% to {soc_match.group(2)}%",
                         "unit": "%", "section": "Cell Specs"})
    _try_extract(extracted, text, text_lower, "CELL_CALENDAR_LIFE", "Calendar Life", "years", "Cell Specs",
                 [r"(?:calendar|shelf|storage|float)\s*life.*?(\d+)\s*years?",
                  r"(\d+)\s*years?.*?(?:calendar|shelf|float)\s*life"])
    _try_extract(extracted, text, text_lower, "CELL_ENERGY_DENSITY", "Energy Density", "Wh/kg", "Cell Specs",
                 [r"energy\s*density.*?(\d+(?:\.\d+)?)\s*Wh/kg"])
    _try_extract(extracted, text, text_lower, "CELL_SELF_DISCHARGE", "Self Discharge Rate", "%/month", "Cell Specs",
                 [r"self[\s-]*discharge.*?(\d+(?:\.\d+)?)\s*%"])
    _try_extract(extracted, text, text_lower, "CELL_EOL_RETENTION", "End-of-Life Capacity Retention", "%", "Cell Specs",
                 [r"(?:EOL|end[\s-]*of[\s-]*life|end[\s-]*of[\s-]*warranty|EOW|end[\s-]*of[\s-]*contract|EOC|state[\s-]*of[\s-]*health|SOH).*?(?:capacity|retention|residual)?.*?(\d+(?:\.\d+)?)\s*%",
                  r"(\d+(?:\.\d+)?)\s*%.*?(?:EOL|end[\s-]*of[\s-]*life|SOH|residual\s*capacity)",
                  r"(?:guaranteed|minimum|min)\s*(?:residual|remaining)\s*capacity.*?(\d+(?:\.\d+)?)\s*%"])
    _try_extract(extracted, text, text_lower, "CELL_C_RATE", "C-Rate", "C", "Cell Specs",
                 [r"(?:c[\s-]*rate|charge[\s-]*rate).*?(\d+(?:\.\d+)?)\s*C"])
    _try_extract(extracted, text, text_lower, "CELL_INTERNAL_RES", "Internal Resistance", "mΩ", "Cell Specs",
                 [r"internal\s*resistance.*?(\d+(?:\.\d+)?)\s*(?:mΩ|mohm|m[oO]hm)"])
    _try_extract(extracted, text, text_lower, "CELL_AVAILABILITY", "Cell-Level Availability", "%", "Cell Specs",
                 [r"cell[\s-]*(?:level\s*)?availability.*?(\d+(?:\.\d+)?)\s*%"], prefix=">=")
    if "new" in text_lower and ("refurbished" in text_lower or "prohibit" in text_lower):
        extracted.append({"parameter": "New Cells Only (No Refurbished)", "code": "CELL_NEW_ONLY", "required_value": "Yes — Refurbished Prohibited", "unit": "", "section": "Cell Specs"})
    _try_keyword(extracted, text_lower, "CELL_FORMAT", "Cell Form Factor", "", "Cell Specs",
                 {"prismatic": "Prismatic", "cylindrical": "Cylindrical", "pouch": "Pouch", "blade": "Blade"})

    # ── DC Block / Container Specs ──
    _try_extract(extracted, text, text_lower, "DC_VOLTAGE_NOM", "DC Bus Voltage (Nominal)", "V", "DC Block",
                 [r"(?:dc\s*bus|battery\s*bus|nominal\s*dc).*?voltage.*?(\d+(?:\.\d+)?)\s*V",
                  r"(?:dc|system)\s*voltage.*?(\d+)\s*V"])
    _try_extract(extracted, text, text_lower, "DC_VOLTAGE_MAX", "DC Voltage Max", "V", "DC Block",
                 [r"(?:max|maximum)\s*(?:dc\s*)?(?:system\s*)?voltage.*?(\d+(?:\.\d+)?)\s*V"])
    _try_extract(extracted, text, text_lower, "DC_VOLTAGE_MIN", "DC Voltage Min", "V", "DC Block",
                 [r"(?:min|minimum)\s*(?:dc\s*)?(?:system\s*)?voltage.*?(\d+(?:\.\d+)?)\s*V"])
    _try_extract(extracted, text, text_lower, "DC_CONTAINER_COUNT", "Number of BESS Containers", "", "DC Block",
                 [r"(\d+)\s*(?:BESS\s*)?container"])
    _try_keyword(extracted, text_lower, "DC_CONTAINER_TYPE", "Container Type", "", "DC Block",
                 {"20ft": "20ft ISO", "20 ft": "20ft ISO", "40ft": "40ft ISO", "40 ft": "40ft ISO",
                  "high cube": "High-Cube", "high-cube": "High-Cube"})
    _try_extract(extracted, text, text_lower, "DC_IP_RATING", "Protection Rating (IP)", "", "DC Block",
                 [r"(IP\s*\d{2}\w?)"])
    _try_extract(extracted, text, text_lower, "DC_NOISE", "Noise Level", "dBA", "DC Block",
                 [r"(?:noise|sound).*?(?:≤|<=|less\s*than)?\s*(\d+)\s*dB"])
    if any(kw in text_lower for kw in ["thermal runaway", "tr propagation"]):
        extracted.append({"parameter": "Thermal Runaway Protection", "code": "DC_TR_PROTECT", "required_value": "Required", "unit": "", "section": "DC Block"})
    if any(kw in text_lower for kw in ["explosion proof", "explosion-proof", "deflagration vent"]):
        extracted.append({"parameter": "Explosion-Proof Vent / Deflagration Panel", "code": "DC_EXPLOSION_VENT", "required_value": "Required", "unit": "", "section": "DC Block"})
    if any(kw in text_lower for kw in ["vesda", "very early smoke"]):
        extracted.append({"parameter": "VESDA Smoke Detection", "code": "DC_VESDA", "required_value": "Required", "unit": "", "section": "DC Block"})
    _try_keyword(extracted, text_lower, "DC_FIRE_AGENT", "Fire Suppression Agent", "", "DC Block",
                 {"novec 1230": "Novec 1230", "novec": "Novec 1230", "fm200": "FM200", "fm-200": "FM200",
                  "aerosol": "Aerosol", "water mist": "Water Mist", "water sprinkler": "Water Sprinkler"})
    if any(kw in text_lower for kw in ["h2 detect", "hydrogen detect", "h₂"]):
        extracted.append({"parameter": "H₂ Gas Detection", "code": "DC_H2_DETECT", "required_value": "Required", "unit": "", "section": "DC Block"})
    if any(kw in text_lower for kw in ["co detect", "carbon monoxide"]):
        extracted.append({"parameter": "CO Gas Detection", "code": "DC_CO_DETECT", "required_value": "Required", "unit": "", "section": "DC Block"})
    _try_keyword(extracted, text_lower, "DC_BMS_ARCH", "BMS Architecture", "", "DC Block",
                 {"3-tier": "3-Tier", "3 tier": "3-Tier", "three-tier": "3-Tier", "2-tier": "2-Tier"})

    # ── PCS Specs ──
    _try_extract(extracted, text, text_lower, "PCS_RATED_POWER", "PCS Rated AC Power", "kW", "PCS",
                 [r"PCS.*?(?:rated|nominal)\s*(?:ac\s*)?(?:power|output).*?(\d+(?:\.\d+)?)\s*(?:MW|kW)",
                  r"(?:rated|nominal)\s*(?:ac\s*)?power.*?PCS.*?(\d+(?:\.\d+)?)\s*(?:MW|kW)"])
    _try_extract(extracted, text, text_lower, "PCS_EFFICIENCY", "PCS Peak Conversion Efficiency", "%", "PCS",
                 [r"PCS\s*(?:conversion\s*)?efficiency.*?(\d+(?:\.\d+)?)\s*%",
                  r"(?:peak|max)\s*(?:conversion\s*)?efficiency.*?(\d+(?:\.\d+)?)\s*%"], prefix=">=")
    _try_extract(extracted, text, text_lower, "PCS_WEIGHTED_EFF", "PCS Weighted / CEC Efficiency", "%", "PCS",
                 [r"(?:weighted|CEC|euro)\s*efficiency.*?(\d+(?:\.\d+)?)\s*%"], prefix=">=")
    _try_extract(extracted, text, text_lower, "PCS_THD", "PCS THD at Rated Output", "%", "PCS",
                 [r"THD.*?[<≤<=]?\s*(\d+(?:\.\d+)?)\s*%"])
    _try_extract(extracted, text, text_lower, "PCS_POWER_FACTOR", "PCS Power Factor Range", "", "PCS",
                 [r"power\s*factor.*?(\d+(?:\.\d+)?)\s*(?:lead|lag|leading|lagging)"])
    _try_extract(extracted, text, text_lower, "PCS_RESPONSE_TIME", "PCS Response Time (0 to Full Power)", "ms", "PCS",
                 [r"(?:response\s*time|0\s*to\s*full).*?[<≤<=]?\s*(\d+)\s*(?:ms|milli)"])
    _try_extract(extracted, text, text_lower, "PCS_RAMP_RATE", "PCS Ramp Rate", "MW/s", "PCS",
                 [r"ramp\s*rate.*?(\d+(?:\.\d+)?)\s*(?:MW/s|%/s|kW/s)"])
    _try_extract(extracted, text, text_lower, "PCS_OVERLOAD", "PCS Overload Capability", "%", "PCS",
                 [r"overload.*?(\d+)\s*%.*?(\d+)\s*(?:min|sec|s\b)"])
    _try_extract(extracted, text, text_lower, "PCS_DC_INJECTION", "PCS DC Injection Limit", "%", "PCS",
                 [r"DC\s*injection.*?(\d+(?:\.\d+)?)\s*%"])
    _try_extract(extracted, text, text_lower, "PCS_AC_VOLTAGE", "PCS AC Voltage", "kV", "PCS",
                 [r"(?:ac|output)\s*(?:side\s*)?(?:interconnection\s*)?voltage.*?(\d+(?:\.\d+)?)\s*kV"])
    _try_extract(extracted, text, text_lower, "PCS_FREQ_RANGE", "PCS Operational Frequency Range", "Hz", "PCS",
                 [r"(?:frequency|freq)\s*range.*?(\d+(?:\.\d+)?)\s*Hz\s*(?:to|–|-)\s*(\d+(?:\.\d+)?)\s*Hz"])
    _try_extract(extracted, text, text_lower, "PCS_REACTIVE_KVAR", "PCS Reactive Power Capability", "kVAr", "PCS",
                 [r"reactive\s*(?:power)?\s*(?:capability|capacity).*?(\d+(?:\.\d+)?)\s*(?:kVAr|MVAr)"])
    _try_extract(extracted, text, text_lower, "PCS_UPTIME", "PCS Uptime Guarantee", "%", "PCS",
                 [r"(?:PCS|inverter)\s*(?:uptime|availability).*?(\d+(?:\.\d+)?)\s*%"], prefix=">=")
    _try_extract(extracted, text, text_lower, "PCS_AUX_CONSUMPTION", "PCS Auxiliary Consumption", "%", "PCS",
                 [r"(?:aux|auxiliary)\s*(?:power\s*)?consumption.*?(?:less\s*than|[<≤<=])\s*(\d+(?:\.\d+)?)\s*%",
                  r"(?:aux|auxiliary)\s*consumption\s*(?:shall\s*)?(?:not\s*)?(?:exceed\s*)?(\d+(?:\.\d+)?)\s*%"])
    _try_extract(extracted, text, text_lower, "PCS_UNITS_COUNT", "Number of PCS Units", "", "PCS",
                 [r"(\d+)\s*(?:PCS\s*)?(?:units|inverter)"])
    _try_keyword(extracted, text_lower, "PCS_TOPOLOGY", "PCS Topology", "", "PCS",
                 {"central": "Central", "string": "String", "npc": "NPC", "3-level": "3-Level",
                  "h-bridge": "H-Bridge", "t-type": "T-Type"})
    _try_keyword(extracted, text_lower, "PCS_COOLING", "PCS Cooling Type", "", "PCS",
                 {"liquid cool": "Liquid Cooled", "air cool": "Air Cooled", "forced air": "Forced Air"})
    if any(kw in text_lower for kw in ["lvrt", "low voltage ride"]):
        extracted.append({"parameter": "LVRT (Low Voltage Ride Through)", "code": "PCS_LVRT", "required_value": "Required per CEA Grid Code", "unit": "", "section": "PCS"})
    if any(kw in text_lower for kw in ["hvrt", "high voltage ride"]):
        extracted.append({"parameter": "HVRT (High Voltage Ride Through)", "code": "PCS_HVRT", "required_value": "Required", "unit": "", "section": "PCS"})
    if "anti-island" in text_lower or "anti island" in text_lower:
        extracted.append({"parameter": "Anti-Islanding Protection", "code": "PCS_ANTI_ISLAND", "required_value": "Required per IEEE 1547 / CEA", "unit": "", "section": "PCS"})
    if "grid forming" in text_lower or "grid-forming" in text_lower:
        extracted.append({"parameter": "Grid-Forming Capability", "code": "PCS_GRID_FORMING", "required_value": "Required", "unit": "", "section": "PCS"})
    if any(kw in text_lower for kw in ["droop control", "frequency droop"]):
        extracted.append({"parameter": "Frequency Droop Control", "code": "PCS_DROOP", "required_value": "Required — configurable", "unit": "", "section": "PCS"})
    if any(kw in text_lower for kw in ["avr", "voltage regulation", "voltage regulator"]):
        extracted.append({"parameter": "Voltage Regulation / AVR Mode", "code": "PCS_AVR", "required_value": "Required", "unit": "", "section": "PCS"})
    # PCS Transformer
    _try_extract(extracted, text, text_lower, "PCS_TRAFO_RATING", "PCS Transformer Rating", "MVA", "PCS",
                 [r"transformer.*?(?:rating|capacity).*?(\d+(?:\.\d+)?)\s*(?:MVA|kVA)",
                  r"(\d+(?:\.\d+)?)\s*(?:MVA|kVA).*?transformer"])
    _try_extract(extracted, text, text_lower, "PCS_TRAFO_VOLTAGE", "PCS Transformer Secondary Voltage", "kV", "PCS",
                 [r"(?:secondary|HV|MV)\s*(?:side\s*)?voltage.*?(\d+(?:\.\d+)?)\s*kV"])

    # ── Thermal / HVAC ──
    _try_extract(extracted, text, text_lower, "THERMAL_AMBIENT_MAX", "Max Ambient Temperature", "°C", "Thermal / HVAC",
                 [r"(?:max|maximum)\s*ambient\s*(?:temp|temperature).*?(\d+)\s*[°℃C]",
                  r"ambient.*?(?:max|maximum).*?(\d+)\s*[°℃C]"])
    _try_extract(extracted, text, text_lower, "THERMAL_AMBIENT_MIN", "Min Ambient Temperature", "°C", "Thermal / HVAC",
                 [r"(?:min|minimum)\s*ambient.*?(-?\d+)\s*[°℃C]",
                  r"ambient.*?(?:min|minimum).*?(-?\d+)\s*[°℃C]"])
    _try_extract(extracted, text, text_lower, "THERMAL_HUMIDITY", "Humidity Range", "%RH", "Thermal / HVAC",
                 [r"humidity.*?(?:up\s*to\s*)?(\d+)\s*%"])
    _try_extract(extracted, text, text_lower, "THERMAL_ALTITUDE", "Site Altitude", "m", "Thermal / HVAC",
                 [r"altitude.*?(\d[\d,]*)\s*m", r"(\d[\d,]*)\s*m.*?(?:altitude|above\s*(?:MSL|sea))"])
    _try_extract(extracted, text, text_lower, "THERMAL_SEISMIC", "Seismic Zone", "", "Thermal / HVAC",
                 [r"(?:seismic|earthquake)\s*(?:zone|IS\s*1893).*?((?:zone\s*)?(?:II|III|IV|V|2|3|4|5))",
                  r"IS\s*1893.*?(?:zone\s*)?(\w+)"])
    _try_extract(extracted, text, text_lower, "HVAC_COOLING_KW", "HVAC Cooling Capacity per Container", "kW", "Thermal / HVAC",
                 [r"(?:HVAC|cooling)\s*(?:capacity|power).*?(\d+(?:\.\d+)?)\s*kW"])
    _try_keyword(extracted, text_lower, "HVAC_COOLING_TYPE", "Cooling System Type", "", "Thermal / HVAC",
                 {"liquid cool": "Liquid Cooling", "liquid-cool": "Liquid Cooling",
                  "air cool": "Air Cooling", "air-cool": "Air Cooling",
                  "precision cool": "Precision Cooling"})

    # ── Guarantees / Performance ──
    _try_extract(extracted, text, text_lower, "GUAR_DISPATCHABLE_MWH", "Dispatchable Energy at POI", "MWh", "Guarantees",
                 [r"(?:dispatchable|net)\s*(?:energy|capacity).*?(\d+(?:\.\d+)?)\s*MWh",
                  r"(\d+(?:\.\d+)?)\s*MWh.*?(?:dispatchable|net\s*deliverable)"])
    _try_extract(extracted, text, text_lower, "GUAR_ANNUAL_DEGRADATION", "Annual Capacity Degradation", "%/year", "Guarantees",
                 [r"(?:annual\s*)?degradation\s*(?:rate|limit)?.*?[≤<=]?\s*(\d+(?:\.\d+)?)\s*%\s*(?:per\s*(?:year|annum))",
                  r"degradation.*?(?:shall\s*)?(?:not\s*)?(?:exceed\s*)(\d+(?:\.\d+)?)\s*%\s*per\s*(?:year|annum)"])
    _try_extract(extracted, text, text_lower, "GUAR_EOL_CAPACITY", "End-of-Life Capacity", "%", "Guarantees",
                 [r"(?:end\s*of\s*life|EOL).*?(?:capacity|retention).*?(\d+)\s*%",
                  r"(\d+)\s*%.*?(?:end\s*of\s*life|EOL)"])
    _try_extract(extracted, text, text_lower, "GUAR_MTBF", "Mean Time Between Failures (MTBF)", "hours", "Guarantees",
                 [r"MTBF.*?(\d[\d,]*)\s*(?:hour|hr)"])
    _try_extract(extracted, text, text_lower, "GUAR_MTTR", "Mean Time To Repair (MTTR)", "hours", "Guarantees",
                 [r"MTTR.*?[<≤<=]?\s*(\d+)\s*(?:hour|hr)"])
    _try_extract(extracted, text, text_lower, "GUAR_LD_CAP", "Liquidated Damages Cap", "%", "Guarantees",
                 [r"(?:LD|liquidated\s*damages?)\s*(?:cap|maximum|aggregate).*?(\d+(?:\.\d+)?)\s*%"])
    _try_extract(extracted, text, text_lower, "GUAR_PLANNED_DOWNTIME", "Planned Maintenance Downtime", "hours/year", "Guarantees",
                 [r"(?:planned|scheduled)\s*(?:maintenance\s*)?downtime.*?(\d+)\s*(?:hour|day)"])
    _try_extract(extracted, text, text_lower, "GUAR_CYCLES_PER_DAY", "Max Cycles Per Day", "cycles/day", "Guarantees",
                 [r"(\d+)\s*(?:cycle|shift)s?\s*per\s*day"])
    _try_extract(extracted, text, text_lower, "GUAR_FIRST_DISCHARGE", "Capacity on First Discharge", "%", "Guarantees",
                 [r"first\s*discharge.*?(\d{2}(?:\.\d+)?)\s*%", r"(\d{2}(?:\.\d+)?)\s*%.*?first\s*discharge"], prefix=">=")
    _try_extract(extracted, text, text_lower, "INTERCONNECT_VOLTAGE", "Interconnection Voltage at POI", "kV", "System",
                 [r"(?:interconnection|POI|point\s*of\s*interconnection).*?(\d+)\s*kV",
                  r"(\d+)\s*kV.*?(?:interconnection|at\s*POI)"])

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
        ("CERT_IEC62109", "IEC 62109 (PV Inverter Safety)", ["iec 62109", "62109"]),
        ("CERT_IEEE1547", "IEEE 1547 (Grid Interconnection)", ["ieee 1547", "1547"]),
        ("CERT_UL1741", "UL 1741 (Inverter Safety)", ["ul 1741", "ul1741"]),
        ("CERT_IEC62443", "IEC 62443 (Cybersecurity)", ["iec 62443", "62443"]),
        ("CERT_IS1893", "IS 1893 (Seismic)", ["is 1893", "is1893"]),
        ("CERT_IS2026", "IS 2026 (Transformer)", ["is 2026"]),
        ("CERT_IEC60076", "IEC 60076 (Power Transformers)", ["iec 60076", "60076"]),
        ("CERT_NFPA855", "NFPA 855 (ESS Fire Safety)", ["nfpa 855"]),
        ("CERT_ISO9001", "ISO 9001 (Quality Management)", ["iso 9001"]),
        ("CERT_ISO14001", "ISO 14001 (Environmental)", ["iso 14001"]),
        ("CERT_ISO45001", "ISO 45001 (Safety)", ["iso 45001"]),
    ]
    for code, param, keywords in cert_checks:
        for kw in keywords:
            if kw in text_lower:
                extracted.append({"parameter": param, "code": code, "required_value": "Required", "unit": "", "section": "Certifications"})
                break

    # ── Fire Safety ──
    if any(kw in text_lower for kw in ["fire detection", "fire alarm", "smoke detect", "heat detect", "vesda"]):
        extracted.append({"parameter": "Fire Detection & Alarm System", "code": "FIRE_DETECTION", "required_value": "Required", "unit": "", "section": "Fire Safety"})
    if any(kw in text_lower for kw in ["fire suppression", "fire protection", "fire fighting", "fire safety system", "fire extinguish"]):
        extracted.append({"parameter": "Fire Suppression System", "code": "FIRE_SUPPRESSION", "required_value": "Required", "unit": "", "section": "Fire Safety"})
    if "nfpa" in text_lower:
        extracted.append({"parameter": "NFPA Standards", "code": "FIRE_NFPA", "required_value": "Required", "unit": "", "section": "Fire Safety"})

    # ── EMS / SCADA ──
    if any(kw in text_lower for kw in ["energy management system", "ems", "scada", "supervisory control", "plant controller", "power plant controller", "ppc"]):
        extracted.append({"parameter": "Energy Management System", "code": "EMS_REQUIRED", "required_value": "Required", "unit": "", "section": "EMS / SCADA"})
    if "hybrid ems" in text_lower or "hybrid energy management" in text_lower or ("solar" in text_lower and "ems" in text_lower and "bess" in text_lower):
        extracted.append({"parameter": "Hybrid EMS (Solar + BESS)", "code": "EMS_HYBRID", "required_value": "Required", "unit": "", "section": "EMS / SCADA"})
    if any(kw in text_lower for kw in ["indigenous", "make in india", "atmanirbhar", "developed in india", "domestic content", "local content"]):
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
        ("GRID_PFR", "Primary Frequency Response (PFR)", ["primary frequency", "pfr", "primary response", "fast frequency response", "ffr"]),
        ("GRID_SFR", "Secondary Frequency Response (SFR)", ["secondary frequency", "sfr", "agc", "automatic generation control"]),
        ("GRID_TFR", "Tertiary Frequency Response", ["tertiary frequency", "tertiary reserve", "manual frequency"]),
        ("GRID_INERTIA", "Synthetic / Virtual Inertia", ["synthetic inertia", "virtual inertia", "synthetic rotational", "grid inertia"]),
        ("GRID_BLACK_START", "Black Start Capability", ["black start", "blackstart", "system restoration"]),
        ("GRID_REACTIVE", "Reactive Power Compensation", ["reactive power", "kvar support", "var support", "voltage support", "stat com", "statcom"]),
    ]
    for code, param, keywords in grid_checks:
        for kw in keywords:
            if kw in text_lower:
                extracted.append({"parameter": param, "code": code, "required_value": "Mandatory", "unit": "", "section": "Grid Support"})
                break

    # ── O&M / Warranty ──
    _try_extract(extracted, text, text_lower, "OM_PERIOD", "O&M / AMC Period", "years", "O&M / Warranty",
                 [r"(?:O&M|O\s*&\s*M|AMC|operation[s]?\s*(?:and|&)\s*maintenance|long[\s-]*term\s*service\s*agreement|LTSA|FSA|CAMC|comprehensive\s*(?:annual\s*)?maintenance)\s*(?:period|duration|term|contract)?.*?(\d+)\s*years?",
                  r"(\d+)\s*years?\s*(?:O&M|AMC|LTSA|FSA|CAMC|comprehensive\s*maintenance)"])
    _try_extract(extracted, text, text_lower, "OM_WARRANTY", "Comprehensive Warranty", "years", "O&M / Warranty",
                 [r"(?:comprehensive|extended|product|equipment|standard)\s*warranty\s*(?:period|duration|term)?.*?(\d+)\s*years?",
                  r"warranty\s*(?:period|term|duration)\s*(?:of)?\s*(\d+)\s*years?",
                  r"(\d+)\s*years?\s*(?:comprehensive\s*)?warranty"])
    if any(kw in text_lower for kw in ["augmentation", "capacity addition", "capacity refresh", "battery refresh", "top-up", "top up", "replacement of cells"]):
        extracted.append({"parameter": "Augmentation in Scope", "code": "OM_AUGMENTATION", "required_value": "Included in bidder scope", "unit": "", "section": "O&M / Warranty"})
    if any(kw in text_lower for kw in ["performance guarantee", "energy throughput warranty", "throughput guarantee", "capacity guarantee", "energy guarantee", "performance warranty"]):
        extracted.append({"parameter": "Performance Guarantee", "code": "OM_PERF_GUARANTEE", "required_value": "Required for full design life", "unit": "", "section": "O&M / Warranty"})
    if any(kw in text_lower for kw in ["insurance", "all risk policy", "CAR policy", "EAR policy"]):
        extracted.append({"parameter": "Insurance", "code": "OM_INSURANCE", "required_value": "Included in scope", "unit": "", "section": "O&M / Warranty"})
    if any(kw in text_lower for kw in ["operator training", "training of operator", "training of personnel", "training programme", "training program", "skill development"]):
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
