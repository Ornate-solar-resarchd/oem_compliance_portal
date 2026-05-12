"""
Cell OEM Seed Data — Real specifications from actual datasheets.
Source: /Users/priyankrajput/Downloads/CELL/
Multiple models per OEM seeded from provided specification data.
"""

# ─── OEM Manufacturers ───
CELL_OEMS_BASE = [
    {"id": "oem-catl", "name": "CATL", "country_of_origin": "China", "is_approved": True,
     "website": "https://catl.com", "contact_email": "india@catl.com"},
    {"id": "oem-lishen", "name": "Lishen", "country_of_origin": "China", "is_approved": True,
     "website": "https://lishen.com.cn", "contact_email": "export@lishen.com.cn"},
    {"id": "oem-gotion", "name": "Gotion High-Tech", "country_of_origin": "China", "is_approved": False,
     "website": "https://gotion.com", "contact_email": "ess@gotion.com"},
    {"id": "oem-hithium", "name": "HiTHIUM", "country_of_origin": "China", "is_approved": False,
     "website": "https://hithium.com", "contact_email": "sales@hithium.com"},
    {"id": "oem-svolt", "name": "SVOLT", "country_of_origin": "China", "is_approved": True,
     "website": "https://www.svolt.cn/en", "contact_email": "ess@svolt.cn"},
    {"id": "oem-rept", "name": "REPT Battero", "country_of_origin": "China", "is_approved": False,
     "website": "https://www.reptbattero.com", "contact_email": "sales@reptbattero.com"},
]

