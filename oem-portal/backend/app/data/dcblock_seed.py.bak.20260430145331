"""
DC Block / BESS Container Seed Data.
Source: /Users/priyankrajput/Downloads/BESS/
Manufacturers: CATL, Hexon, Lishen, SVOLT
"""

DCBLOCK_OEMS = [
    {"id": "oem-catl-bess",   "name": "CATL (BESS)",   "country_of_origin": "China",
     "is_approved": True,
     "website": "https://catl.com", "contact_email": "india@catl.com"},
    {"id": "oem-hexon",       "name": "Hexon",          "country_of_origin": "China",
     "is_approved": False,
     "website": "https://hexon.com", "contact_email": "sales@hexon.com"},
    {"id": "oem-lishen-bess", "name": "Lishen (BESS)",  "country_of_origin": "China",
     "is_approved": True,
     "website": "https://lishen.com.cn", "contact_email": "export@lishen.com.cn"},
    {"id": "oem-svolt-bess",  "name": "SVOLT (BESS)",   "country_of_origin": "China",
     "is_approved": True,
     "website": "https://www.svolt.cn/en", "contact_email": "ess@svolt.cn"},
]

DCBLOCK_COMPONENTS = [
    # ── CATL ──
    {"id": "comp-catl-enerx",      "oem_id": "oem-catl-bess",   "oem_name": "CATL (BESS)",
     "model_name": "CATL EnerX 0.25P (20ft Container)", "sku": "ENERX-0.25P",
     "component_type_name": "DC Block",
     "is_active": True,
     "datasheet": "CATL Interface documentation of EnerX 0.25P.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/BESS/CATL_BESS/CATL Interface documentation of EnerX 0.25P.pdf"},
    {"id": "comp-catl-tener",      "oem_id": "oem-catl-bess",   "oem_name": "CATL (BESS)",
     "model_name": "CATL Tener R2-S070 (Outdoor Rack)", "sku": "TENER-R2-S070",
     "component_type_name": "DC Block",
     "is_active": True,
     "datasheet": "CATL Tener R2-S070 Interface of BESS Specification.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/BESS/CATL_BESS/CATL Tener R2-S070 Interface of BESS Specification.pdf"},
    # ── Hexon ──
    {"id": "comp-hexon-125-261",   "oem_id": "oem-hexon",       "oem_name": "Hexon",
     "model_name": "Hexon HESS-125-261 (Liquid Cooled Cabinet)", "sku": "HESS-125-261",
     "component_type_name": "DC Block",
     "is_active": True,
     "datasheet": "Hexon_Technical Product Specification-125-261.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/BESS/HEXON_BESS/Hexon_Technical Product Specification-125-261.pdf"},
    {"id": "comp-hexon-215-418",   "oem_id": "oem-hexon",       "oem_name": "Hexon",
     "model_name": "Hexon HESS-215-418 (Liquid Cooled Cabinet)", "sku": "HESS-215-418-CN",
     "component_type_name": "DC Block",
     "is_active": True,
     "datasheet": "215_418kWh.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/BESS/HEXON_BESS/215_418kWh.pdf"},
    {"id": "comp-hexon-5015",      "oem_id": "oem-hexon",       "oem_name": "Hexon",
     "model_name": "Hexon HEMERA HBAT-5015-15 (20ft Container)", "sku": "HBAT-5015-15",
     "component_type_name": "DC Block",
     "is_active": True,
     "datasheet": "BESS_Hexon_T01.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/BESS/HEXON_BESS/BESS_Hexon_T01.pdf"},
    {"id": "comp-hexon-eos",       "oem_id": "oem-hexon",       "oem_name": "Hexon",
     "model_name": "Hexon EOS All-in-One C&I (100kW/215kWh)", "sku": "SOLAESS-100-215",
     "component_type_name": "DC Block",
     "is_active": True,
     "datasheet": "EOS All-in-One C&I Datasheet.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/BESS/HEXON_BESS/EOS  All-in-One C&I Energy Storage System Datasheet- v1.0.pdf"},
    {"id": "comp-hexon-eosplus",   "oem_id": "oem-hexon",       "oem_name": "Hexon",
     "model_name": "Hexon EOS+ Modular (125kW/261kWh)", "sku": "SOLAES-125-261",
     "component_type_name": "DC Block",
     "is_active": True,
     "datasheet": "EOS+ Modular Datasheet.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/BESS/HEXON_BESS/EOS+ Modular Solar Energy Storage System Datasheet- v1.0.pdf"},
    # ── Lishen ──
    {"id": "comp-lishen-5mwh",     "oem_id": "oem-lishen-bess", "oem_name": "Lishen (BESS)",
     "model_name": "Lishen ESS-ES5016C 5MWh (20ft Container)", "sku": "ESS-ES5016C",
     "component_type_name": "DC Block",
     "is_active": True,
     "datasheet": "5MWh Liquid Cooling BESS Container Specification.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/BESS/Lishen_BESS/5MWh Liquid Cooling BESS Container Specification _ Rev4_20250827-V2.pdf"},
    # ── SVOLT ──
    {"id": "comp-svolt-5160",      "oem_id": "oem-svolt-bess",  "oem_name": "SVOLT (BESS)",
     "model_name": "SVOLT CE-L-5160-B1-EU Short Blade II (20ft)", "sku": "CE-L-5160-B1-EU",
     "component_type_name": "DC Block",
     "is_active": True,
     "datasheet": "5160kWh Liquid Cooling Energy Storage Container.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/BESS/SVolt_BESS/03 5160kWh Liquid Cooling Energy Storage Container.pdf"},
]


