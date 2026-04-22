"""
EMS (Energy Management System) Seed Data.
Source: /Users/priyankrajput/Downloads/EMS/
Manufacturers: Acrel, Adaptive (AEPL), EIT Automation, Smart Grid Analytics (SGA)
"""

EMS_OEMS = [
    {"id": "oem-acrel",     "name": "Acrel",                    "country_of_origin": "China",
     "is_approved": False,
     "website": "https://www.acrel.cn", "contact_email": "sales@acrel.cn"},
    {"id": "oem-adaptive",  "name": "Adaptive Engineering (AEPL)", "country_of_origin": "India",
     "is_approved": True,
     "website": "https://www.adaptive-engg.com", "contact_email": "info@adaptive-engg.com"},
    {"id": "oem-eit",       "name": "EIT Automation",           "country_of_origin": "India",
     "is_approved": True,
     "website": "https://www.eitautomation.com", "contact_email": "sales@eitautomation.com"},
    {"id": "oem-sga",       "name": "Smart Grid Analytics (SGA)", "country_of_origin": "India",
     "is_approved": True,
     "website": "https://www.sgrids.com", "contact_email": "kumarm@sgrids.io"},
]

EMS_COMPONENTS = [
    # ── Acrel ──
    {"id": "comp-acrel-anet",       "oem_id": "oem-acrel",     "oem_name": "Acrel",
     "model_name": "Acrel ANet Communication Gateway", "sku": "ANet-Series",
     "component_type_name": "EMS Gateway",
     "is_active": True,
     "datasheet": "Installation Instructions Acrel.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/EMS/Acrel_EMS/Installation Instructions Acrel.pdf"},
    # ── Adaptive ──
    {"id": "comp-adaptive-ems",     "oem_id": "oem-adaptive",  "oem_name": "Adaptive Engineering (AEPL)",
     "model_name": "AEPL BESS EMS (Schneider PLC + AVEVA)", "sku": "AEPL-EMS-BESS",
     "component_type_name": "EMS",
     "is_active": True,
     "datasheet": "Ornate-Rajasthan-35MWh.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/EMS/Adaptive/3476-Ornate-Rajasthan-35MWh.pdf"},
    # ── EIT ──
    {"id": "comp-eit-ems",          "oem_id": "oem-eit",       "oem_name": "EIT Automation",
     "model_name": "EIT BESS EMS (Mitsubishi PLC)", "sku": "EIT-EMS-BESS",
     "component_type_name": "EMS",
     "is_active": True,
     "datasheet": "EMS_CRS_EIT_21.03.26.xlsx",
     "datasheet_path": "/Users/priyankrajput/Downloads/EMS/EIT/EMS_CRS_EIT_21.03.26.xlsx"},
    # ── Smart Grid Analytics (SGA) ──
    {"id": "comp-sga-solvyn",       "oem_id": "oem-sga",       "oem_name": "Smart Grid Analytics (SGA)",
     "model_name": "Solvyn EMS/EPPC", "sku": "SGA-SOLVYN",
     "component_type_name": "EMS",
     "is_active": True,
     "datasheet": "EMS_FDS_R0 9.pdf",
     "datasheet_path": "/Users/priyankrajput/Downloads/EMS/Smartgrid_EMS/EMS_FDS_R0 9.pdf"},
]


def _p(code, name, value, unit, section):
    return {"code": code, "name": name, "value": value, "unit": unit,
            "section": section}


