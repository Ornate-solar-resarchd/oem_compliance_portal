"""
In-memory data store — pre-loaded with Cell OEM seed data from real datasheets.
No database required. All data served from these lists/dicts.
DNV seed data is in app/data/dnv_seed.py (kept separately).
Cell seed data is in app/data/cell_seed.py (6 OEMs, 6 cell models).
"""
from app.data.cell_seed import CELL_OEMS, CELL_COMPONENTS, CELL_PARAMETERS

# ─── OEM Library (pre-loaded with cell data + populated by uploads) ───
OEMS = list(CELL_OEMS)
COMPONENTS = list(CELL_COMPONENTS)
PARAMETERS = dict(CELL_PARAMETERS)  # keyed by component_id

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
