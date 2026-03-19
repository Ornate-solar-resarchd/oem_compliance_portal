"""
In-memory seed data — realistic BESS component data for 4 OEMs.
No database required. All data served from these dictionaries.
"""

OEMS = [
    {
        "id": "oem-catl-001",
        "name": "CATL",
        "country_of_origin": "China",
        "is_approved": True,
        "score": 97.5,
        "models": 2,
        "model_count": 2,
        "avg_compliance_score": 97.5,
        "website": "https://catl.com",
        "contact_email": "india@catl.com",
    },
    {
        "id": "oem-lishen-002",
        "name": "Lishen",
        "country_of_origin": "China",
        "is_approved": True,
        "score": 91.2,
        "models": 2,
        "model_count": 2,
        "avg_compliance_score": 91.2,
        "website": "https://lishen.com.cn",
        "contact_email": "export@lishen.com.cn",
    },
    {
        "id": "oem-byd-003",
        "name": "BYD",
        "country_of_origin": "China",
        "is_approved": True,
        "score": 94.8,
        "models": 1,
        "model_count": 1,
        "avg_compliance_score": 94.8,
        "website": "https://byd.com",
        "contact_email": "ess@byd.com",
    },
    {
        "id": "oem-hithium-004",
        "name": "HiTHIUM",
        "country_of_origin": "China",
        "is_approved": False,
        "score": 87.4,
        "models": 1,
        "model_count": 1,
        "avg_compliance_score": 87.4,
        "website": "https://hithium.com",
        "contact_email": "sales@hithium.com",
    },
    {
        "id": "oem-svolt-005",
        "name": "SVOLT",
        "country_of_origin": "China",
        "is_approved": True,
        "score": 93.1,
        "models": 2,
        "model_count": 2,
        "avg_compliance_score": 93.1,
        "website": "https://www.svolt.cn/en",
        "contact_email": "ess@svolt.cn",
    },
]

COMPONENTS = [
    {
        "id": "comp-catl-280",
        "oem_id": "oem-catl-001",
        "oem_name": "CATL",
        "model_name": "CATL-LFP-280AH-3.2V",
        "sku": "EVE-LF280K",
        "component_type_name": "Cell",
        "fill_rate": 100,
        "compliance_score": 97.5,
        "is_active": True,
        "pass": 26, "fail": 1, "waived": 1,
        "datasheet": "catl-280ah-datasheet-v3.1.pdf",
    },
    {
        "id": "comp-catl-314",
        "oem_id": "oem-catl-001",
        "oem_name": "CATL",
        "model_name": "CATL-LFP-314AH-3.2V",
        "sku": "CATL-LF314K",
        "component_type_name": "Cell",
        "fill_rate": 96,
        "compliance_score": 96.4,
        "is_active": True,
        "pass": 25, "fail": 1, "waived": 2,
        "datasheet": "catl-314ah-datasheet-v2.0.pdf",
    },
    {
        "id": "comp-lishen-271",
        "oem_id": "oem-lishen-002",
        "oem_name": "Lishen",
        "model_name": "Lishen-LFP-271AH-3.2V",
        "sku": "LR-LF271K",
        "component_type_name": "Cell",
        "fill_rate": 100,
        "compliance_score": 91.2,
        "is_active": True,
        "pass": 24, "fail": 2, "waived": 2,
        "datasheet": "lishen-271ah-datasheet-v4.pdf",
    },
    {
        "id": "comp-lishen-280",
        "oem_id": "oem-lishen-002",
        "oem_name": "Lishen",
        "model_name": "Lishen-LFP-280AH-3.2V",
        "sku": "LR-LF280K",
        "component_type_name": "Cell",
        "fill_rate": 93,
        "compliance_score": 89.3,
        "is_active": True,
        "pass": 23, "fail": 3, "waived": 2,
        "datasheet": "lishen-280ah-datasheet-v2.pdf",
    },
    {
        "id": "comp-byd-blade",
        "oem_id": "oem-byd-003",
        "oem_name": "BYD",
        "model_name": "BYD-Blade-LFP-138AH",
        "sku": "BYD-BL138",
        "component_type_name": "Cell",
        "fill_rate": 100,
        "compliance_score": 94.8,
        "is_active": True,
        "pass": 25, "fail": 1, "waived": 2,
        "datasheet": "byd-blade-138ah-datasheet.pdf",
    },
    {
        "id": "comp-hithium-280",
        "oem_id": "oem-hithium-004",
        "oem_name": "HiTHIUM",
        "model_name": "HiTHIUM-LFP-280AH-3.2V",
        "sku": "HTL-LF280K",
        "component_type_name": "Cell",
        "fill_rate": 89,
        "compliance_score": 87.4,
        "is_active": True,
        "pass": 22, "fail": 4, "waived": 2,
        "datasheet": "hithium-280ah-datasheet-v1.pdf",
    },
    {
        "id": "comp-svolt-280",
        "oem_id": "oem-svolt-005",
        "oem_name": "SVOLT",
        "model_name": "SVOLT-LFP-280AH-3.2V",
        "sku": "SVL-LF280N",
        "component_type_name": "Cell",
        "fill_rate": 100,
        "compliance_score": 95.2,
        "is_active": True,
        "pass": 26, "fail": 1, "waived": 1,
        "datasheet": "svolt-280ah-datasheet-v2.pdf",
    },
    {
        "id": "comp-svolt-blade",
        "oem_id": "oem-svolt-005",
        "oem_name": "SVOLT",
        "model_name": "SVOLT-Short-Blade-LFP-196AH",
        "sku": "SVL-SB196",
        "component_type_name": "Cell",
        "fill_rate": 96,
        "compliance_score": 91.0,
        "is_active": True,
        "pass": 24, "fail": 2, "waived": 2,
        "datasheet": "svolt-short-blade-196ah-v1.pdf",
    },
]

