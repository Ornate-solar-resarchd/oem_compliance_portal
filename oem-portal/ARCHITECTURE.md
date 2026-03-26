# UnityESS Technical Compliance Portal — Architecture v2.3

## Overview
BESS (Battery Energy Storage System) technical compliance portal for OEM evaluation, RFQ processing, datasheet extraction, and deal pipeline management.

**Stack:** Next.js 14 + Tailwind + shadcn/ui + Recharts | FastAPI + In-memory Data | Gemini AI + Google Drive

**Live URLs:**
- Frontend: https://oem-compliance-portal.vercel.app
- Backend: https://oem-compliance-portal.onrender.com

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vercel)                        │
│                     Next.js 14 + Tailwind                       │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Dashboard │ │OEM Lib   │ │RFQ Mgr   │ │Pipeline  │  + 8     │
│  │KPIs      │ │5 OEMs    │ │AI Extract│ │Kanban    │  more    │
│  │Workflow  │ │8 Models  │ │Drive Fetch│ │6 Stages  │  pages   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       └─────────────┴─────────────┴─────────────┘              │
│                          REST API                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────┴──────────────────────────────────────┐
│                       BACKEND (Render)                          │
│                    FastAPI + Python 3.11                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              14 API Endpoint Modules                   │      │
│  │  auth · oems · components · projects · sheets         │      │
│  │  workflow · rfq · pipeline · comparison · dashboard    │      │
│  │  documents · templates · mail · gdrive                │      │
│  └──────────────────────┬───────────────────────────────┘      │
│                         │                                       │
│  ┌──────────┐  ┌────────┴────────┐  ┌──────────────────┐      │
│  │In-Memory │  │  AI Extraction  │  │  Google Drive     │      │
│  │Seed Data │  │  Engine         │  │  Integration      │      │
│  │5 OEMs    │  │1. Gemini (free)│  │Search & Fetch    │      │
│  │8 Models  │  │2. Claude (paid)│  │via Apps Script   │      │
│  │28 params │  │3. Keywords     │  │                   │      │
│  │5 Projects│  │60+ params/doc  │  │                   │      │
│  │7 Sheets  │  │                 │  │                   │      │
│  │3 RFQs    │  │                 │  │                   │      │
│  │6 Deals   │  │                 │  │                   │      │
│  └──────────┘  └─────────────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
oem-portal/
├── backend/                          # FastAPI Python
│   ├── app/
│   │   ├── main.py                   # App entry + CORS + 14 routers
│   │   ├── api/v1/endpoints/         # 14 endpoint modules
│   │   │   ├── auth.py               # JWT login (7 demo users)
│   │   │   ├── oems.py               # OEM CRUD
│   │   │   ├── components.py         # Components + datasheet upload + AI extract
│   │   │   ├── projects.py           # Project management
│   │   │   ├── sheets.py             # Compliance sheets
│   │   │   ├── workflow.py           # 7-stage approval pipeline
│   │   │   ├── rfq.py               # RFQ upload + AI extraction
│   │   │   ├── pipeline.py           # Deal pipeline (6 stages)
│   │   │   ├── gdrive.py            # Google Drive integration
│   │   │   ├── comparison.py         # Model comparison matrix
│   │   │   ├── dashboard.py          # KPI stats + charts
│   │   │   ├── documents.py          # PDF generation
│   │   │   ├── templates.py          # Compliance templates
│   │   │   └── mail.py               # Technical email
│   │   └── data/
│   │       ├── seed.py               # All in-memory data
│   │       ├── rfq_extraction.py     # RFQ AI extraction (60+ params)
│   │       ├── datasheet_extraction.py # Datasheet AI parser
│   │       └── gdrive_upload.py      # Drive upload helper
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml
│   └── .env
│
├── frontend/                          # Next.js 14 (App Router)
│   ├── app/
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Redirect → /login or /dashboard
│   │   ├── login/page.tsx             # Login page
│   │   └── (portal)/                  # Protected routes
│   │       ├── layout.tsx             # Sidebar + Header + Auth guard
│   │       ├── dashboard/             # KPIs + workflow + projects
│   │       ├── oems/                  # OEM library + [id] detail
│   │       ├── rfq/                   # RFQ upload + AI + detail + compliance + diversify
│   │       ├── projects/              # Projects & Workflow
│   │       ├── compare/               # Model comparison matrix
│   │       ├── technical-data/        # All models by OEM
│   │       ├── pipeline/              # Deal pipeline Kanban
│   │       ├── tech-signal/           # Tech signal sheets
│   │       ├── workflow/              # Approval workflow
│   │       └── settings/              # Settings
│   ├── components/
│   │   ├── ui/                        # shadcn/ui components
│   │   ├── layout/                    # Sidebar, Header
│   │   └── shared/                    # ScoreRing, StatusBadge, DriveFetcherModal
│   ├── lib/
│   │   ├── api.ts                     # REST client
│   │   ├── auth.tsx                   # Auth context
│   │   └── utils.ts                   # Utilities
│   ├── Dockerfile
│   └── package.json
│
├── ARCHITECTURE.md
├── PROJECT_HANDOFF.md
└── .gitignore
```

---

## Core Business Flow

```
1. OEM LIBRARY (/oems)
   ├── Browse OEMs → Categories: Cell, DC Block, PCS, EMS
   ├── Upload datasheets → AI extracts 30-50+ specs
   └── Fetch from Google Drive → AI extracts specs (no duplicate)