# ─── Acrel ANet Communication Gateway ───
# Note: This is a gateway/data concentrator, NOT a full EMS. Scored accordingly.
_ACREL_ANET = [
    _p("EMS_TYPE",              "System Type",              "Communication Gateway",    "",     "General"),
    _p("EMS_PLATFORM",          "Platform",                 "ANet Series (ARM Cortex-A7 528MHz)","","General"),
    _p("EMS_PROTOCOLS_DOWN",    "Downlink Protocols",       "RS485 Modbus RTU, CAN, MBUS, Lora","","Communication"),
    _p("EMS_PROTOCOLS_UP",      "Uplink Protocols",         "Ethernet Modbus TCP, 4G","",       "Communication"),
    _p("EMS_IEC104",            "IEC 60870-5-104",          "Supported (forwarding)","",        "Communication"),
    _p("EMS_IEC61850",          "IEC 61850",                "Supported (forwarding)","",        "Communication"),
    _p("EMS_MAX_DEVICES",       "Max Connected Devices",    "256",          "",                 "Scalability"),
    _p("EMS_MAX_DATAPOINTS",    "Max Data Points",          "36000",        "",                 "Scalability"),
    _p("EMS_MEMORY",            "Memory",                   "128-256MB DDR","",                 "Hardware"),
    _p("EMS_STORAGE",           "Storage",                  "256MB Flash + 8GB SD","",          "Hardware"),
    _p("EMS_RS485_PORTS",       "RS485 Ports",              "2-16",         "",                 "Hardware"),
    _p("EMS_POWER_W",           "Power Consumption",        "<10",          "W",                "Hardware"),
    _p("EMS_OP_TEMP_MIN",       "Operating Temp Min",       "-20",          "°C",               "Environmental"),
    _p("EMS_OP_TEMP_MAX",       "Operating Temp Max",       "55",           "°C",               "Environmental"),
    _p("EMS_HUMIDITY",          "Humidity",                 "≤95%",         "",                 "Environmental"),
    _p("EMS_MTBF",              "MTBF",                     ">30000",       "hours",            "Reliability"),
    _p("EMS_EMC",               "EMC Rating",               "ESD L4, EFT L4, SURGE L4","",     "Safety"),
    _p("EMS_EDGE_COMPUTE",      "Edge Computing",           "Sum, logic, Schmitt trigger, timed","","Features"),
    # Missing BESS-critical features
    _p("EMS_SCADA",             "SCADA HMI",                "None (gateway only)","",           "Features"),
    _p("EMS_CONTROL_MODES",     "BESS Control Modes",       "None",         "",                 "Control"),
    _p("EMS_REDUNDANCY",        "Hot Standby Redundancy",   "No",           "",                 "Reliability"),
    _p("EMS_CYBERSECURITY",     "Cybersecurity Compliance", "Basic EMC only","",                "Security"),
    _p("EMS_HISTORIAN",         "Data Historian",           "8GB SD only",  "",                 "Storage"),
    _p("EMS_BESS_EXPERIENCE",   "BESS Project Experience",  "None documented","",               "Experience"),
]

