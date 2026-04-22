"""
Data Completeness scoring — shared by oems + components endpoints.
Measures what % of core expected parameters each model has filled.
"""
from app.data.seed import PARAMETERS

# Core expected parameters per component type
CORE_PARAMS = {
    "Cell": {
        "CELL_CAPACITY_AH", "CELL_VOLTAGE_V", "CELL_ENERGY_WH",
        "CELL_CHARGE_CUTOFF_V", "CELL_DISCHARGE_CUTOFF_V",
        "CELL_CYCLE_LIFE", "CELL_EOL_RETENTION", "CELL_ENERGY_DENSITY_WH_KG",
        "CELL_CHARGE_TEMP_MIN", "CELL_CHARGE_TEMP_MAX",
        "CELL_DISCHARGE_TEMP_MIN", "CELL_DISCHARGE_TEMP_MAX",
        "CELL_CERTS", "CELL_CHEMISTRY", "CELL_FORM",
        "CELL_WEIGHT_KG", "CELL_LENGTH_MM", "CELL_WIDTH_MM", "CELL_HEIGHT_MM",
        "CELL_CALENDAR_LIFE", "CELL_RTE",
    },
    "PCS": {
        "PCS_RATED_POWER_KW", "PCS_AC_VOLTAGE_V",
        "PCS_DC_VOLTAGE_MIN", "PCS_DC_VOLTAGE_MAX",
        "PCS_FREQUENCY_HZ", "PCS_EFFICIENCY_PCT",
        "PCS_THD_PCT", "PCS_POWER_FACTOR",
        "PCS_IP_RATING", "PCS_COOLING",
        "PCS_OP_TEMP_MIN", "PCS_OP_TEMP_MAX",
        "PCS_WEIGHT_KG", "PCS_DIMENSIONS", "PCS_COMMS", "PCS_CERTS",
    },
    "EMS": {
        "EMS_TYPE", "EMS_PLATFORM",
        "EMS_MODBUS_TCP", "EMS_IEC104", "EMS_IEC61850",
        "EMS_ACTIVE_POWER", "EMS_REACTIVE_POWER", "EMS_FREQ_REG",
        "EMS_SOC_MGMT", "EMS_SCADA",
        "EMS_REDUNDANCY", "EMS_CYBERSECURITY", "EMS_HISTORIAN",
        "EMS_RBAC", "EMS_BESS_EXPERIENCE", "EMS_GRID_CODES",
    },
    "EMS Gateway": {
        "EMS_TYPE", "EMS_PLATFORM", "EMS_PROTOCOLS_DOWN", "EMS_PROTOCOLS_UP",
        "EMS_MAX_DEVICES", "EMS_OP_TEMP_MIN", "EMS_OP_TEMP_MAX",
    },
    "DC Block": {
        "DC_RATED_ENERGY_KWH", "DC_RATED_VOLTAGE_V", "DC_VOLTAGE_RANGE",
        "DC_CONFIGURATION", "DC_COOLING",
        "DC_OP_TEMP_MIN", "DC_OP_TEMP_MAX",
        "DC_IP_RATING", "DC_DIMENSIONS",
        "DC_FIRE_SUPPRESSION", "DC_BMS_LEVELS", "DC_COMMS", "DC_CERTS",
        "DC_FORM_FACTOR",
    },
    "DC-DC Converter": {
        "PCS_RATED_POWER_KW", "PCS_EFFICIENCY_PCT",
        "PCS_IP_RATING", "PCS_COOLING",
        "PCS_OP_TEMP_MIN", "PCS_OP_TEMP_MAX",
        "PCS_COMMS", "PCS_CERTS",
    },
}


def completeness(comp):
    """Data completeness: what % of core expected params does this model have.
    Core params → up to 90%. Extra params beyond core → up to 10% bonus."""
    params = PARAMETERS.get(comp["id"], [])
    comp_type = comp.get("component_type_name", "")
    core = CORE_PARAMS.get(comp_type, set())
    if not core:
        return 100.0 if params else 0.0
    filled_codes = {p["code"] for p in params}
    core_filled = len(core & filled_codes)
    core_pct = (core_filled / len(core)) * 90
    bonus_params = len(filled_codes - core)
    bonus_pct = min(bonus_params * 0.5, 10)
    return min(round(core_pct + bonus_pct, 1), 100.0)
