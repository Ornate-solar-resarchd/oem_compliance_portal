# UnityESS Technical Compliance Portal — Architecture

## Overview
BESS (Battery Energy Storage System) technical compliance portal for OEM evaluation, RFQ processing, and deal pipeline management.

**Stack:** Next.js 14 + Tailwind + shadcn/ui + Recharts | FastAPI + In-memory data | Gemini AI for document extraction

---

## Project Structure

```
OEM-anushthaFatehPortal/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py             # FastAPI app entry + CORS + routers
│   │   ├── api/v1/endpoints/   # REST API endpoints
│   │   │   ├── auth.py         # JWT login (demo users)
│   │   │   ├── oems.py         # OEM CRUD
│   │   │   ├── components.py   # Component models + params + datasheet upload
│   │   │   ├── projects.py     # Project management
│   │   │   ├── sheets.py       # Technical compliance sheets
│   │   │   ├── workflow.py     # 7-stage approval workflow
│   │   │   ├── rfq.py          # RFQ upload + AI extraction (Gemini/Claude/keyword)
│   │   │   ├── pipeline.py     # Deal pipeline (enquiry→rfq→meeting→proposal→final)
│   │   │   ├── dashboard.py    # KPI stats + chart data
│   │   │   ├── comparison.py   # Side-by-side model comparison matrix
│   │   │   ├── documents.py    # Document generation
│   │   │   ├── templates.py    # Compliance templates
│   │   │   └── mail.py         # Technical mail
│   │   └── data/
│   │       ├── seed.py         # In-memory seed data (OEMs, components, params, projects, pipeline)
│   │       └── rfq_extraction.py # AI extraction engine (Gemini → Claude → keyword fallback)
│   ├── requirements.txt
│   └── .env                    # API keys (GEMINI_API_KEY, ANTHROPIC_API_KEY)
│
├── frontend/                   # Next.js 14 (App Router)
│   ├── app/
│   │   ├── layout.tsx          # Root HTML layout
│   │   ├── page.tsx            # Redirect → /dashboard or /login
│   │   ├── login/page.tsx      # Login with demo credentials
│   │   └── (portal)/           # Protected routes (auth required)
│   │       ├── layout.tsx      # Sidebar + Header + Auth guard
│   │       ├── dashboard/      # KPI cards + charts
│   │       ├── pipeline/       # Deal pipeline Kanban board (NEW)
│   │       ├── technical-data/ # All OEM models grouped by manufacturer
│   │       ├── oems/           # OEM library + [id] detail page
│   │       ├── rfq/            # RFQ upload + AI extraction + detail view
│   │       ├── tech-signal/    # Tech signal sheets per component
│   │       ├── compare/        # Side-by-side model comparison
│   │       ├── projects/       # Project management
│   │       ├── workflow/       # Approval pipeline
│   │       └── settings/       # User settings
│   ├── components/
│   │   ├── ui/                 # shadcn/ui (Button, Card, Badge, Dialog, Progress, Input)
│   │   ├── layout/             # Sidebar (dark navy), Header (glass blur)
│   │   └── shared/             # ScoreRing (animated), StatusBadge, StageBadge
│   ├── lib/
│   │   ├── api.ts              # REST client (all backend API calls)
│   │   ├── auth.tsx            # AuthProvider + useAuth + JWT parsing
│   │   └── utils.ts            # cn(), scoreColor(), formatNumber()
│   ├── tailwind.config.ts      # Custom theme (brand colors, animations, shadows)
│   └── .env.local              # NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
│
└── .gitignore
```

---

## Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│  Backend API │────▶│  In-Memory   │
│  Next.js 14  │◀────│   FastAPI    │◀────│  Seed Data   │
│  Port 3000   │     │  Port 8000   │     │  (Python)    │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
                    ┌──────▼───────┐
                    │  Gemini AI   │
                    │  (PDF Parse) │
                    └──────────────┘
```

---

## Core Features

### 1. Deal Pipeline (`/pipeline`)
```
Enquiry → RFQ → Meeting → Request → Proposal → Final
```
Kanban board tracking deals from first contact to closure. 6 pre-loaded deals (NTPC, Evolve, BSPGCL, etc.)

### 2. Technical Data (`/technical-data`)
All OEM models grouped by manufacturer (CATL, Lishen, BYD, HiTHIUM, SVOLT). Card + List view toggle. Click to expand → full parameter table with charts.

### 3. RFQ Manager (`/rfq`)
Upload any RFQ PDF → Gemini AI reads the document → extracts 30-50 BESS technical requirements (capacity, RTE, certifications, EMS specs, grid support, etc.)

### 4. OEM Library (`/oems` + `/oems/[id]`)
OEM cards with compliance scores, country, approval status. Detail page with model scores, charts, electrical parameters.

### 5. Tech Signal (`/tech-signal`)
Per-component technical signal documents with parameter tables, electrical bar charts, confidence indicators.

### 6. Comparison (`/compare`)
Side-by-side parameter matrix. Filter by manufacturer, component type. Color-coded best/worst values.

### 7. Approval Workflow (`/workflow`)
7-stage pipeline: Draft → Eng Review → Tech Lead → Management → Customer Submission → Signoff → Locked

---

## OEMs in System

| OEM | Models | Avg Score | Country | Website |
|-----|--------|-----------|---------|---------|
| CATL | 2 | 97.5% | China | catl.com |
| Lishen | 2 | 91.2% | China | lishen.com.cn |
| BYD | 1 | 94.8% | China | byd.com |
| HiTHIUM | 1 | 87.4% | China | hithium.com |
| SVOLT | 2 | 93.1% | China | svolt.cn |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/login | JWT login |
| GET | /dashboard/stats | KPI metrics |
| GET | /oems/ | List OEMs |
| GET | /components/ | List component models |
| GET | /components/{id}/parameters | Model parameters |
| POST | /components/upload-datasheet | Upload OEM datasheet |
| GET | /projects/ | List projects |
| GET | /sheets/ | List compliance sheets |
| GET | /workflow/pending | Pending approvals |
| POST | /workflow/{id}/advance | Advance workflow |
| POST | /rfq/upload | Upload RFQ + AI extraction |
| GET | /rfq/{id} | RFQ detail |
| GET | /pipeline/ | Deal pipeline |
| POST | /pipeline/ | Create new lead |
| POST | /pipeline/{id}/advance | Move deal stage |
| GET | /comparison/matrix | Model comparison |
| GET | /templates/ | Compliance templates |
| POST | /documents/technical-signal | Generate tech signal |

---

## Authentication
- JWT tokens (HS256, 8hr expiry)
- 7 demo users: 3 Admin, 1 Engineer, 1 Reviewer, 1 Commercial, 1 Customer
- Role-based access (admin, engineer, reviewer, commercial, customer)

---

## AI Integration
RFQ extraction priority:
1. **Gemini API** (free, 1M context) — reads full PDF text
2. **Claude API** (paid fallback) — same extraction prompt
3. **Keyword extraction** (offline) — regex-based, always works

Extracts 60+ BESS parameters: system specs, performance, cell specs, certifications, fire safety, EMS/SCADA, grid support, O&M, solar integration, commercial terms.

---

## Running Locally

```bash
# Backend
cd backend && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
# Open http://localhost:3000
```