# ─── Adaptive Engineering (AEPL) — Schneider PLC + AVEVA ───
_ADAPTIVE_EMS = [
    _p("EMS_TYPE",              "System Type",              "Full EMS + SCADA",     "",         "General"),
    _p("EMS_PLATFORM",          "Platform",                 "Schneider Electric PLC + AVEVA SCADA","","General"),
    _p("EMS_OS",                "Server OS",                "Windows Server 2022",  "",         "General"),
    # Communication
    _p("EMS_MODBUS_TCP",        "Modbus TCP/IP",            "Supported",    "",                 "Communication"),
    _p("EMS_IEC104",            "IEC 60870-5-104",          "Supported (Edition 1, CP56Time2a)","","Communication"),
    _p("EMS_OPC_UA",            "OPC-UA",                   "Cogent DataHub (2 licenses)","",   "Communication"),
    _p("EMS_IEC61850",          "IEC 61850",                "Not mentioned","",                 "Communication"),
    _p("EMS_RS485",             "Modbus RS485",             "Via gateway (Masibus)","",          "Communication"),
    _p("EMS_GPS_SYNC",          "GPS Time Sync",            "NTP + IRIG-B, Masibus GPS clock","","Communication"),
    _p("EMS_DAY_AHEAD",         "Day-Ahead Schedule",       "CSV via FTP, 96×15min blocks","",  "Communication"),
    # Control Modes
    _p("EMS_ACTIVE_POWER",      "Active Power Dispatch",    "Supported (MW from SLDC/NLDC)","", "Control"),
    _p("EMS_REACTIVE_POWER",    "Reactive Power Control",   "Supported (kVAr setpoint)","",     "Control"),
    _p("EMS_AGC",               "AGC Interface",            "Supported (per CERC)","",          "Control"),
    _p("EMS_FREQ_REG",          "Frequency Regulation",     "Primary/Secondary/Tertiary","",    "Control"),
    _p("EMS_PEAK_SHAVE",        "Peak Shaving",             "Supported",    "",                 "Control"),
    _p("EMS_RAMP_RATE",         "Ramp Rate Control",        "10 MW/min (configurable)","",      "Control"),
    _p("EMS_SOC_MGMT",          "SOC Management",           "Predictive algorithms","",         "Control"),
    _p("EMS_DEGRADATION",       "Degradation-Aware Dispatch","Supported",   "",                 "Control"),
    _p("EMS_BLACK_START",       "Black Start",              "Supported",    "",                 "Control"),
    _p("EMS_ISLANDING",         "Islanding Detection",      "Supported",    "",                 "Control"),
    _p("EMS_DROOP",             "Droop Control",            "1-3% range, PID 100-1000ms","",    "Control"),
    # Performance
    _p("EMS_PPC_LATENCY_MS",    "Master PPC → Slave EMS",   "20-30",        "ms",               "Performance"),
    _p("EMS_TO_PCS_MS",         "EMS → PCS Response",       "500-800",      "ms",               "Performance"),
    _p("EMS_END_TO_END_MS",     "End-to-End Setpoint",      "700-1000",     "ms",               "Performance"),
    _p("EMS_IEC104_INTERVAL",   "IEC-104 to LDC Interval",  "5",            "min",              "Performance"),
    _p("EMS_SOE_RES",           "SOE Resolution",           "≤1",           "ms",               "Performance"),
    _p("EMS_DATA_REFRESH",      "SCADA Data Refresh",       "≤1",           "sec",              "Performance"),
    # SCADA
    _p("EMS_SCADA",             "SCADA Software",           "AVEVA (2 licenses)","",            "Features"),
    _p("EMS_ALARM_MGMT",        "Alarm Management",         "Multi-level configurable","",      "Features"),
    _p("EMS_TRENDING",          "Trending & Historicals",    "Supported",    "",                 "Features"),
    _p("EMS_REPORTS",           "Report Generation",        "Daily/Monthly/Annual","",          "Features"),
    _p("EMS_WEB_ACCESS",        "Web-Based Remote Access",  "Role-based (1 concurrent)","",     "Features"),
    _p("EMS_MOBILE_APP",        "Mobile App",               "Yes",          "",                 "Features"),
    # Hardware
    _p("EMS_CONTROLLER",        "EMS Controller",           "Schneider PLC (redundant)","",     "Hardware"),
    _p("EMS_SERVER_CPU",        "Server CPU",               "Intel Xeon 4-core 2.6GHz","",     "Hardware"),
    _p("EMS_SERVER_RAM",        "Server RAM",               "64GB (up to 128GB)","",            "Hardware"),
    _p("EMS_SERVER_STORAGE",    "Server Storage",           "2×2TB SSD RAID-1","",              "Hardware"),
    _p("EMS_DISPLAYS",          "Display Setup",            "2×32\" LED + 1×55\" LED","",       "Hardware"),
    _p("EMS_NETWORK",           "Network Switches",         "Advantech/ORing L3 managed, SFP fiber","","Hardware"),
    # Cybersecurity
    _p("EMS_CYBERSECURITY",     "Cybersecurity Standard",   "CEA 2020 + IEC 62443","",         "Security"),
    _p("EMS_RBAC",              "Role-Based Access Control", "Yes + audit trail","",            "Security"),
    _p("EMS_FIREWALL",          "Firewall",                 "Fortinet FortiGate 60F ×2 (OT+IT)","","Security"),
    _p("EMS_ENCRYPTION",        "Encrypted Communication",  "TLS/SSL",      "",                 "Security"),
    _p("EMS_IDS",               "Intrusion Detection",      "Supported",    "",                 "Security"),
    _p("EMS_DMZ",               "DMZ Architecture",         "Defense-in-depth","",              "Security"),
    # Redundancy
    _p("EMS_REDUNDANCY",        "Hot Standby",              "Dual PLC + dual servers","",       "Reliability"),
    _p("EMS_IEC104_REDUND",     "IEC-104 Redundancy",       "Hot-hot dual ports","",            "Reliability"),
    _p("EMS_FIBER_RING",        "Fiber Ring Topology",      "RSTP failover","",                 "Reliability"),
    # Historian
    _p("EMS_HISTORIAN",         "Data Historian",           "MS SQL Server, 5yr, RAID-1","",    "Storage"),
    # Certifications & Experience
    _p("EMS_CERTS",             "Certifications",           "ISO 9001:2015 (TUV-Nord)","",     "Safety"),
    _p("EMS_WARRANTY",          "Warranty",                 "60mo SW / 36mo HW","",             "General"),
    _p("EMS_BESS_EXPERIENCE",   "BESS Experience",          "1500 MWh claimed","",              "Experience"),
    _p("EMS_SOLAR_EXPERIENCE",  "Solar SCADA Experience",   "20000+ MW, 500+ sites","",        "Experience"),
    _p("EMS_GRID_CODES",        "Grid Code Compliance",     "Indian (CERC/CEA)","",             "Compliance"),
    _p("EMS_IO_POINTS",         "I/O Points",               "300-10000",    "",                 "Scalability"),
]