# Parameters keyed by component_id
PARAMETERS = {
    "comp-catl-280": [
        {"code": "CELL_CAPACITY_AH", "name": "Nominal Capacity", "value": "280", "unit": "Ah", "section": "Electrical", "status": "pass", "confidence": 0.97},
        {"code": "CELL_VOLTAGE_V", "name": "Nominal Voltage", "value": "3.2", "unit": "V", "section": "Electrical", "status": "pass", "confidence": 0.99},
        {"code": "CELL_ENERGY_WH", "name": "Energy", "value": "896", "unit": "Wh", "section": "Electrical", "status": "pass", "confidence": 0.95},
        {"code": "CELL_IR_MOHM", "name": "Internal Resistance", "value": "0.4", "unit": "mohm", "section": "Electrical", "status": "pass", "confidence": 0.92},
        {"code": "CELL_CYCLE_LIFE", "name": "Cycle Life", "value": "6000", "unit": "cycles", "section": "Electrical", "status": "pass", "confidence": 0.94},
        {"code": "CELL_CALENDAR_LIFE", "name": "Calendar Life", "value": "20", "unit": "years", "section": "Electrical", "status": "pass", "confidence": 0.90},
        {"code": "CELL_MAX_CHARGE_RATE", "name": "Max Charge Rate", "value": "0.5", "unit": "C", "section": "Electrical", "status": "pass", "confidence": 0.93},
        {"code": "CELL_MAX_DISCHARGE_RATE", "name": "Max Discharge Rate", "value": "1.0", "unit": "C", "section": "Electrical", "status": "pass", "confidence": 0.93},
        {"code": "CELL_WEIGHT_KG", "name": "Weight", "value": "5.42", "unit": "kg", "section": "Physical", "status": "pass", "confidence": 0.98},
        {"code": "CELL_LENGTH_MM", "name": "Length", "value": "174", "unit": "mm", "section": "Physical", "status": "pass", "confidence": 0.99},
        {"code": "CELL_WIDTH_MM", "name": "Width", "value": "72", "unit": "mm", "section": "Physical", "status": "pass", "confidence": 0.99},
        {"code": "CELL_HEIGHT_MM", "name": "Height", "value": "207", "unit": "mm", "section": "Physical", "status": "pass", "confidence": 0.99},
        {"code": "CELL_ENERGY_DENSITY", "name": "Energy Density", "value": "165", "unit": "Wh/kg", "section": "Physical", "status": "pass", "confidence": 0.91},
        {"code": "CELL_CHARGE_TEMP_MIN", "name": "Charge Temp Min", "value": "0", "unit": "C", "section": "Thermal", "status": "pass", "confidence": 0.96},
        {"code": "CELL_CHARGE_TEMP_MAX", "name": "Charge Temp Max", "value": "55", "unit": "C", "section": "Thermal", "status": "pass", "confidence": 0.96},
        {"code": "CELL_DISCHARGE_TEMP_MIN", "name": "Discharge Temp Min", "value": "-20", "unit": "C", "section": "Thermal", "status": "pass", "confidence": 0.96},
        {"code": "CELL_DISCHARGE_TEMP_MAX", "name": "Discharge Temp Max", "value": "60", "unit": "C", "section": "Thermal", "status": "pass", "confidence": 0.96},
        {"code": "CELL_STORAGE_TEMP_MIN", "name": "Storage Temp Min", "value": "-20", "unit": "C", "section": "Thermal", "status": "pass", "confidence": 0.94},
        {"code": "CELL_STORAGE_TEMP_MAX", "name": "Storage Temp Max", "value": "45", "unit": "C", "section": "Thermal", "status": "pass", "confidence": 0.94},
        {"code": "CELL_CHEMISTRY", "name": "Chemistry", "value": "LFP", "unit": "", "section": "Safety", "status": "pass", "confidence": 0.99},
        {"code": "CELL_CERTIFICATIONS", "name": "Certifications", "value": "IEC 62619, UL 1973", "unit": "", "section": "Safety", "status": "pass", "confidence": 0.95},
        {"code": "CELL_BIS_CERT", "name": "BIS Certified", "value": "Yes", "unit": "", "section": "Safety", "status": "pass", "confidence": 0.92},
        {"code": "CELL_UN383", "name": "UN38.3", "value": "Yes", "unit": "", "section": "Safety", "status": "pass", "confidence": 0.97},
        {"code": "CELL_FORM_FACTOR", "name": "Form Factor", "value": "Prismatic", "unit": "", "section": "Safety", "status": "pass", "confidence": 0.99},
        {"code": "CELL_SELF_DISCHARGE", "name": "Self Discharge Rate", "value": "3", "unit": "%/month", "section": "Performance", "status": "pass", "confidence": 0.88},
        {"code": "CELL_COULOMBIC_EFF", "name": "Coulombic Efficiency", "value": "99.5", "unit": "%", "section": "Performance", "status": "pass", "confidence": 0.90},
        {"code": "CELL_ENERGY_EFF", "name": "Round-trip Efficiency", "value": "95.8", "unit": "%", "section": "Performance", "status": "fail", "confidence": 0.87},
        {"code": "CELL_EOL_CAPACITY", "name": "EOL Capacity Retention", "value": "80", "unit": "%", "section": "Performance", "status": "pass", "confidence": 0.91},
    ],
    "comp-catl-314": None,  # will be auto-generated
    "comp-lishen-271": None,
    "comp-lishen-280": None,
    "comp-byd-blade": None,
    "comp-hithium-280": None,
    "comp-svolt-280": None,
    "comp-svolt-blade": None,
}


