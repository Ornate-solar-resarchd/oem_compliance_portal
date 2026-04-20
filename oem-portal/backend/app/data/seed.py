"""
In-memory data store — starts empty, populated by real uploads.
No database required. All data served from these lists/dicts.
DNV seed data is in app/data/dnv_seed.py (kept separately).
"""

# ─── OEM Library (populated by uploading datasheets) ───
OEMS = []
COMPONENTS = []
PARAMETERS = {}  # keyed by component_id

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