def _p(code, name, value, unit, section):
    return {"code": code, "name": name, "value": value, "unit": unit,
            "section": section}


# ─────────────────────────────────────────────────────────────────────
# CATL EnerX 0.25P — 5,644 kWh 20ft Container
# ─────────────────────────────────────────────────────────────────────
_CATL_ENERX = [
    _p("DC_RATED_ENERGY_KWH",    "Rated Energy",             "5644.29",      "kWh",  "Electrical"),
    _p("DC_RATED_VOLTAGE_V",     "Rated DC Voltage",         "1331.2",       "V",    "Electrical"),
    _p("DC_VOLTAGE_RANGE",       "DC Voltage Range",         "1040-1500",    "V",    "Electrical"),
    _p("DC_CONFIGURATION",       "Configuration",            "4P2P416S",     "",     "Electrical"),
    _p("DC_CELL_CAPACITY_AH",    "Cell Capacity",            "530",          "Ah",   "Electrical"),
    _p("DC_CHARGE_RATE",         "Charge/Discharge Rate",    "≤0.25P",       "",     "Electrical"),
    _p("DC_EOL_SOH",             "EOL SOH Target",           "70",           "%",    "Performance"),
    _p("DC_FORM_FACTOR",         "Form Factor",              "20ft container","",    "Physical"),
    _p("DC_DIMENSIONS",          "Dimensions (L×W×H)",       "6058×2438×2896","mm",  "Physical"),
    _p("DC_WEIGHT_T",            "Weight",                   "45",           "t",    "Physical"),
    _p("DC_COOLING",             "Cooling Type",             "Liquid (50% EG + 50% DI water)","","Thermal"),
    _p("DC_OP_TEMP_MIN",         "Operating Temp Min",       "-35",          "°C",   "Thermal"),
    _p("DC_OP_TEMP_MAX",         "Operating Temp Max",       "55",           "°C",   "Thermal"),
    _p("DC_STORAGE_TEMP",        "Storage Temp Range",       "-35 to 60",    "°C",   "Thermal"),
    _p("DC_ALTITUDE_M",          "Max Altitude (no derating)","4000",        "m",    "Environmental"),
    _p("DC_IP_RATING",           "IP Rating",                "IP55",         "",     "Protection"),
    _p("DC_HUMIDITY",            "Humidity",                 "<95%, no condensing","","Environmental"),
    _p("DC_NOISE_DB",            "Noise Level",              "<85",          "dBA",  "Physical"),
    _p("DC_COATING",             "Enclosure Coating",        "ISO 12944 C4 (C5 opt)","","Physical"),
    _p("DC_AUX_POWER",           "Auxiliary Power",          "AUX1: 380-480VAC 34.5kW; AUX2: 110-230VAC 0.5kW","","Electrical"),
    _p("DC_FIRE_SUPPRESSION",    "Fire Suppression",         "4-level: alarm + ventilation (NFPA 69/ATEX) + aerosol (12 units) + water spray (NFPA 855)","","Safety"),
    _p("DC_FIRE_DETECTORS",      "Fire Detectors",           "Smoke(3), Heat(2), H2(1), CO(1)","","Safety"),
    _p("DC_BMS_LEVELS",          "BMS Architecture",         "Module (MBMU) + Rack (SBMU)","",  "BMS"),
    _p("DC_COMMS",               "Communication",            "CAN 2.0, Fiber, Ethernet, RS485","","Communication"),
    _p("DC_CERTS",               "Certifications",           "UL 1973, UL 9540A, IEC 62619, IEC 62477-1, IEC 61000-6-2/6-4","","Safety"),
    _p("DC_MODULE_IP",           "Module IP Rating",         "IP67",         "",     "Protection"),
    _p("DC_COOLING_CAPACITY_KW", "Cooling Capacity",         "13.4",         "kW",   "Thermal"),
]