def _make_params(base, overrides):
    """Clone base params with overrides dict."""
    result = []
    for p in base:
        new = dict(p)
        if new["code"] in overrides:
            new.update(overrides[new["code"]])
        result.append(new)
    return result


# Generate params for other components based on CATL-280 as template
_catl_base = PARAMETERS["comp-catl-280"]

PARAMETERS["comp-catl-314"] = _make_params(_catl_base, {
    "CELL_CAPACITY_AH": {"value": "314"},
    "CELL_ENERGY_WH": {"value": "1004.8"},
    "CELL_WEIGHT_KG": {"value": "5.88"},
    "CELL_ENERGY_DENSITY": {"value": "170.9"},
    "CELL_CYCLE_LIFE": {"value": "6500"},
    "CELL_ENERGY_EFF": {"value": "96.2", "status": "pass"},
})

PARAMETERS["comp-lishen-271"] = _make_params(_catl_base, {
    "CELL_CAPACITY_AH": {"value": "271"},
    "CELL_ENERGY_WH": {"value": "867.2"},
    "CELL_IR_MOHM": {"value": "0.45"},
    "CELL_CYCLE_LIFE": {"value": "5000"},
    "CELL_CALENDAR_LIFE": {"value": "18"},
    "CELL_WEIGHT_KG": {"value": "5.48"},
    "CELL_LENGTH_MM": {"value": "174"},
    "CELL_WIDTH_MM": {"value": "71"},
    "CELL_HEIGHT_MM": {"value": "204"},
    "CELL_ENERGY_DENSITY": {"value": "158"},
    "CELL_BIS_CERT": {"value": "No", "status": "fail"},
    "CELL_CERTIFICATIONS": {"value": "IEC 62619"},
    "CELL_ENERGY_EFF": {"value": "95.2", "status": "fail"},
})