# ─── EIT Automation — Mitsubishi PLC ───
_EIT_EMS = [
    _p("EMS_TYPE",              "System Type",              "Full EMS + PPC",       "",         "General"),
    _p("EMS_PLATFORM",          "Platform",                 "Mitsubishi Electric PLC","",       "General"),
    # Communication
    _p("EMS_MODBUS_TCP",        "Modbus TCP/IP",            "Supported",    "",                 "Communication"),
    _p("EMS_IEC104",            "IEC 60870-5-104",          "Supported (if required)","",       "Communication"),
    _p("EMS_IEC61850",          "IEC 61850",                "Supported (relays)","",            "Communication"),
    _p("EMS_RS485",             "Modbus RS485",             "Supported",    "",                 "Communication"),
    _p("EMS_DAY_AHEAD",         "Day-Ahead Schedule",       "CSV via SFTP","",                  "Communication"),
    _p("EMS_GPS_SYNC",          "GPS Time Sync",            "Available as add-on","",           "Communication"),
    _p("EMS_OPC_UA",            "OPC-UA",                   "Not mentioned","",                 "Communication"),
    # Control Modes
    _p("EMS_ACTIVE_POWER",      "Active Power Control",     "Supported",    "",                 "Control"),
    _p("EMS_REACTIVE_POWER",    "Reactive Power Control",   "Supported",    "",                 "Control"),
    _p("EMS_FREQ_REG",          "Voltage/Frequency Droop",  "Per CEA regulations","",           "Control"),
    _p("EMS_AGC",               "AGC Interface",            "Via telemetry RTU","",             "Control"),
    _p("EMS_RAMP_RATE",         "Ramp Rate Control",        "Settable",     "",                 "Control"),
    _p("EMS_SOC_MGMT",          "SOC Management",           "Curtailment/de-rate logic","",     "Control"),
    _p("EMS_ANCILLARY",         "Ancillary Services",       "Concurrent with day-ahead","",     "Control"),
    # Performance
    _p("EMS_PLC_SCAN_MS",       "PLC Scan Cycle",           "10",           "ms",               "Performance"),
    _p("EMS_CTRL_RESP_MS",      "Control Output Response",  "200",          "ms",               "Performance"),
    _p("EMS_PPC_LATENCY_MS",    "Master PPC → Slave EMS",   "100",          "ms",               "Performance"),
    # SCADA
    _p("EMS_SCADA",             "SCADA",                    "Real-time monitoring","",          "Features"),
    _p("EMS_DATA_LOG_1S",       "1-Second Data Logging",    "15 days",      "",                 "Features"),
    _p("EMS_DATA_LOG_1M",       "1-Minute Data Logging",    "Extended period","",               "Features"),
    _p("EMS_RBAC",              "Role-Based Access Control", "Yes",          "",                 "Security"),
    _p("EMS_NETWORK_SLA",       "Network Availability SLA", "0.99",         "",                 "Reliability"),
    # Cybersecurity
    _p("EMS_CYBERSECURITY",     "Cybersecurity Standard",   "CEA 2019","",                      "Security"),
    _p("EMS_FIREWALL",          "Firewall",                 "Not detailed","",                  "Security"),
    _p("EMS_ENCRYPTION",        "Encrypted Communication",  "Not detailed","",                  "Security"),
    # Redundancy
    _p("EMS_REDUNDANCY",        "Hot Standby",              "Not detailed","",                  "Reliability"),
    # Historian
    _p("EMS_HISTORIAN",         "Data Historian",           "1s/15 days, 1min/extended","",     "Storage"),
    # Experience
    _p("EMS_BESS_EXPERIENCE",   "BESS Project Experience",  "1100+ MWh (ACME 250MW/1100MWh)","","Experience"),
    _p("EMS_TOTAL_EXPERIENCE",  "Total SCADA Experience",   "14 GW+, 140+ projects","",        "Experience"),
    _p("EMS_GRID_CODES",        "Grid Code Compliance",     "Indian (CEA)","",                  "Compliance"),
    _p("EMS_CERTS",             "Certifications",           "None listed","",                   "Safety"),
    _p("EMS_TEAM",              "Engineering Team",         "30+ engineers","",                 "General"),
]