# ─────────────────────────────────────────────────────────────────────
# CATL Tener R2-S070 — 706 kWh Outdoor Rack
# ─────────────────────────────────────────────────────────────────────
_CATL_TENER = [
    _p("DC_RATED_ENERGY_KWH",    "Rated Energy",             "705.536",      "kWh",  "Electrical"),
    _p("DC_RATED_VOLTAGE_V",     "Rated DC Voltage",         "1331.2",       "V",    "Electrical"),
    _p("DC_VOLTAGE_RANGE",       "DC Voltage Range",         "1040-1500",    "V",    "Electrical"),
    _p("DC_CONFIGURATION",       "Configuration",            "1P416S (8 modules of 1P52S)","","Electrical"),
    _p("DC_CELL_CAPACITY_AH",    "Cell Capacity",            "530",          "Ah",   "Electrical"),
    _p("DC_CHARGE_RATE",         "Charge/Discharge Rate",    "≤0.5P",        "",     "Electrical"),
    _p("DC_EOL_SOH",             "EOL SOH Target",           "70",           "%",    "Performance"),
    _p("DC_FORM_FACTOR",         "Form Factor",              "Outdoor rack", "",     "Physical"),
    _p("DC_DIMENSIONS",          "Dimensions (L×W×H)",       "1700×1500×2425","mm",  "Physical"),
    _p("DC_WEIGHT_T",            "Weight",                   "6.0",          "t",    "Physical"),
    _p("DC_COOLING",             "Cooling Type",             "Liquid (50% EG + 50% DI water)","","Thermal"),
    _p("DC_OP_TEMP_MIN",         "Operating Temp Min",       "-35",          "°C",   "Thermal"),
    _p("DC_OP_TEMP_MAX",         "Operating Temp Max",       "55",           "°C",   "Thermal"),
    _p("DC_STORAGE_TEMP",        "Storage Temp Range",       "-40 to 60",    "°C",   "Thermal"),
    _p("DC_ALTITUDE_M",          "Max Altitude (no derating)","4000",        "m",    "Environmental"),
    _p("DC_IP_RATING",           "IP Rating",                "IP66",         "",     "Protection"),
    _p("DC_NOISE_DB",            "Noise Level",              "≤65",          "dBA",  "Physical"),
    _p("DC_COATING",             "Enclosure Coating",        "ISO 12944 C4 (C5 opt)","","Physical"),
    _p("DC_FIRE_SUPPRESSION",    "Fire Suppression",         "4-level: alarm + ventilation (NFPA 69) + aerosol + dry pipe (opt)","","Safety"),
    _p("DC_BMS_LEVELS",          "BMS Architecture",         "MBMU (module) + SBMU (rack)","","BMS"),
    _p("DC_COMMS",               "Communication",            "CAN 2.0, Ethernet/Fiber","","Communication"),
    _p("DC_CERTS",               "Certifications",           "UN 38.3, UL 1973, UL 9540A, IEC 62619, IEC 62477-1, IEC 62933-5-2, IEC 63056, NFPA 855","","Safety"),
    _p("DC_MODULE_IP",           "Module IP Rating",         "IP67",         "",     "Protection"),
    _p("DC_COOLING_CAPACITY_KW", "Cooling Capacity",         "10",           "kW",   "Thermal"),
]