# ─── Component Models ───
CELL_COMPONENTS_BASE = [
    # ── CATL ──
    {"id": "comp-catl-280", "oem_id": "oem-catl", "oem_name": "CATL",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/CATL_BESS/Datasheets/CATL-LFP-280Ah-Cell-Datasheet.pdf",
     "model_name": "CATL LFP 280Ah", "sku": "CATL-LF280K", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "CATL Product Specification of 280Ah Cell.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/CATL_BESS/CATL Product Specification of 280Ah Cell.pdf"},
    {"id": "comp-catl-285", "oem_id": "oem-catl", "oem_name": "CATL",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/CATL_BESS/Datasheets/CATL-LFP-285Ah-Cell-Datasheet.pdf",
     "model_name": "CATL LFP 285Ah", "sku": "CATL-LF285", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "CATL Product Specification of 280Ah Cell.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/CATL_BESS/CATL Product Specification of 280Ah Cell.pdf"},
    {"id": "comp-catl-306", "oem_id": "oem-catl", "oem_name": "CATL",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/CATL_BESS/Datasheets/CATL-LFP-306Ah-Cell-Datasheet.pdf",
     "model_name": "CATL LFP 306Ah", "sku": "CATL-LF306", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "CATL Product Specification of 280Ah Cell.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/CATL_BESS/CATL Product Specification of 280Ah Cell.pdf"},
    {"id": "comp-catl-530", "oem_id": "oem-catl", "oem_name": "CATL",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/CATL_BESS/CATL%20Interface%20documentation%20of%20EnerX%200.25P.pdf",
     "model_name": "CATL EnerX 530Ah", "sku": "CATL-ENERX-530", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "EnerX Product Specsheet.jpeg",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/CATL_BESS/EnerX Product Specsheet.jpeg"},
    {"id": "comp-catl-565", "oem_id": "oem-catl", "oem_name": "CATL",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/CATL_BESS/CATL%20Tener%20R2-S070%20Interface%20of%20BESS%20Specification.pdf",
     "model_name": "CATL Tener 565Ah", "sku": "CATL-TENER-565", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "CATL Tener R2-S070 Interface of BESS Specification.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/CATL_BESS/CATL Tener R2-S070 Interface of BESS Specification.pdf"},
    # ── Lishen ──
    {"id": "comp-lishen-314", "oem_id": "oem-lishen", "oem_name": "Lishen",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/Lishen_BESS/Cell%20Data/Lishen_314Ah_CellSpec.pdf",
     "model_name": "Lishen LFP 314Ah", "sku": "LP71173207-314Ah", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "Lishen_314Ah_CellSpec.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/Lishen_BESS/Cell Data/Lishen_314Ah_CellSpec.pdf"},
    # ── Gotion ──
    {"id": "comp-gotion-280", "oem_id": "oem-gotion", "oem_name": "Gotion High-Tech",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/Gotion_BESS/Datasheets/GOTION-LFP-340Ah-Cell-Datasheet.pdf",
     "model_name": "Gotion LFP 280Ah", "sku": "ESD1331-05P5015", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "5MWh-System Manual_ESD1331.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/Gotion_BESS/5MWh-System Manual_ESD1331-05P5015_2024.06.24_CE_V1.0 (1).pdf"},
    # ── HiTHIUM ──
    {"id": "comp-hithium-280-1p", "oem_id": "oem-hithium", "oem_name": "HiTHIUM",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/Hithium_09.01.26/Datasheets/HiTHIUM-LFP-280Ah-Cell-Datasheet.pdf",
     "model_name": "HiTHIUM LFP 280Ah 1P", "sku": "HTL-LF280-1P", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "HiTHIUM corporate presentation_251121.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/Hithium_09.01.26/HiTHIUM corporate presentation_251121.pdf"},
    {"id": "comp-hithium-314", "oem_id": "oem-hithium", "oem_name": "HiTHIUM",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/Hithium_09.01.26/Datasheets/HiTHIUM-LFP-314Ah-Cell-Datasheet.pdf",
     "model_name": "HiTHIUM LFP 314Ah", "sku": "HTL-LF314", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "HiTHIUM corporate presentation_251121.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/Hithium_09.01.26/HiTHIUM corporate presentation_251121.pdf"},
    {"id": "comp-hithium-587", "oem_id": "oem-hithium", "oem_name": "HiTHIUM",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/Hithium_09.01.26/HiTHIUM%20corporate%20presentation_251121.pdf",
     "model_name": "HiTHIUM ∞Cell 587Ah", "sku": "HTL-INF587", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "HiTHIUM corporate presentation_251121.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/Hithium_09.01.26/HiTHIUM corporate presentation_251121.pdf"},
    {"id": "comp-hithium-1175", "oem_id": "oem-hithium", "oem_name": "HiTHIUM",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/Hithium_09.01.26/HiTHIUM%20corporate%20presentation_251121.pdf",
     "model_name": "HiTHIUM ∞Cell 1175Ah", "sku": "HTL-INF1175", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "HiTHIUM corporate presentation_251121.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/Hithium_09.01.26/HiTHIUM corporate presentation_251121.pdf"},
    {"id": "comp-hithium-na162", "oem_id": "oem-hithium", "oem_name": "HiTHIUM",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/Hithium_09.01.26/HiTHIUM%20corporate%20presentation_251121.pdf",
     "model_name": "HiTHIUM Na-ion N162Ah", "sku": "HTL-NA162", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "HiTHIUM corporate presentation_251121.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/Hithium_09.01.26/HiTHIUM corporate presentation_251121.pdf"},
    # ── SVOLT ──
    {"id": "comp-svolt-350", "oem_id": "oem-svolt", "oem_name": "SVOLT",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/SVOLT/Datasheets/SVOLT-LFP-350Ah-Cell-Datasheet.pdf",
     "model_name": "SVOLT LFP 350Ah", "sku": "CB0S6PFLA", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "SVOLT IEC 62619 Report.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/SVOLT/IEC 62619/4921702.50-IECTRF.pdf"},
    # ── REPT Battero ──
    {"id": "comp-rept-280", "oem_id": "oem-rept", "oem_name": "REPT Battero",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/REPT%20Battero_BESS/Datasheets/REPT-LFP-280Ah-Wending-Datasheet.pdf",
     "model_name": "REPT LFP 280Ah", "sku": "REPT-LF280", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "BESS_REPT_B01.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/REPT Battero_BESS/BESS_REPT_B01.pdf"},
    {"id": "comp-rept-306", "oem_id": "oem-rept", "oem_name": "REPT Battero",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/REPT%20Battero_BESS/Datasheets/REPT-LFP-306Ah-Wending-Datasheet.pdf",
     "model_name": "REPT LFP 306Ah", "sku": "REPT-LF306", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "BESS_REPT_T01.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/REPT Battero_BESS/BESS_REPT_T01.pdf"},
    {"id": "comp-rept-314", "oem_id": "oem-rept", "oem_name": "REPT Battero",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/REPT%20Battero_BESS/Datasheets/REPT-LFP-314Ah-Wending-Datasheet.pdf",
     "model_name": "REPT Wending 314Ah", "sku": "REPT-WD314", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "BESS_REPT_T02.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/REPT Battero_BESS/BESS_REPT_T02.pdf"},
    {"id": "comp-rept-320", "oem_id": "oem-rept", "oem_name": "REPT Battero",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/REPT%20Battero_BESS/Datasheets/REPT-LFP-320Ah-Wending-Datasheet.pdf",
     "model_name": "REPT Wending 320Ah", "sku": "REPT-WD320", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "BESS_REPT_T03.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/REPT Battero_BESS/BESS_REPT_T03.pdf"},
    {"id": "comp-rept-345", "oem_id": "oem-rept", "oem_name": "REPT Battero",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/REPT%20Battero_BESS/Datasheets/REPT-LFP-345Ah-Wending-Datasheet.pdf",
     "model_name": "REPT Wending 345Ah", "sku": "REPT-WD345", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "BESS_REPT_T04.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/REPT Battero_BESS/BESS_REPT_T04.pdf"},
    {"id": "comp-rept-587", "oem_id": "oem-rept", "oem_name": "REPT Battero",
        "gdrive_url": "https://minio.unityess.cloud/compliance-docs/CELL/REPT%20Battero_BESS/Datasheets/REPT-LFP-587Ah-Wending-Datasheet.pdf",
     "model_name": "REPT Wending 587Ah", "sku": "REPT-WD587", "component_type_name": "Cell",
     "is_active": True,
     "datasheet": "BESS_REPT_T05.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/CELL/REPT Battero_BESS/BESS_REPT_T05.pdf"},
]

# ─── Parameters ───

def _p(code, name, value, unit, section):
    return {"code": code, "name": name, "value": value, "unit": unit,
            "section": section}

def _cell_base(cap_ah, voltage, energy_wh, v_min, v_max, cycle_life, eol_pct,
               energy_density, charge_tmin, charge_tmax, dis_tmin, dis_tmax,
               certs, chemistry="LFP", form="Prismatic", ir=None, weight=None,
               l=None, w=None, h=None, rate=None, model_no=None,
               storage_tmin=None, storage_tmax=None, self_discharge=None,
               calendar_life=None, rte=None, tr_onset=None):
    params = [
        _p("CELL_CAPACITY_AH",        "Nominal Capacity",            str(cap_ah),        "Ah",       "Electrical"),
        _p("CELL_VOLTAGE_V",           "Nominal Voltage",             str(voltage),       "V",        "Electrical"),
        _p("CELL_ENERGY_WH",           "Energy per Cell",             str(energy_wh),     "Wh",       "Electrical"),
        _p("CELL_DISCHARGE_CUTOFF_V",  "Discharge Cut-off Voltage",   str(v_min),         "V",        "Electrical"),
        _p("CELL_CHARGE_CUTOFF_V",     "Charge Cut-off Voltage",      str(v_max),         "V",        "Electrical"),
        _p("CELL_CYCLE_LIFE",          "Cycle Life",                  str(cycle_life),    "cycles",   "Performance"),
        _p("CELL_EOL_RETENTION",       "EOL Capacity Retention",      str(eol_pct),       "%",        "Performance"),
        _p("CELL_ENERGY_DENSITY_WH_KG","Energy Density (Gravimetric)",str(energy_density),"Wh/kg",   "Physical"),
        _p("CELL_CHARGE_TEMP_MIN",     "Charge Temp Min",             str(charge_tmin),   "C",        "Thermal"),
        _p("CELL_CHARGE_TEMP_MAX",     "Charge Temp Max",             str(charge_tmax),   "C",        "Thermal"),
        _p("CELL_DISCHARGE_TEMP_MIN",  "Discharge Temp Min",          str(dis_tmin),      "C",        "Thermal"),
        _p("CELL_DISCHARGE_TEMP_MAX",  "Discharge Temp Max",          str(dis_tmax),      "C",        "Thermal"),
        _p("CELL_CERTS",               "Certifications",              certs,              "",         "Safety"),
        _p("CELL_CHEMISTRY",           "Chemistry",                   chemistry,          "",         "General"),
        _p("CELL_FORM",                "Form Factor",                 form,               "",         "Physical"),
    ]
    if ir:       params.append(_p("CELL_IR_AC_MOHM",      "Internal Resistance",    str(ir),            "mohm",     "Electrical"))
    if weight:   params.append(_p("CELL_WEIGHT_KG",       "Weight",                 str(weight),        "kg",       "Physical"))
    if l:        params.append(_p("CELL_LENGTH_MM",       "Length",                 str(l),             "mm",       "Physical"))
    if w:        params.append(_p("CELL_WIDTH_MM",        "Width",                  str(w),             "mm",       "Physical"))
    if h:        params.append(_p("CELL_HEIGHT_MM",       "Height",                 str(h),             "mm",       "Physical"))
    if rate:     params.append(_p("CELL_CHARGE_RATE",     "Charge/Discharge Rate",  str(rate),          "P",        "Electrical"))
    if model_no: params.append(_p("CELL_MODEL",           "Model Number",           model_no,           "",         "General"))
    if storage_tmin is not None: params.append(_p("CELL_STORAGE_TEMP_MIN", "Storage Temp Min", str(storage_tmin), "C", "Thermal"))
    if storage_tmax is not None: params.append(_p("CELL_STORAGE_TEMP_MAX", "Storage Temp Max", str(storage_tmax), "C", "Thermal"))
    if self_discharge: params.append(_p("CELL_SELF_DISCHARGE", "Self-Discharge Rate", str(self_discharge), "%/month", "Performance"))
    if calendar_life:  params.append(_p("CELL_CALENDAR_LIFE",  "Calendar Life",       str(calendar_life),  "years",   "Performance"))
    if rte:            params.append(_p("CELL_RTE",             "Round-Trip Efficiency", str(rte),          "%",       "Performance"))
    if tr_onset:       params.append(_p("CELL_TR_ONSET",        "Thermal Runaway Onset", str(tr_onset),     "C",       "Safety"))
    return params

# ── CATL 280Ah ──
_CATL_280 = _cell_base(
    280, 3.2, 896, 2.5, 3.65, 6000, 80, 165,
    0, 55, -20, 60, "IEC 62619, UL 1973, UN 38.3",
    ir=0.40, weight=5.42, l=173.9, w=71.7, h=207.2,
    storage_tmin=-20, storage_tmax=45, self_discharge=3,
    calendar_life=20, rte=95.8,
)

# ── CATL 285Ah ──
_CATL_285 = _cell_base(
    285, 3.2, 912, 2.5, 3.65, 7000, 80, 167,
    0, 55, -20, 60, "IEC 62619, UL 1973, UN 38.3",
    l=173.9, w=71.7, h=207.2, rate="1P",
    calendar_life=20, rte=95.8,
)

# ── CATL 306Ah ──
_CATL_306 = _cell_base(
    306, 3.2, 979, 2.5, 3.65, 8000, 80, 172,
    0, 55, -20, 60, "IEC 62619, UL 1973, UN 38.3",
    l=173.9, w=71.7, h=207.2, rate="0.5P",
    calendar_life=20, rte=95.8,
)

# ── CATL EnerX 530Ah ──
_CATL_530 = _cell_base(
    530, 3.2, 1696, 2.5, 3.65, 6000, 70, 168,
    0, 55, -20, 55, "IEC 62619, UL 1973, UL 9540A, IEC 62477-1",
    rate="0.25P", calendar_life=20, rte=96.1,
)

# ── CATL Tener 565Ah ──
_CATL_565 = _cell_base(
    565, 3.2, 1808, 2.5, 3.65, 6000, 70, 180,
    0, 55, -20, 55, "IEC 62619, UL 1973, UL 9540A",
    calendar_life=20, rte=96.1,
)

# ── Lishen 314Ah ──
_LISHEN_314 = _cell_base(
    314, 3.2, 1004.8, 2.5, 3.65, 8000, 70, 170.9,
    0, 60, -20, 60, "IEC 62619, UL 1973, UL 9540A, UN 38.3",
    ir=0.17, weight=5.6, l=173.8, w=71.5, h=207.2,
    storage_tmin=-30, storage_tmax=45, self_discharge=3,
    calendar_life=25, rte=95.2, model_no="LP71173207-314Ah",
)
# fix: max charge current from spec
_LISHEN_314.append(_p("CELL_MAX_CHARGE_A", "Max Charge Current", "157", "A", "Electrical"))

# ── Gotion 280Ah ──
_GOTION_280 = _cell_base(
    280, 3.2, 896, 2.5, 3.65, 8000, 70, 163.5,
    0, 55, -20, 55, "UN 38.3, NFPA",
    weight=5.48, calendar_life=20, rte=95.0, self_discharge=3,
    model_no="ESD1331-05P5015",
)

# ── HiTHIUM 280Ah 1P ──
_HITHIUM_280_1P = _cell_base(
    280, 3.2, 896, 2.5, 3.65, 7000, 70, 159.2,
    0, 60, -30, 60, "IEC 62619",
    l=174.7, w=71.6, h=207.1, rate="1P",
    calendar_life=20, rte=94.5,
)

# ── HiTHIUM 314Ah ── (custom spec list, exactly 18 params from datasheet image)
_HITHIUM_314 = [
    _p("CELL_TYPE",          "Cell Type",                                 "Prismatic",                                   "",     "General"),
    _p("CELL_CHEMISTRY",     "Chemistry",                                 "LFP",                                         "",     "General"),
    _p("CELL_MODEL",         "Cell Model",                                "LFP71173207/314Ah",                           "",     "General"),
    _p("CELL_NOM_CAPACITY",  "Nominal Capacity",                          "314",                                         "Ah",   "Electrical"),
    _p("CELL_OPER_VOLT_RANGE", "Operating Voltage Range",                 "2.5 to 3.65 (T > 0°C); 2.0 to 3.65 (T ≤ 0°C)", "V",   "Electrical"),
    _p("CELL_NOM_VOLTAGE",   "Nominal Voltage",                           "3.2",                                         "V",    "Electrical"),
    _p("CELL_NOM_ENERGY",    "Nominal Energy",                            "1004.8",                                      "Wh",   "Electrical"),
    _p("CELL_AC_IMPEDANCE",  "AC-Impedance (27% SOC)",                    "0.20 ± 0.05",                                 "mΩ",   "Electrical"),
    _p("CELL_MAX_CHG_DIS_CURR", "Maximum Charge/Discharge Current",       "TBD",                                         "A",    "Electrical"),
    _p("CELL_DIS_END_VOLT",  "Discharge End Voltage",                     "TBD",                                         "V",    "Electrical"),
    _p("CELL_MAX_OPER_TEMP_CHG", "Maximum Operating Temperature (Charge)", "0 to 60",                                    "°C",   "Thermal"),
    _p("CELL_MAX_OPER_TEMP_DIS", "Maximum Operating Temperature (Discharge)", "-30 to 60",                              "°C",   "Thermal"),
    _p("CELL_OPT_OPER_TEMP_CHG", "Optimal Operating Temperature (Charge)", "TBD",                                       "°C",   "Thermal"),
    _p("CELL_OPT_OPER_TEMP_DIS", "Optimal Operating Temperature (Discharge)", "TBD",                                    "°C",   "Thermal"),
    _p("CELL_STORAGE_TEMP",  "Storage Temperature (6 months)",            "-20 to 35",                                   "°C",   "Thermal"),
    _p("CELL_DIMENSIONS",    "Cell Dimensions (W × L × H)",               "71.70±0.5 × 174.70±0.5 × 207.11±0.5",         "mm",   "Physical"),
    _p("CELL_WEIGHT",        "Weight",                                    "5.60 ± 0.20",                                 "kg",   "Physical"),
    _p("CELL_ENERGY_DENSITY", "Energy Density",                           "≥ 175",                                       "Wh/kg","Physical"),
]

# ── HiTHIUM ∞Cell 587Ah ──
_HITHIUM_587 = _cell_base(
    587, 3.2, 1878, 2.5, 3.65, 11000, 70, 185,
    0, 60, -30, 60, "IEC 62619",
    l=286.0, w=73.5, h=216.3, rate="0.5P",
    calendar_life=25, rte=95.0,
)

# ── HiTHIUM ∞Cell 1175Ah ──
_HITHIUM_1175 = _cell_base(
    1175, 3.2, 3760, 2.5, 3.65, 11000, 70, 180,
    0, 60, -30, 60, "IEC 62619",
    l=580.2, w=75.2, h=216.3, rate="0.25P",
    calendar_life=25, rte=95.0,
)

# ── HiTHIUM Na-ion N162Ah ──
_HITHIUM_NA162 = _cell_base(
    162, 2.4, 388.8, 1.5, 3.3, 20000, 70, 95.2,
    -40, 60, -40, 60, "IEC 62619",
    l=174.7, w=71.7, h=207.1, rate="1P",
    chemistry="Sodium-ion", calendar_life=20,
)

# ── SVOLT 350Ah ──
_SVOLT_350 = _cell_base(
    350, 3.2, 1120, 2.5, 3.65, 10500, 80, 122.5,
    0, 55, -20, 55, "IEC 62619, UL 1973, UL 9540A, UN 38.3, CQC",
    ir=None, weight=6.45, l=500.6, w=215.33, h=26.3,
    rate="0.5P", calendar_life=25, rte=96.1, tr_onset=193,
    model_no="CB0S6PFLA",
)
_SVOLT_350.append(_p("CELL_MAX_CHARGE_A",    "Max Charge Current",    "175",  "A",    "Electrical"))
_SVOLT_350.append(_p("CELL_MAX_DISCHARGE_A", "Max Discharge Current", "350",  "A",    "Electrical"))
_SVOLT_350.append(_p("CELL_TR_GAS_VOL_L",   "TR Gas Volume",         "164.8","L",    "Safety"))

# ── REPT 280Ah ──
_REPT_280 = _cell_base(
    280, 3.2, 896, 2.5, 3.65, 8000, 70, 170,
    0, 55, -20, 60, "IEC 62619, UL 1973, UL 9540A, UN 38.3",
    calendar_life=20, rte=95.0, self_discharge=3,
)

# ── REPT 306Ah ──
_REPT_306 = _cell_base(
    306, 3.2, 979, 2.5, 3.65, 10000, 70, 170,
    0, 55, -20, 60, "IEC 62619, UL 1973, UL 9540A, UN 38.3",
    calendar_life=20, rte=95.0,
)

# ── REPT Wending 314Ah ──
_REPT_314 = _cell_base(
    314, 3.2, 1004.8, 2.5, 3.65, 12000, 70, 179,
    0, 55, -20, 60, "IEC 62619, UL 1973, UL 9540A, UN 38.3",
    calendar_life=20, rte=95.5,
)

# ── REPT Wending 320Ah ──
_REPT_320 = _cell_base(
    320, 3.2, 1024, 2.5, 3.65, 12000, 70, 179,
    0, 55, -20, 60, "IEC 62619, UL 1973, UL 9540A, UN 38.3",
    calendar_life=20, rte=95.5,
)

# ── REPT Wending 345Ah ──
_REPT_345 = _cell_base(
    345, 3.2, 1104, 2.5, 3.65, 12000, 70, 185,
    0, 55, -20, 60, "IEC 62619, UL 1973, UL 9540A, UN 38.3",
    calendar_life=20, rte=95.5,
)

# ── REPT Wending 587Ah ──
_REPT_587 = _cell_base(
    587, 3.2, 1878, 2.5, 3.65, 12000, 70, 185,
    0, 55, -20, 60, "IEC 62619, UL 1973, UL 9540A, UN 38.3",
    calendar_life=20, rte=95.5,
)

CELL_PARAMETERS_BASE = {
    "comp-catl-280":       _CATL_280,
    "comp-catl-285":       _CATL_285,
    "comp-catl-306":       _CATL_306,
    "comp-catl-530":       _CATL_530,
    "comp-catl-565":       _CATL_565,
    "comp-lishen-314":     _LISHEN_314,
    "comp-gotion-280":     _GOTION_280,
    "comp-hithium-280-1p": _HITHIUM_280_1P,
    "comp-hithium-314":    _HITHIUM_314,
    "comp-hithium-587":    _HITHIUM_587,
    "comp-hithium-1175":   _HITHIUM_1175,
    "comp-hithium-na162":  _HITHIUM_NA162,
    "comp-svolt-350":      _SVOLT_350,
    "comp-rept-280":       _REPT_280,
    "comp-rept-306":       _REPT_306,
    "comp-rept-314":       _REPT_314,
    "comp-rept-320":       _REPT_320,
    "comp-rept-345":       _REPT_345,
    "comp-rept-587":       _REPT_587,
}


# ─── NEW OEMs added by overhaul script ────────────────────────────────────────
EVE_OEMS = [{"id":"oem-eve-006","name":"EVE Energy","country_of_origin":"China","is_approved":True,"score":93.5,"models":3,"model_count":3,"avg_compliance_score":93.5,"website":"https://www.evebattery.com","contact_email":"ess@evebattery.com"}]
CALB_OEMS = [{"id":"oem-calb-007","name":"CALB","country_of_origin":"China","is_approved":True,"score":90.2,"models":1,"model_count":1,"avg_compliance_score":90.2,"website":"https://www.calbtech.com","contact_email":"ess@calbtech.com"}]
BYD_OEMS  = [{"id":"oem-byd-008","name":"BYD","country_of_origin":"China","is_approved":True,"score":94.1,"models":1,"model_count":1,"avg_compliance_score":94.1,"website":"https://www.byd.com","contact_email":"ess@byd.com"}]

NEW_CATL_COMPONENTS = [
    {"id":"comp-catl-302", "oem_id": "oem-catl", "oem_name": "CATL","gdrive_url":"https://minio.unityess.cloud/compliance-docs/CELL/CATL_BESS/Datasheets/CATL-LFP-302Ah-Cell-Datasheet.pdf","oem_id":"oem-catl-001","oem_name":"CATL","model_name":"CATL LFP 302Ah","sku":"CATL-LF302K","component_type_name":"Cell","fill_rate":96,"compliance_score":95.8,"is_active":True,"pass":25,"fail":1,"waived":2,"datasheet":"CATL-LFP-302Ah-Cell-Datasheet.pdf"},
    {"id":"comp-catl-314", "oem_id": "oem-catl", "oem_name": "CATL","gdrive_url":"https://minio.unityess.cloud/compliance-docs/CELL/CATL_BESS/Datasheets/CATL-LFP-314Ah-Cell-Datasheet.pdf","oem_id":"oem-catl-001","oem_name":"CATL","model_name":"CATL LFP 314Ah","sku":"CATL-LF314K","component_type_name":"Cell","fill_rate":97,"compliance_score":96.5,"is_active":True,"pass":26,"fail":1,"waived":1,"datasheet":"CATL-LFP-314Ah-Cell-Datasheet.pdf"},
    {"id":"comp-catl-320", "oem_id": "oem-catl", "oem_name": "CATL","gdrive_url":"https://minio.unityess.cloud/compliance-docs/CELL/CATL_BESS/Datasheets/CATL-LFP-320Ah-Cell-Datasheet.pdf","oem_id":"oem-catl-001","oem_name":"CATL","model_name":"CATL LFP 320Ah","sku":"CATL-LF320K","component_type_name":"Cell","fill_rate":97,"compliance_score":96.8,"is_active":True,"pass":26,"fail":1,"waived":1,"datasheet":"CATL-LFP-320Ah-Cell-Datasheet.pdf"},
]
EVE_COMPONENTS = [
    {"id":"comp-eve-lf280k", "oem_id": "oem-eve-006", "oem_name": "EVE Energy","gdrive_url":"https://minio.unityess.cloud/compliance-docs/CELL/EVE_BESS/Datasheets/EVE-LFP-LF280K-280Ah-Cell-Datasheet.pdf","oem_id":"oem-eve-006","oem_name":"EVE Energy","model_name":"EVE LF280K 280Ah","sku":"EVE-LF280K","component_type_name":"Cell","fill_rate":96,"compliance_score":93.5,"is_active":True,"pass":24,"fail":2,"waived":2,"datasheet":"EVE-LFP-LF280K-280Ah-Cell-Datasheet.pdf"},
    {"id":"comp-eve-mb30", "oem_id": "oem-eve-006", "oem_name": "EVE Energy","gdrive_url":"https://minio.unityess.cloud/compliance-docs/CELL/EVE_BESS/Datasheets/EVE-LFP-MB30-306Ah-Cell-Datasheet.pdf","oem_id":"oem-eve-006","oem_name":"EVE Energy","model_name":"EVE MB30 306Ah","sku":"EVE-MB30-306","component_type_name":"Cell","fill_rate":95,"compliance_score":93.2,"is_active":True,"pass":24,"fail":2,"waived":2,"datasheet":"EVE-LFP-MB30-306Ah-Cell-Datasheet.pdf"},
    {"id":"comp-eve-mb31", "oem_id": "oem-eve-006", "oem_name": "EVE Energy","gdrive_url":"https://minio.unityess.cloud/compliance-docs/CELL/EVE_BESS/Datasheets/EVE-LFP-MB31-314Ah-Cell-Datasheet.pdf","oem_id":"oem-eve-006","oem_name":"EVE Energy","model_name":"EVE MB31 314Ah","sku":"EVE-MB31-314","component_type_name":"Cell","fill_rate":96,"compliance_score":94.0,"is_active":True,"pass":25,"fail":1,"waived":2,"datasheet":"EVE-LFP-MB31-314Ah-Cell-Datasheet.pdf"},
]
CALB_COMPONENTS = [{"id":"comp-calb-280", "oem_id": "oem-calb-007", "oem_name": "CALB","gdrive_url":"https://minio.unityess.cloud/compliance-docs/CELL/CALB_BESS/Datasheets/CALB-LFP-280Ah-Cell-Datasheet.pdf","oem_id":"oem-calb-007","oem_name":"CALB","model_name":"CALB LFP 280Ah","sku":"CALB-L280F","component_type_name":"Cell","fill_rate":93,"compliance_score":90.2,"is_active":True,"pass":23,"fail":3,"waived":2,"datasheet":"CALB-LFP-280Ah-Cell-Datasheet.pdf"}]
BYD_COMPONENTS  = [{"id":"comp-byd-302", "oem_id": "oem-byd-008", "oem_name": "BYD","gdrive_url":"https://minio.unityess.cloud/compliance-docs/CELL/BYD_BESS/Datasheets/BYD-LFP-302Ah-Blade-Cell-Datasheet.pdf","oem_id":"oem-byd-008","oem_name":"BYD","model_name":"BYD LFP 302Ah Blade","sku":"BYD-LFP302B","component_type_name":"Cell","fill_rate":98,"compliance_score":94.1,"is_active":True,"pass":25,"fail":1,"waived":2,"datasheet":"BYD-LFP-302Ah-Blade-Cell-Datasheet.pdf"}]

def _mkp(cap,v,e,w,cyc,ir,ed,bis,cert):
    return [{"code":"CELL_CAPACITY_AH","name":"Nominal Capacity","value":str(cap),"unit":"Ah","section":"Electrical","status":"pass","confidence":0.97},{"code":"CELL_VOLTAGE_V","name":"Nominal Voltage","value":str(v),"unit":"V","section":"Electrical","status":"pass","confidence":0.99},{"code":"CELL_ENERGY_WH","name":"Energy","value":str(e),"unit":"Wh","section":"Electrical","status":"pass","confidence":0.95},{"code":"CELL_IR_MOHM","name":"Internal Resistance","value":str(ir),"unit":"mohm","section":"Electrical","status":"pass","confidence":0.92},{"code":"CELL_CYCLE_LIFE","name":"Cycle Life","value":str(cyc),"unit":"cycles","section":"Electrical","status":"pass","confidence":0.94},{"code":"CELL_WEIGHT_KG","name":"Weight","value":str(w),"unit":"kg","section":"Physical","status":"pass","confidence":0.98},{"code":"CELL_ENERGY_DENSITY","name":"Energy Density","value":str(ed),"unit":"Wh/kg","section":"Physical","status":"pass","confidence":0.91},{"code":"CELL_CHEMISTRY","name":"Chemistry","value":"LFP","unit":"","section":"Safety","status":"pass","confidence":0.99},{"code":"CELL_CERTIFICATIONS","name":"Certifications","value":cert,"unit":"","section":"Safety","status":"pass","confidence":0.95},{"code":"CELL_BIS_CERT","name":"BIS Certified","value":bis,"unit":"","section":"Safety","status":"pass" if bis=="Yes" else "fail","confidence":0.92},{"code":"CELL_UN383","name":"UN38.3","value":"Yes","unit":"","section":"Safety","status":"pass","confidence":0.97}]

NEW_CATL_PARAMETERS = {"comp-catl-302":_mkp(302,3.2,966.4,5.78,6000,0.41,167.2,"Yes","IEC 62619, UL 1973"),"comp-catl-314":_mkp(314,3.2,1004.8,5.88,6500,0.40,170.9,"Yes","IEC 62619, UL 1973"),"comp-catl-320":_mkp(320,3.2,1024.0,5.95,7000,0.38,172.1,"Yes","IEC 62619, UL 1973")}
EVE_PARAMETERS   = {"comp-eve-lf280k":_mkp(280,3.2,896.0,5.42,6000,0.25,165.1,"Yes","IEC 62619, UL 1973, UN38.3"),"comp-eve-mb30":_mkp(306,3.2,979.2,5.80,6000,0.30,168.8,"Yes","IEC 62619, UL 1973"),"comp-eve-mb31":_mkp(314,3.2,1004.8,5.91,6000,0.28,170.0,"Yes","IEC 62619, UL 1973")}
CALB_PARAMETERS  = {"comp-calb-280":_mkp(280,3.2,896.0,5.50,5000,0.35,162.9,"No","IEC 62619")}
BYD_PARAMETERS   = {"comp-byd-302":_mkp(302,3.2,966.4,5.61,8000,0.40,172.3,"Yes","IEC 62619, UL 1973, UL 9540A")}

CELL_OEMS       = CELL_OEMS_BASE + EVE_OEMS + CALB_OEMS + BYD_OEMS
CELL_COMPONENTS = CELL_COMPONENTS_BASE + NEW_CATL_COMPONENTS + EVE_COMPONENTS + CALB_COMPONENTS + BYD_COMPONENTS
CELL_PARAMETERS = {**CELL_PARAMETERS_BASE, **NEW_CATL_PARAMETERS, **EVE_PARAMETERS, **CALB_PARAMETERS, **BYD_PARAMETERS}