PARAMETERS["comp-lishen-280"] = _make_params(_catl_base, {
    "CELL_CAPACITY_AH": {"value": "280"},
    "CELL_ENERGY_WH": {"value": "896"},
    "CELL_IR_MOHM": {"value": "0.48"},
    "CELL_CYCLE_LIFE": {"value": "5500"},
    "CELL_CALENDAR_LIFE": {"value": "18"},
    "CELL_WEIGHT_KG": {"value": "5.52"},
    "CELL_ENERGY_DENSITY": {"value": "162"},
    "CELL_BIS_CERT": {"value": "No", "status": "fail"},
    "CELL_CERTIFICATIONS": {"value": "IEC 62619"},
    "CELL_SELF_DISCHARGE": {"value": "3.5"},
    "CELL_ENERGY_EFF": {"value": "94.8", "status": "fail"},
})

PARAMETERS["comp-byd-blade"] = _make_params(_catl_base, {
    "CELL_CAPACITY_AH": {"value": "138"},
    "CELL_ENERGY_WH": {"value": "441.6"},
    "CELL_IR_MOHM": {"value": "0.5"},
    "CELL_CYCLE_LIFE": {"value": "8000"},
    "CELL_CALENDAR_LIFE": {"value": "25"},
    "CELL_WEIGHT_KG": {"value": "3.92"},
    "CELL_LENGTH_MM": {"value": "905"},
    "CELL_WIDTH_MM": {"value": "13.5"},
    "CELL_HEIGHT_MM": {"value": "118"},
    "CELL_ENERGY_DENSITY": {"value": "112.7"},
    "CELL_FORM_FACTOR": {"value": "Blade (Prismatic)"},
    "CELL_CERTIFICATIONS": {"value": "IEC 62619, UL 1973, BIS"},
    "CELL_ENERGY_EFF": {"value": "96.0", "status": "pass"},
})

PARAMETERS["comp-hithium-280"] = _make_params(_catl_base, {
    "CELL_IR_MOHM": {"value": "0.42"},
    "CELL_WEIGHT_KG": {"value": "5.38"},
    "CELL_ENERGY_DENSITY": {"value": "166.5"},
    "CELL_CERTIFICATIONS": {"value": "IEC 62619"},
    "CELL_BIS_CERT": {"value": "No", "status": "fail"},
    "CELL_SELF_DISCHARGE": {"value": "3.2"},
    "CELL_COULOMBIC_EFF": {"value": "99.2"},
    "CELL_ENERGY_EFF": {"value": "94.5", "status": "fail"},
    "CELL_EOL_CAPACITY": {"value": "78", "status": "fail"},
})