# ─────────────────────────────────────────────────────────────────────
# Hexon HESS-125-261 — 261 kWh Liquid Cooled Cabinet
# ─────────────────────────────────────────────────────────────────────
_HEXON_125_261 = [
    _p("DC_RATED_ENERGY_KWH",    "Rated Energy",             "261.248",      "kWh",  "Electrical"),
    _p("DC_RATED_VOLTAGE_V",     "Rated DC Voltage",         "832",          "V",    "Electrical"),
    _p("DC_VOLTAGE_RANGE",       "DC Voltage Range",         "650-949",      "V",    "Electrical"),
    _p("DC_RATED_POWER_KW",      "Rated Power",              "125",          "kW",   "Electrical"),
    _p("DC_MAX_POWER_KW",        "Max Power",                "137.5",        "kW",   "Electrical"),
    _p("DC_CONFIGURATION",       "Configuration",            "1P260S (5×1P52S)","",  "Electrical"),
    _p("DC_CELL_TYPE",           "Cell Type",                "LFP 3.2V/314Ah","",    "Electrical"),
    _p("DC_CHARGE_RATE",         "Charge/Discharge Rate",    "≤0.5P",        "",     "Electrical"),
    _p("DC_FORM_FACTOR",         "Form Factor",              "Integrated cabinet","","Physical"),
    _p("DC_DIMENSIONS",          "Dimensions (W×D×H)",       "1100×1320×2560","mm",  "Physical"),
    _p("DC_WEIGHT_KG",           "Weight",                   "2600",         "kg",   "Physical"),
    _p("DC_COOLING",             "Cooling Type",             "Liquid cooling/heating","","Thermal"),
    _p("DC_OP_TEMP_MIN",         "Operating Temp Min (Discharge)","-30",     "°C",   "Thermal"),
    _p("DC_OP_TEMP_MAX",         "Operating Temp Max",       "55",           "°C",   "Thermal"),
    _p("DC_STORAGE_TEMP",        "Storage Temp",             "-20 to 35",    "°C",   "Thermal"),
    _p("DC_ALTITUDE_M",          "Max Altitude",             "3000",         "m",    "Environmental"),
    _p("DC_IP_RATING",           "IP Rating",                "IP54",         "",     "Protection"),
    _p("DC_HUMIDITY",            "Humidity",                 "0-95%, no condensation","","Environmental"),
    _p("DC_INSULATION_MOHM",     "Insulation Resistance",    "≥550",         "MΩ",   "Protection"),
    _p("DC_FIRE_SUPPRESSION",    "Fire Suppression",         "Aerosol + smoke/temp detection","","Safety"),
    _p("DC_BMS_LEVELS",          "BMS Architecture",         "3-level: BMU + BCU + EMS comm","","BMS"),
    _p("DC_COMMS",               "Communication",            "RS485/Ethernet/CAN, Modbus RTU/TCP","","Communication"),
    _p("DC_CERTS",               "Certifications",           "GB/T 36276-2023, IEC 62933-5-2, IEC 62619, IEC 62477-1, IEC 63056, UN 38.3","","Safety"),
    _p("DC_MODULE_IP",           "Module IP Rating",         "IP67",         "",     "Protection"),
]

# ─────────────────────────────────────────────────────────────────────
# Hexon HESS-215-418 — 418 kWh Liquid Cooled Cabinet (with PCS)
# ─────────────────────────────────────────────────────────────────────
_HEXON_215_418 = [
    _p("DC_RATED_ENERGY_KWH",    "Rated Energy",             "418",          "kWh",  "Electrical"),
    _p("DC_RATED_VOLTAGE_V",     "Rated DC Voltage",         "1331.2",       "V",    "Electrical"),
    _p("DC_VOLTAGE_RANGE",       "DC Voltage Range",         "1040-1518.4",  "V",    "Electrical"),
    _p("DC_RATED_POWER_KW",      "Rated Power (AC)",         "215",          "kW",   "Electrical"),
    _p("DC_MAX_POWER_KW",        "Max Output Power",         "258",          "kW",   "Electrical"),
    _p("DC_CONFIGURATION",       "Configuration",            "1P416S (8×1P52S)","",  "Electrical"),
    _p("DC_CELL_TYPE",           "Cell Type",                "LFP 3.2V/314Ah","",    "Electrical"),
    _p("DC_PCS_EFFICIENCY",      "PCS Max Efficiency",       ">98.5",        "%",    "Performance"),
    _p("DC_THD",                 "THDi",                     "<3",           "%",    "Power Quality"),
    _p("DC_POWER_FACTOR",        "Power Factor",             "-1 to +1",     "",     "Power Quality"),
    _p("DC_FORM_FACTOR",         "Form Factor",              "Integrated cabinet","","Physical"),
    _p("DC_DIMENSIONS",          "Dimensions (W×D×H)",       "1400×1350×2350","mm",  "Physical"),
    _p("DC_WEIGHT_KG",           "Weight",                   "3800",         "kg",   "Physical"),
    _p("DC_COOLING",             "Cooling Type",             "Liquid cooling (8kW)","","Thermal"),
    _p("DC_OP_TEMP_MIN",         "Operating Temp Min",       "-30",          "°C",   "Thermal"),
    _p("DC_OP_TEMP_MAX",         "Operating Temp Max",       "55",           "°C",   "Thermal"),
    _p("DC_ALTITUDE_M",          "Max Altitude",             "3000",         "m",    "Environmental"),
    _p("DC_IP_RATING",           "IP Rating",                "IP66/IP54",    "",     "Protection"),
    _p("DC_COATING",             "Anti-Corrosion",           "C4, ≥120μm film, fire-resist ≥1.5h","","Physical"),
    _p("DC_FIRE_SUPPRESSION",    "Fire Suppression",         "FK-5-1-12 (Novec) + water system","","Safety"),
    _p("DC_BMS_LEVELS",          "BMS Architecture",         "3-level: BMU + BCU + BAU","","BMS"),
    _p("DC_COMMS",               "Communication",            "RS485/Ethernet/CAN, Modbus RTU/TCP, IEC 104","","Communication"),
    _p("DC_UPS",                 "UPS Backup",               "≥1 hour",      "",     "Reliability"),
    _p("DC_CERTS",               "Certifications",           "GB/T 36276-2023","",   "Safety"),
    _p("DC_NOISE_DB",            "PCS Noise Level",          "<70",          "dBA",  "Physical"),
]