# ─── Smart Grid Analytics (SGA) — Solvyn EMS/EPPC ───
_SGA_SOLVYN = [
    _p("EMS_TYPE",              "System Type",              "Full EMS/EPPC + SCADA","",         "General"),
    _p("EMS_PLATFORM",          "Platform",                 "Solvyn (proprietary, Linux Ubuntu)","","General"),
    _p("EMS_HARDWARE",          "Hardware",                 "Industrial box-type, Intel processor","","General"),
    # Communication
    _p("EMS_MODBUS_TCP",        "Modbus TCP/RTU",           "Supported",    "",                 "Communication"),
    _p("EMS_IEC104",            "IEC 60870-5-104",          "Supported",    "",                 "Communication"),
    _p("EMS_IEC61850",          "IEC 61850",                "Supported",    "",                 "Communication"),
    _p("EMS_OPC_UA",            "OPC-UA",                   "Supported",    "",                 "Communication"),
    _p("EMS_GPS_SYNC",          "GPS Time Sync",            "NTP/PTP (IEEE 1588)","",           "Communication"),
    _p("EMS_WEATHER",           "Weather Station Integration","Supported",  "",                 "Communication"),
    # Control Modes — Grid Code
    _p("EMS_ACTIVE_POWER",      "Active Power Control",     "P setpoint from SLDC/NLDC","",     "Control"),
    _p("EMS_REACTIVE_POWER",    "Reactive Power Control",   "Voltage droop + PF management","", "Control"),
    _p("EMS_RAMP_RATE",         "Ramp Rate Control",        "10-100% per minute","",            "Control"),
    _p("EMS_FREQ_REG",          "Frequency Control",        "PI controller, deadband, Pri/Sec/Tert","","Control"),
    _p("EMS_VOLTAGE_DROOP",     "Voltage Droop Control",    "5% droop rate, Q max 100%","",     "Control"),
    # Control Modes — Merchant
    _p("EMS_ARBITRAGE",         "Energy Arbitrage",         "Charge low / discharge high","",   "Control"),
    _p("EMS_PEAK_SHAVE",        "Peak Shaving / Assured Peak","Supported", "",                 "Control"),
    _p("EMS_SCHEDULED_DISPATCH","Scheduled Dispatch",       "96×15min blocks, day-ahead","",    "Control"),
    _p("EMS_TIME_SHIFTING",     "Energy Time Shifting",     "Supported",    "",                 "Control"),
    _p("EMS_SMOOTHING",         "Power Curve Smoothing",    "Supported",    "",                 "Control"),
    # Control Modes — Ancillary
    _p("EMS_FFR",               "Fast Frequency Response",  "Supported",    "",                 "Control"),
    _p("EMS_FCAS",              "FCAS (AEMO framework)",    "Supported",    "",                 "Control"),
    _p("EMS_BLACK_START",       "Black Start",              "Supported",    "",                 "Control"),
    _p("EMS_FIRMING",           "RE Firming",               "Intermittent → dispatchable","",   "Control"),
    _p("EMS_RTC",               "Round-the-Clock Supply",   "Supported",    "",                 "Control"),
    _p("EMS_DG_CONTROL",        "DG Integration Control",   "Supported",    "",                 "Control"),
    _p("EMS_ELECTROLYSER",      "Electrolyser Integration", "Green hydrogen support","",        "Control"),
    # Additional
    _p("EMS_SOC_MGMT",          "SOC Management",           "Predictive algorithms","",         "Control"),
    _p("EMS_DEGRADATION",       "Degradation-Aware Dispatch","Supported",   "",                 "Control"),
    _p("EMS_ISLANDING",         "Islanding Detection",      "Supported",    "",                 "Control"),
    # Performance
    _p("EMS_CTRL_REFRESH",      "EMS Control Refresh",      "1",            "sec",              "Performance"),
    _p("EMS_BESS_MONITORING",   "BESS Monitoring Interval", "1",            "min",              "Performance"),
    _p("EMS_SOE_RES",           "SOE Resolution",           "≤1",           "ms",               "Performance"),
    # SCADA
    _p("EMS_SCADA",             "SCADA HMI",                "Redundant operator workstations","","Features"),
    _p("EMS_ALARM_MGMT",        "Alarm Management",         "Multi-level configurable","",      "Features"),
    _p("EMS_TRENDING",          "Trending & Historicals",    "5+ years storage","",              "Features"),
    _p("EMS_REPORTS",           "Report Generation",        "Daily/Monthly/Annual","",          "Features"),
    _p("EMS_WEB_ACCESS",        "Web-Based Remote Access",  "Role-based","",                    "Features"),
    _p("EMS_MOBILE_APP",        "Mobile App",               "Not available","",                 "Features"),
    # Failover
    _p("EMS_FAILOVER",          "Failover Strategy",        "PPC continues on last setpoints","","Reliability"),
    _p("EMS_REDUNDANCY",        "Hot Standby",              "Project-specific server config","","Reliability"),
    # Cybersecurity
    _p("EMS_CYBERSECURITY",     "Cybersecurity Standard",   "IEC 62443 (pending confirmation)","","Security"),
    _p("EMS_RBAC",              "Role-Based Access Control", "Yes",          "",                 "Security"),
    _p("EMS_FIREWALL",          "Firewall & Segmentation",  "Yes",          "",                 "Security"),
    _p("EMS_IDS",               "Intrusion Detection",      "Yes",          "",                 "Security"),
    _p("EMS_ENCRYPTION",        "Encrypted Communication",  "Pending confirmation","",          "Security"),
    _p("EMS_VAPT",              "VAPT Testing",             "During commissioning only","",     "Security"),
    # Historian
    _p("EMS_HISTORIAN",         "Data Historian",           "5+ years","",                      "Storage"),
    # Certifications & Experience
    _p("EMS_CERTS",             "Certifications",           "IEC 61850 conformance (pending)","","Safety"),
    _p("EMS_BESS_EXPERIENCE",   "BESS Project Experience",  "5500+ MWh, 25+ projects","",      "Experience"),
    _p("EMS_LARGEST_PROJECT",   "Largest BESS Project",     "ACME 350MW/1400MWh","",            "Experience"),
    _p("EMS_GLOBAL_PRESENCE",   "Global Presence",          "15+ countries, 20+ grid codes","", "Experience"),
    _p("EMS_GRID_CODES",        "Grid Code Compliance",     "India, USA, Australia, KSA, South Africa + 15 more","","Compliance"),
]


EMS_PARAMETERS = {
    "comp-acrel-anet":      _ACREL_ANET,
    "comp-adaptive-ems":    _ADAPTIVE_EMS,
    "comp-eit-ems":         _EIT_EMS,
    "comp-sga-solvyn":      _SGA_SOLVYN,
}