# SVOLT 280Ah — high-quality LFP prismatic cell (svolt.cn)
PARAMETERS["comp-svolt-280"] = _make_params(_catl_base, {
    "CELL_CAPACITY_AH": {"value": "280"},
    "CELL_ENERGY_WH": {"value": "896"},
    "CELL_IR_MOHM": {"value": "0.38"},
    "CELL_CYCLE_LIFE": {"value": "6000"},
    "CELL_CALENDAR_LIFE": {"value": "20"},
    "CELL_MAX_CHARGE_RATE": {"value": "0.5"},
    "CELL_MAX_DISCHARGE_RATE": {"value": "1.0"},
    "CELL_WEIGHT_KG": {"value": "5.35"},
    "CELL_LENGTH_MM": {"value": "174"},
    "CELL_WIDTH_MM": {"value": "72"},
    "CELL_HEIGHT_MM": {"value": "207"},
    "CELL_ENERGY_DENSITY": {"value": "167.5"},
    "CELL_CERTIFICATIONS": {"value": "IEC 62619, UL 1973"},
    "CELL_BIS_CERT": {"value": "Yes"},
    "CELL_SELF_DISCHARGE": {"value": "2.8"},
    "CELL_COULOMBIC_EFF": {"value": "99.5"},
    "CELL_ENERGY_EFF": {"value": "96.1", "status": "pass"},
    "CELL_EOL_CAPACITY": {"value": "80"},
})

# SVOLT Short Blade 196Ah — compact blade cell for C&I/BTM
PARAMETERS["comp-svolt-blade"] = _make_params(_catl_base, {
    "CELL_CAPACITY_AH": {"value": "196"},
    "CELL_ENERGY_WH": {"value": "627.2"},
    "CELL_IR_MOHM": {"value": "0.45"},
    "CELL_CYCLE_LIFE": {"value": "7000"},
    "CELL_CALENDAR_LIFE": {"value": "22"},
    "CELL_MAX_CHARGE_RATE": {"value": "0.5"},
    "CELL_MAX_DISCHARGE_RATE": {"value": "1.5"},
    "CELL_WEIGHT_KG": {"value": "4.15"},
    "CELL_LENGTH_MM": {"value": "580"},
    "CELL_WIDTH_MM": {"value": "21.5"},
    "CELL_HEIGHT_MM": {"value": "118"},
    "CELL_ENERGY_DENSITY": {"value": "151.1"},
    "CELL_FORM_FACTOR": {"value": "Short Blade (Prismatic)"},
    "CELL_CERTIFICATIONS": {"value": "IEC 62619"},
    "CELL_BIS_CERT": {"value": "No", "status": "fail"},
    "CELL_SELF_DISCHARGE": {"value": "2.5"},
    "CELL_COULOMBIC_EFF": {"value": "99.4"},
    "CELL_ENERGY_EFF": {"value": "95.5", "status": "fail"},
    "CELL_EOL_CAPACITY": {"value": "82"},
})

PROJECTS = [
    {"id": "proj-001", "name": "NTPC Barh BESS", "client_name": "NGSL", "project_type": "utility", "kwh": 400000, "kw": 200000, "location": "Barh, Bihar", "status": "active", "progress": 65},
    {"id": "proj-002", "name": "Amrita Hospital BTM", "client_name": "Amrita Hospital", "project_type": "btm", "kwh": 20000, "kw": 11000, "location": "Kochi, Kerala", "status": "active", "progress": 45},
    {"id": "proj-003", "name": "BSPGCL Bihar", "client_name": "BSPGCL", "project_type": "utility", "kwh": 500000, "kw": 125000, "location": "Patna, Bihar", "status": "active", "progress": 100},
    {"id": "proj-004", "name": "Eagle Infra TNGECL", "client_name": "Eagle Infra", "project_type": "ci", "kwh": 25000, "kw": 5000, "location": "Chennai, Tamil Nadu", "status": "active", "progress": 30},
    {"id": "proj-005", "name": "Sitapur Solar+BESS", "client_name": "NTPC REL", "project_type": "hybrid", "kwh": 200000, "kw": 250000, "location": "Sitapur, UP", "status": "active", "progress": 80},
]