# ─────────────────────────────────────────────────────────────────────
# Hexon HEMERA HBAT-5015-15 — ~5 MWh 20ft Container
# ─────────────────────────────────────────────────────────────────────
_HEXON_5015 = [
    _p("DC_RATED_ENERGY_KWH",    "Rated Energy",             "5015",         "kWh",  "Electrical"),
    _p("DC_RATED_VOLTAGE_V",     "Rated DC Voltage",         "1331.2",       "V",    "Electrical"),
    _p("DC_VOLTAGE_RANGE",       "DC Voltage Range",         "1104.6-1497.6","V",    "Electrical"),
    _p("DC_CONFIGURATION",       "Configuration",            "12 clusters, 1P416S","","Electrical"),
    _p("DC_CELL_TYPE",           "Cell Type",                "LFP 314Ah",   "",      "Electrical"),
    _p("DC_CHARGE_RATE",         "Charge/Discharge Rate",    "0.5C",         "",     "Electrical"),
    _p("DC_FORM_FACTOR",         "Form Factor",              "20ft container","",    "Physical"),
    _p("DC_DIMENSIONS",          "Dimensions (L×W×H)",       "6058×2438×2896","mm",  "Physical"),
    _p("DC_WEIGHT_T",            "Weight",                   "42",           "t",    "Physical"),
    _p("DC_COOLING",             "Cooling Type",             "Liquid cooling","",    "Thermal"),
    _p("DC_OP_TEMP_MIN",         "Operating Temp Min",       "-30",          "°C",   "Thermal"),
    _p("DC_OP_TEMP_MAX",         "Operating Temp Max",       "55",           "°C",   "Thermal"),
    _p("DC_ALTITUDE_M",          "Max Altitude",             "3000",         "m",    "Environmental"),
    _p("DC_IP_RATING",           "IP Rating",                "IP54",         "",     "Protection"),
    _p("DC_COATING",             "Anti-Corrosion",           "C4",           "",     "Physical"),
    _p("DC_FIRE_SUPPRESSION",    "Fire Suppression",         "Aerosol",      "",     "Safety"),
    _p("DC_COMMS",               "Communication",            "RS485/Ethernet/CAN","","Communication"),
    _p("DC_CERTS",               "Certifications",           "IEC 62619, UN 38.3","","Safety"),
]