2. RFQ MANAGER (/rfq)
   ├── Upload customer RFQ (PDF/Excel)
   ├── AI extracts 60+ BESS technical requirements
   └── Fetch RFQ from Google Drive

3. DEAL PIPELINE (/pipeline)
   └── Enquiry → RFQ → Meeting → Request → Proposal → Final

4. TECHNICAL DATA (/technical-data)
   └── All models grouped by OEM (Card + List view)

5. COMPARISON (/compare)
   └── Select 2+ models → Parameter matrix (filter by OEM, type, section)

6. PROJECTS & WORKFLOW (/projects)
   ├── Create projects → Add compliance sheets
   └── 7-stage approval: Draft → Eng Review → Tech Lead → Mgmt → Customer → Locked
```

---

## AI Extraction (Gemini → Claude → Keywords)

```
Document → Extract Text → Gemini 2.0 Flash (free) → 30-60+ params
                              ↓ (fallback)
                          Claude API (paid)
                              ↓ (fallback)
                          Keyword Regex (offline)
```

**Categories:** Cell (35+ params), DC Block (20+), PCS (22+), EMS (13+)

---

## Google Drive Integration

- **Search:** `GET /gdrive/search?q=CATL` → Search company Drive
- **Fetch & Extract:** `POST /gdrive/fetch-and-extract` → Download + AI extract
- **No duplicates:** Files fetched from Drive are NOT re-uploaded
- **Manual uploads:** Saved to Drive via Apps Script doPost()

---

## Authentication (7 Demo Users)

| Email | Role | Password |
|-------|------|----------|
| anushtha@ornatesolar.in | Admin | Admin@1234 |
| fateh@ornatesolar.in | Admin | Admin@1234 |
| kedar@ornatesolar.in | Admin | Admin@1234 |
| ravi.sharma@ornatesolar.in | Engineer | Ornate@1234 |
| priya.nair@ornatesolar.in | Reviewer | Ornate@1234 |
| arun.mehta@ornatesolar.in | Commercial | Ornate@1234 |
| vijay.k@sunsure.in | Customer | Customer@1234 |

---

## Deployment

| Service | Platform | Plan | Note |
|---------|----------|------|------|
| Backend | Render | Free | Sleeps after 15min idle |
| Frontend | Vercel | Free | No card required |

**Env vars:** GEMINI_API_KEY, SECRET_KEY, GDRIVE_FETCHER_URL, NEXT_PUBLIC_API_URL

---

*UnityESS TCP v2.3 — Ornate Agencies Pvt. Ltd.*