SHEETS = [
    {"id": "sheet-001", "sheet_number": "TCS-001", "project_id": "proj-001", "project_name": "NTPC Barh BESS", "component_id": "comp-catl-280", "component_model_name": "CATL-LFP-280AH-3.2V", "workflow_stage": "technical_lead", "compliance_score": 97.5, "revision": "r2", "pass": 26, "fail": 1, "waived": 1},
    {"id": "sheet-002", "sheet_number": "TCS-002", "project_id": "proj-001", "project_name": "NTPC Barh BESS", "component_id": "comp-lishen-271", "component_model_name": "Lishen-LFP-271AH-3.2V", "workflow_stage": "engineering_review", "compliance_score": 91.2, "revision": "r1", "pass": 24, "fail": 2, "waived": 2},
    {"id": "sheet-003", "sheet_number": "TCS-003", "project_id": "proj-002", "project_name": "Amrita Hospital BTM", "component_id": "comp-byd-blade", "component_model_name": "BYD-Blade-LFP-138AH", "workflow_stage": "management", "compliance_score": 94.8, "revision": "r1", "pass": 25, "fail": 1, "waived": 2},
    {"id": "sheet-004", "sheet_number": "TCS-004", "project_id": "proj-003", "project_name": "BSPGCL Bihar", "component_id": "comp-catl-280", "component_model_name": "CATL-LFP-280AH-3.2V", "workflow_stage": "locked", "compliance_score": 98.2, "revision": "v1.0", "pass": 27, "fail": 0, "waived": 1},
    {"id": "sheet-005", "sheet_number": "TCS-005", "project_id": "proj-004", "project_name": "Eagle Infra TNGECL", "component_id": "comp-hithium-280", "component_model_name": "HiTHIUM-LFP-280AH-3.2V", "workflow_stage": "draft", "compliance_score": 87.4, "revision": "r1", "pass": 22, "fail": 4, "waived": 2},
    {"id": "sheet-006", "sheet_number": "TCS-006", "project_id": "proj-005", "project_name": "Sitapur Solar+BESS", "component_id": "comp-catl-314", "component_model_name": "CATL-LFP-314AH-3.2V", "workflow_stage": "customer_submission", "compliance_score": 96.4, "revision": "r1", "pass": 25, "fail": 1, "waived": 2},
    {"id": "sheet-007", "sheet_number": "TCS-007", "project_id": "proj-005", "project_name": "Sitapur Solar+BESS", "component_id": "comp-lishen-280", "component_model_name": "Lishen-LFP-280AH-3.2V", "workflow_stage": "customer_signoff", "compliance_score": 89.3, "revision": "r3", "pass": 23, "fail": 3, "waived": 2},
]

WORKFLOWS = [
    {"id": "sheet-001", "sheet_number": "TCS-001", "project_name": "NTPC Barh BESS", "workflow_stage": "technical_lead", "compliance_score": 97.5, "component_model_name": "CATL-LFP-280AH-3.2V", "waiting_hours": 5, "revision": "r2", "pass": 26, "fail": 1, "waived": 1},
    {"id": "sheet-002", "sheet_number": "TCS-002", "project_name": "NTPC Barh BESS", "workflow_stage": "engineering_review", "compliance_score": 91.2, "component_model_name": "Lishen-LFP-271AH-3.2V", "waiting_hours": 18, "revision": "r1", "pass": 24, "fail": 2, "waived": 2},
    {"id": "sheet-003", "sheet_number": "TCS-003", "project_name": "Amrita Hospital BTM", "workflow_stage": "management", "compliance_score": 94.8, "component_model_name": "BYD-Blade-LFP-138AH", "waiting_hours": 2, "revision": "r1", "pass": 25, "fail": 1, "waived": 2},
    {"id": "sheet-005", "sheet_number": "TCS-005", "project_name": "Eagle Infra TNGECL", "workflow_stage": "draft", "compliance_score": 87.4, "component_model_name": "HiTHIUM-LFP-280AH-3.2V", "waiting_hours": 51, "revision": "r1", "pass": 22, "fail": 4, "waived": 2},
    {"id": "sheet-006", "sheet_number": "TCS-006", "project_name": "Sitapur Solar+BESS", "workflow_stage": "customer_submission", "compliance_score": 96.4, "component_model_name": "CATL-LFP-314AH-3.2V", "waiting_hours": 7, "revision": "r1", "pass": 25, "fail": 1, "waived": 2},
]