# ─────────────────────────────────────────────────────────────────────
# Hexon EOS All-in-One C&I (SOLAESS-100-215)
# ─────────────────────────────────────────────────────────────────────
_HEXON_EOS = [
    _p("DC_RATED_POWER_KW",      "Rated AC Power",           "100",          "kW",   "Electrical"),
    _p("DC_MAX_POWER_KW",        "Max AC Power",             "110",          "kW",   "Electrical"),
    _p("DC_RATED_ENERGY_KWH",    "Rated Battery Capacity",   "215",          "kWh",  "Electrical"),
    _p("DC_AC_VOLTAGE_V",        "AC Voltage",               "400",          "V",    "Electrical"),
    _p("DC_PV_VOLTAGE_MAX",      "Max PV Open Circuit",      "700",          "V DC", "PV Input"),
    _p("DC_PV_POWER_KWP",        "Rated PV Power",           "100",          "kWp",  "PV Input"),
    _p("DC_MPPT_COUNT",          "MPPT Channels",            "2",            "",     "PV Input"),
    _p("DC_THD",                 "THDi",                     "<3",           "%",    "Power Quality"),
    _p("DC_POWER_FACTOR",        "Power Factor",             "-0.8 to +0.8","",      "Power Quality"),
    _p("DC_OVERLOAD",            "Overload",                 "110% 10min, 120% 1min","","Performance"),
    _p("DC_FORM_FACTOR",         "Form Factor",              "All-in-One C&I cabinet","","Physical"),
    _p("DC_COOLING",             "Cooling Type",             "Liquid cooling","",    "Thermal"),
    _p("DC_CERTS",               "PCS Certifications",       "IEC 62477-1, IEC 61000, EN 50549-1, VDE 4105","","Safety"),
    _p("DC_MODULE_CERTS",        "Module Certifications",    "UL 1973, UL 9540A, IEC 62619, UN 38.3","","Safety"),
]

# ─────────────────────────────────────────────────────────────────────
# Hexon EOS+ Modular (SOLAES-125-261)
# ─────────────────────────────────────────────────────────────────────
_HEXON_EOSPLUS = [
    _p("DC_RATED_POWER_KW",      "Rated AC Power",           "125",          "kW",   "Electrical"),
    _p("DC_RATED_ENERGY_KWH",    "Battery Capacity",         "261",          "kWh",  "Electrical"),
    _p("DC_AC_VOLTAGE_V",        "AC Voltage",               "400",          "V",    "Electrical"),
    _p("DC_PV_VOLTAGE_MAX",      "Max PV Open Circuit",      "1050",         "V DC", "PV Input"),
    _p("DC_PV_POWER_KWP",        "Max PV Power",             "250",          "kWp",  "PV Input"),
    _p("DC_BATTERY_VOLTAGE",     "Battery Voltage Range",    "470.4-1382.4", "V",    "Electrical"),
    _p("DC_OP_TEMP_MIN",         "Operating Temp Min",       "-27",          "°C",   "Thermal"),
    _p("DC_OP_TEMP_MAX",         "Operating Temp Max",       "56",           "°C",   "Thermal"),
    _p("DC_IP_RATING",           "IP Rating",                "IP65",         "",     "Protection"),
    _p("DC_COOLING",             "Cooling Type",             "Air-cooled + intelligent A/C","","Thermal"),
    _p("DC_ALTITUDE_M",          "Max Altitude",             "3000",         "m",    "Environmental"),
    _p("DC_DIMENSIONS",          "Dimensions (L×W×H)",       "3000×2300×2700","mm",  "Physical"),
    _p("DC_WEIGHT_KG",           "Weight",                   "2500",         "kg",   "Physical"),
    _p("DC_COMMS",               "Communication",            "Ethernet, RS485, 4G","","Communication"),
    _p("DC_FORM_FACTOR",         "Form Factor",              "Modular outdoor cabinet","","Physical"),
]

