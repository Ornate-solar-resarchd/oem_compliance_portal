"""
In-memory data store — pre-loaded with Cell OEM seed data from real datasheets.
No database required. All data served from these lists/dicts.
DNV seed data is in app/data/dnv_seed.py (kept separately).
Cell seed data is in app/data/cell_seed.py (6 OEMs, 6 cell models).
"""
from app.data.cell_seed import CELL_OEMS, CELL_COMPONENTS, CELL_PARAMETERS
from app.data.pcs_seed import PCS_OEMS, PCS_COMPONENTS, PCS_PARAMETERS
from app.data.ems_seed import EMS_OEMS, EMS_COMPONENTS, EMS_PARAMETERS
from app.data.dcblock_seed import DCBLOCK_OEMS, DCBLOCK_COMPONENTS, DCBLOCK_PARAMETERS

# ─── OEM Library (cell + PCS + EMS + DC Block data, populated further by uploads) ───
OEMS = list(CELL_OEMS) + list(PCS_OEMS) + list(EMS_OEMS) + list(DCBLOCK_OEMS)
COMPONENTS = list(CELL_COMPONENTS) + list(PCS_COMPONENTS) + list(EMS_COMPONENTS) + list(DCBLOCK_COMPONENTS)
PARAMETERS = {**CELL_PARAMETERS, **PCS_PARAMETERS, **EMS_PARAMETERS, **DCBLOCK_PARAMETERS}

# ─── Projects & Workflow ───
PROJECTS = []
SHEETS = []
WORKFLOWS = []

# ─── RFQ Manager (populated by uploading RFQ PDFs) ───
RFQS = []

# ─── Documents & Templates ───
DOCUMENTS = []
TEMPLATES = []

# ─── Sales Pipeline ───
PIPELINE_STAGES = ["enquiry", "rfq", "meeting", "request", "proposal", "final"]

PIPELINE_STAGE_LABELS = {
    "enquiry":  "Enquiry / Lead",
    "rfq":      "RFQ Received",
    "meeting":  "Meeting / Discussion",
    "request":  "Bid Preparation",
    "proposal": "Proposal Submitted",
    "final":    "Final Decision",
}

PIPELINE = []