RFQS = [
    {
        "id": "rfq-001",
        "customer_name": "NTPC REL",
        "project_name": "Sitapur Solar+BESS",
        "status": "active",
        "created_at": "2026-02-15T10:00:00Z",
        "requirements": [
            {"parameter": "Nominal Capacity", "code": "CELL_CAPACITY_AH", "required_value": ">=270", "unit": "Ah"},
            {"parameter": "Nominal Voltage", "code": "CELL_VOLTAGE_V", "required_value": "3.2", "unit": "V"},
            {"parameter": "Cycle Life", "code": "CELL_CYCLE_LIFE", "required_value": ">=5000", "unit": "cycles"},
            {"parameter": "BIS Certified", "code": "CELL_BIS_CERT", "required_value": "Yes", "unit": ""},
            {"parameter": "Chemistry", "code": "CELL_CHEMISTRY", "required_value": "LFP", "unit": ""},
            {"parameter": "Round-trip Efficiency", "code": "CELL_ENERGY_EFF", "required_value": ">=95", "unit": "%"},
            {"parameter": "Energy Density", "code": "CELL_ENERGY_DENSITY", "required_value": ">=150", "unit": "Wh/kg"},
            {"parameter": "UN38.3", "code": "CELL_UN383", "required_value": "Yes", "unit": ""},
        ]
    },
    {
        "id": "rfq-002",
        "customer_name": "BSPGCL",
        "project_name": "Bihar Grid-Scale BESS",
        "status": "active",
        "created_at": "2026-03-01T09:00:00Z",
        "requirements": [
            {"parameter": "Nominal Capacity", "code": "CELL_CAPACITY_AH", "required_value": ">=280", "unit": "Ah"},
            {"parameter": "Cycle Life", "code": "CELL_CYCLE_LIFE", "required_value": ">=6000", "unit": "cycles"},
            {"parameter": "Calendar Life", "code": "CELL_CALENDAR_LIFE", "required_value": ">=20", "unit": "years"},
            {"parameter": "BIS Certified", "code": "CELL_BIS_CERT", "required_value": "Yes", "unit": ""},
            {"parameter": "Certifications", "code": "CELL_CERTIFICATIONS", "required_value": "IEC 62619", "unit": ""},
            {"parameter": "Round-trip Efficiency", "code": "CELL_ENERGY_EFF", "required_value": ">=96", "unit": "%"},
        ]
    },
    {
        "id": "rfq-003",
        "customer_name": "Evolve Energy Group",
        "project_name": "15MW/45MWh Solar+BESS+EMS — Tamil Nadu",
        "status": "active",
        "created_at": "2026-02-01T10:00:00Z",
        "source_file": "RFQ_15MW_45MWH_BESS_EMS_Rev01.pdf",
        "extraction_method": "ai_simulated",
        "project_meta": {
            "rfq_ref": "EEG/BESS-EMS/RFQ/2025-01",
            "capacity": "15 MW / 45 MWh",
            "solar_pv": "20 MWp",
            "location": "Tamil Nadu, India",
            "scope": "Turnkey BESS + EMS/SCADA",
            "design_life": "12 Years (Option 1) | 25 Years (Option 2)",
        },
        "requirements": [
            {"parameter": "Chemistry / Technology", "code": "CELL_CHEMISTRY", "required_value": "LFP", "unit": "", "section": "BESS"},
            {"parameter": "Cooling System", "code": "BESS_COOLING", "required_value": "Liquid Cooled", "unit": "", "section": "BESS"},
            {"parameter": "Round-Trip Efficiency (AC-AC)", "code": "CELL_ENERGY_EFF", "required_value": ">=85", "unit": "%", "section": "BESS Performance"},
            {"parameter": "Firm Discharge", "code": "BESS_DISCHARGE_MWH", "required_value": "45", "unit": "MWh in 3hrs", "section": "BESS Performance"},
            {"parameter": "Min Monthly Peak Supply", "code": "BESS_PEAK_SUPPLY", "required_value": ">=95", "unit": "%", "section": "BESS Performance"},
            {"parameter": "IEC 62619 Certification", "code": "CELL_CERTIFICATIONS", "required_value": "IEC 62619", "unit": "", "section": "Cell Standards"},
            {"parameter": "UL 1973 Certification", "code": "CELL_UL1973", "required_value": "Yes", "unit": "", "section": "Cell Standards"},
            {"parameter": "UL 9540A Thermal Runaway", "code": "CELL_UL9540A", "required_value": "Yes", "unit": "", "section": "Fire Safety"},
            {"parameter": "UN 38.3 Transport Test", "code": "CELL_UN383", "required_value": "Yes", "unit": "", "section": "Cell Standards"},
            {"parameter": "BIS Registration", "code": "CELL_BIS_CERT", "required_value": "Yes", "unit": "", "section": "Compliance"},
            {"parameter": "EMS Software Origin", "code": "EMS_ORIGIN", "required_value": "Indigenous (India)", "unit": "", "section": "EMS"},
            {"parameter": "EMS System Availability", "code": "EMS_AVAILABILITY", "required_value": ">=99.5", "unit": "%", "section": "EMS"},
            {"parameter": "SCADA Data Refresh Rate", "code": "EMS_REFRESH", "required_value": "<=1", "unit": "second", "section": "EMS"},
            {"parameter": "Communication Protocol", "code": "EMS_PROTOCOL", "required_value": "IEC 61850, Modbus TCP/IP", "unit": "", "section": "EMS"},
            {"parameter": "Black Start Capability", "code": "BESS_BLACK_START", "required_value": "Yes", "unit": "", "section": "Grid Support"},
            {"parameter": "Primary Frequency Response", "code": "BESS_PFR", "required_value": "Yes", "unit": "", "section": "Grid Support"},
            {"parameter": "Synthetic Inertia", "code": "BESS_INERTIA", "required_value": "Yes", "unit": "", "section": "Grid Support"},
            {"parameter": "Cyber Security Compliance", "code": "EMS_CYBERSEC", "required_value": "CEA Regulations", "unit": "", "section": "Compliance"},
            {"parameter": "Design Life", "code": "BESS_DESIGN_LIFE", "required_value": ">=12", "unit": "years", "section": "BESS"},
            {"parameter": "EMS Warranty", "code": "EMS_WARRANTY", "required_value": ">=10", "unit": "years", "section": "Warranty"},
        ]
    },
]

DOCUMENTS = [
    {"id": "doc-001", "document_type": "Compliance Sheet", "sheet_number": "TCS-001", "format": "PDF", "file_size": "2.4 MB", "file_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6", "created_at": "2026-03-10T14:00:00Z"},
    {"id": "doc-002", "document_type": "Technical Signal", "sheet_number": "TCS-004", "format": "PDF", "file_size": "3.8 MB", "file_hash": "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4", "created_at": "2026-03-12T09:30:00Z"},
]

TEMPLATES = [
    {"id": "tmpl-001", "name": "Battery Cell LFP - Standard", "component_type": "Cell", "version": "1.2", "parameter_count": 28},
    {"id": "tmpl-002", "name": "Battery Cell LFP - BIS Required", "component_type": "Cell", "version": "1.0", "parameter_count": 28},
]