# ─────────────────────────────────────────────────────────────────────
# Lishen ESS-ES5016C — 5.016 MWh 20ft Container
# ─────────────────────────────────────────────────────────────────────
_LISHEN_5MWH = [
    _p("DC_RATED_ENERGY_KWH",    "Rated Energy",             "5015.96",      "kWh",  "Electrical"),
    _p("DC_RATED_VOLTAGE_V",     "Rated DC Voltage",         "1331.2",       "V",    "Electrical"),
    _p("DC_VOLTAGE_RANGE",       "DC Voltage Range",         "1123.2-1497.6","V",    "Electrical"),
    _p("DC_RATED_POWER_KW",      "Rated Power (0.5P)",       "2500",         "kW",   "Electrical"),
    _p("DC_CONFIGURATION",       "Configuration",            "12P416S (6 racks×2P416S, 4992 cells)","","Electrical"),
    _p("DC_CELL_TYPE",           "Cell",                     "LP71173207 LFP 314Ah","","Electrical"),
    _p("DC_CYCLE_LIFE",          "Cell Cycle Life",          "≥8800 (0.5P, 65% SOH)","cycles","Performance"),
    _p("DC_RTE_PCT",             "Round-Trip Efficiency",    "≥94",          "%",    "Performance"),
    _p("DC_EOL_SOH",             "EOL SOH Target",           "65",           "%",    "Performance"),
    _p("DC_FORM_FACTOR",         "Form Factor",              "20ft container","",    "Physical"),
    _p("DC_DIMENSIONS",          "Dimensions (L×W×H)",       "6058×2438×2896","mm",  "Physical"),
    _p("DC_WEIGHT_T",            "Weight",                   "43",           "t",    "Physical"),
    _p("DC_COOLING",             "Cooling Type",             "Liquid (60kW cooling, 21kW heating, R32)","","Thermal"),
    _p("DC_OP_TEMP_MIN",         "Operating Temp Min",       "-20",          "°C",   "Thermal"),
    _p("DC_OP_TEMP_MAX",         "Operating Temp Max",       "55",           "°C",   "Thermal"),
    _p("DC_STORAGE_TEMP",        "Storage Temp",             "-30 to 45",    "°C",   "Thermal"),
    _p("DC_ALTITUDE_M",          "Max Altitude",             "2000",         "m",    "Environmental"),
    _p("DC_IP_RATING",           "IP Rating",                "IP55",         "",     "Protection"),
    _p("DC_COATING",             "Enclosure Coating",        "C4, steel ≥2.0mm, IK10","","Physical"),
    _p("DC_AUX_POWER_STANDBY",   "Aux Power (Standby)",     "0.7",          "kW",   "Electrical"),
    _p("DC_AUX_POWER_MAX",       "Aux Power (Max)",         "37.6",          "kW",   "Electrical"),
    _p("DC_FIRE_SUPPRESSION",    "Fire Suppression",         "Aerosol (5 units) + water sprinkler; smoke/heat/gas detectors (EN54); ATEX ventilation","","Safety"),
    _p("DC_BMS_LEVELS",          "BMS Architecture",         "3-level: MBMS + RBMS + SBMS; IEC 61850 + IEC 104","","BMS"),
    _p("DC_BMS_BALANCE",         "BMS Balancing",            "Passive, 100mA","",    "BMS"),
    _p("DC_COMMS",               "Communication",            "RS485, Ethernet, CAN 2.0","","Communication"),
    _p("DC_UPS",                 "UPS",                      "3 kVA (UL1778, IEC62040-1)","","Reliability"),
    _p("DC_CERTS",               "Certifications",           "UL 1973, UL 9540A, UL 9540, UN 3536, IEC 62933-5-2, IEC 62933-2-1, Zone-4 seismic, BV","","Safety"),
    _p("DC_MODULE_IP",           "Module IP Rating",         "IP67",         "",     "Protection"),
    _p("DC_LIGHTING",            "Explosion-Proof Lighting", "5×20W LED",    "",     "Safety"),
]

# ─────────────────────────────────────────────────────────────────────
# SVOLT CE-L-5160-B1-EU — 5,161 kWh 20ft Container (Short Blade II)
# ─────────────────────────────────────────────────────────────────────
_SVOLT_5160 = [
    _p("DC_RATED_ENERGY_KWH",    "Rated Energy",             "5160.96",      "kWh",  "Electrical"),
    _p("DC_RATED_VOLTAGE_V",     "Rated DC Voltage",         "1228.8",       "V",    "Electrical"),
    _p("DC_VOLTAGE_RANGE",       "DC Voltage Range",         "1075.2-1382.4","V",    "Electrical"),
    _p("DC_RATED_POWER_KW",      "Nominal Power (0.5P)",     "2580",         "kW",   "Electrical"),
    _p("DC_CONFIGURATION",       "Configuration",            "12 clusters×1P384S (3 packs×1P128S)","","Electrical"),
    _p("DC_CELL_TYPE",           "Cell",                     "LFP CL40, 350Ah, 176 Wh/kg","","Electrical"),
    _p("DC_CELL_IR_MOHM",        "Cell Internal Resistance", "≤0.3",         "mΩ",   "Electrical"),
    _p("DC_CYCLE_LIFE",          "Cell Cycle Life",          "≥10000",       "cycles","Performance"),
    _p("DC_RTE_PCT",             "DC Round-Trip Efficiency", "94",           "%",    "Performance"),
    _p("DC_DOD",                 "Depth of Discharge",       "100",          "%",    "Performance"),
    _p("DC_AVAILABILITY",        "Availability Target",      "≥97",          "%",    "Performance"),
    _p("DC_FORM_FACTOR",         "Form Factor",              "20ft container","",    "Physical"),
    _p("DC_DIMENSIONS",          "Dimensions (W×H×D)",       "6058×3100×2438","mm",  "Physical"),
    _p("DC_WEIGHT_T",            "Weight",                   "≤43",          "t",    "Physical"),
    _p("DC_COOLING",             "Cooling Type",             "Liquid (50% EG, 60kW cooling, ≥24kW heating)","","Thermal"),
    _p("DC_OP_TEMP_MIN",         "Operating Temp Min",       "-30",          "°C",   "Thermal"),
    _p("DC_OP_TEMP_MAX",         "Operating Temp Max",       "55",           "°C",   "Thermal"),
    _p("DC_STORAGE_TEMP",        "Storage Temp (1mo/6mo)",   "-40~45 / -20~35","°C", "Thermal"),
    _p("DC_ALTITUDE_M",          "Max Altitude (no derating)","3000",        "m",    "Environmental"),
    _p("DC_IP_RATING",           "IP Rating",                "IP55",         "",     "Protection"),
    _p("DC_HUMIDITY",            "Operating Humidity",        "5-95%",       "",      "Environmental"),
    _p("DC_NOISE_DB",            "Noise Level",              "≤80",          "dBA",  "Physical"),
    _p("DC_COATING",             "Enclosure Coating",        "C4 (C5 opt), RAL 7035, CORTEN-A steel","","Physical"),
    _p("DC_FIRE_RESIST",         "Fire Resistant Time",      "≥1 hour",      "",     "Safety"),
    _p("DC_FIRE_SUPPRESSION",    "Fire Suppression",         "Aerosol + sprinkler + quick-access; smoke/temp/H2/CO detectors","","Safety"),
    _p("DC_SEISMIC",             "Anti-Seismic",             "UBC Zone 4",   "",     "Environmental"),
    _p("DC_WIND_SPEED",          "Anti-Wind",                "35",           "m/s",  "Environmental"),
    _p("DC_BMS_LEVELS",          "BMS Architecture",         "3-level: BMU + BCU + ESMU; passive balance ≥100mA","","BMS"),
    _p("DC_BMS_TEMP_ACC",        "BMS Temp Accuracy",        "≤±1",         "°C",    "BMS"),
    _p("DC_BMS_V_ACC",           "BMS Voltage Accuracy",     "≤±3mV (0-5V)","",     "BMS"),
    _p("DC_BMS_SOC_ACC",         "BMS SOC Accuracy",         "<5",          "%",     "BMS"),
    _p("DC_COMMS",               "Communication",            "RS485, Ethernet, CAN 2.0; Modbus RTU/TCP, IEC 104","","Communication"),
    _p("DC_UPS",                 "UPS Backup",               "30 min",       "",     "Reliability"),
    _p("DC_INSULATION_MON",      "Insulation Monitoring",    "BMS + EMC joint","",   "Protection"),
    _p("DC_THERMAL_INSUL",       "Thermal Insulation",       "100mm rock wool (top/bottom), 50mm (sides)","","Thermal"),
    _p("DC_PACK_IP",             "Pack IP Rating",           "IP65",         "",     "Protection"),
    _p("DC_CERTS",               "Certifications",           "UL 1973, UL 9540A, UL 9540, IEC 62619, IEC 63056, IEC 62933-5-2, IEC 62933-2-1, UN 38.3, UN 3536, NFPA 68/69/855, RoHS","","Safety"),
]


DCBLOCK_PARAMETERS = {
    "comp-catl-enerx":      _CATL_ENERX,
    "comp-catl-tener":      _CATL_TENER,
    "comp-hexon-125-261":   _HEXON_125_261,
    "comp-hexon-215-418":   _HEXON_215_418,
    "comp-hexon-5015":      _HEXON_5015,
    "comp-hexon-eos":       _HEXON_EOS,
    "comp-hexon-eosplus":   _HEXON_EOSPLUS,
    "comp-lishen-5mwh":     _LISHEN_5MWH,
    "comp-svolt-5160":      _SVOLT_5160,
}

