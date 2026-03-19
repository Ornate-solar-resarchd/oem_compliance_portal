# ⚡ UnityESS Technical Compliance Portal

> **Enterprise BESS Component Compliance Management System**  
> Ornate Agencies Pvt. Ltd. · New Delhi, India  
> Version 2.1 · March 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Database Schema](#4-database-schema)
5. [Approval Workflow](#5-approval-workflow)
6. [Backend Services](#6-backend-services)
7. [Frontend Modules](#7-frontend-modules)
8. [Security & RBAC](#8-security--rbac)
9. [Document Generation](#9-document-generation)
10. [AI Extraction](#10-ai-extraction)
11. [Deployment](#11-deployment)
12. [Environment Variables](#12-environment-variables)
13. [Development Setup](#13-development-setup)
14. [API Reference](#14-api-reference)
15. [Data Immutability](#15-data-immutability)
16. [Roadmap](#16-roadmap)

---

## 1. Project Overview

The UnityESS Technical Compliance Portal is an enterprise-grade internal tool for managing the **technical approval lifecycle** of BESS component specifications across all active projects.

### What It Does

| Capability | Description |
|---|---|
| **OEM Repository** | Master database of all OEM partners, component models, and mapped technical parameters |
| **Parameter Engine** | Standard schema per component type; OEM values mapped and validated against it |
| **Compliance Builder** | Auto-generate compliance sheets from parameter mappings using named templates |
| **Approval Workflow** | 7-stage multi-role sign-off with digital signatures and immutable audit trail |
| **Comparison Engine** | Side-by-side OEM model comparison across any parameter set |
| **Document Generator** | Auto-export to branded PDF, Excel, and PPTX |
| **Customer Portal** | Scoped external interface for customer review and digital sign-off |
| **AI Extraction** | Upload OEM datasheet PDF → auto-extract and populate parameters via Claude API |

### Active Projects Tracked

| Project | Scale | Client | Stage |
|---|---|---|---|
| NTPC Barh | 200 MW / 400 MWh | NGSL | Technical Lead Review |
| TNGECL Eagle Infra | 5 MWh × 5 sites | Eagle Infra | Engineering Review |
| Sitapur Solar+BESS | 250 MW + 200 MWh | NTPC REL | Customer Submission |
| Amrita Hospital BTM | 11 MWp + 20 MWh | Amrita Hospital | Customer Sign-off |
| BSPGCL Bihar | 125 MW / 500 MWh | BSPGCL | 🔒 Locked v1.4 |

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  CLIENT LAYER                                               │
│  Next.js 14 (SSR)  ·  Mobile PWA  ·  Customer Portal       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / WSS
┌──────────────────────────▼──────────────────────────────────┐
│  GATEWAY LAYER                                              │
│  Cloudflare CDN/WAF  →  Nginx  →  Keycloak (JWT RS256)      │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────┐
│  SERVICE LAYER                          ┌─────────────────┐ │
│  FastAPI Core (Python 3.12)             │  Celery Workers │ │
│  ├── Parameter Engine                   │  (4 workers)    │ │
│  ├── Workflow Engine                    │                 │ │
│  ├── Compliance Engine                  │  • Doc gen      │ │
│  ├── Document Generator ──────────────► │  • AI extract   │ │
│  ├── AI Extraction Service              │  • Email notif  │ │
│  ├── Notification Service               │  • Audit snap   │ │
│  └── Audit Service                      └────────┬────────┘ │
└──────────────────────────┬─────────────────────┬─┘          │
                           │                     │ Redis       │
┌──────────────────────────▼─────────────────────▼────────────┐
│  DATA LAYER                                                 │
│  PostgreSQL 16 (Primary + Read Replica)                     │
│  Redis 7 (Cache · Queue · Sessions)                         │
│  MinIO (S3-compatible object storage)                       │
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  INFRASTRUCTURE  ·  AWS ap-south-1 (Mumbai)                 │
│  EC2 · RDS · ElastiCache · Vercel · GitHub Actions          │
└─────────────────────────────────────────────────────────────┘
```

**Data residency:** All data stored in `ap-south-1` (Mumbai) to comply with IT Act 2000 and NTPC/BSPGCL contract requirements.

---

## 3. Tech Stack

### Frontend
| Component | Technology | Rationale |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR for document preview, file-based routing |
| Language | TypeScript | Strict typing for compliance schemas and workflow states |
| Styling | Tailwind CSS + shadcn/ui | Utility-first, accessible component library |
| State | React Query + Zustand | Server state + client state separation |
| Deploy | Vercel | Zero-config deploy, CDN, edge functions |

### Backend
| Component | Technology | Rationale |
|---|---|---|
| API Framework | FastAPI (Python 3.12) | Async, auto-OpenAPI docs, Pydantic v2 |
| ORM | SQLAlchemy 2.0 async | Async queries, connection pooling |
| Task Queue | Celery + Redis | Async doc generation, AI extraction, email |
| Server | Uvicorn + Gunicorn | Production-grade ASGI server |
| Migrations | Alembic | Version-controlled schema migrations |

### Data
| Component | Technology | Rationale |
|---|---|---|
| Primary DB | PostgreSQL 16 | ACID, RLS, triggers, JSONB, partitioning |
| Cache / Queue | Redis 7 | Celery broker, session cache, rate limiting |
| Object Storage | MinIO (S3-compatible) | Datasheets, generated documents |
| Read Replica | PostgreSQL streaming | Offload reporting queries |

### Infrastructure
| Component | Technology |
|---|---|
| Cloud | AWS ap-south-1 (Mumbai) |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Auth | Keycloak 24 (SSO, OIDC, JWT RS256) |
| CDN / WAF | Cloudflare |
| Monitoring | Sentry + Prometheus + Grafana |

---

## 4. Database Schema

17 tables across 6 logical groups. Full schema: `schema.sql`

### Core OEM Group
```
oems ──────────────► component_models ──────────────► parameter_values
                          │                                   │
component_types ──────────┘                                   │
      │                                                       │
standard_parameters ──────────────────────────────────────────┘
```

### Compliance Group
```
compliance_templates ──► compliance_template_parameters
      │
projects ──► technical_sheets ──► sheet_compliance_results
```

### Workflow Group
```
technical_sheets ──► approval_workflows ──► workflow_steps (immutable)
```

### Key Design Decisions

- **JSONB for parameter values** — flexible storage for numeric, range, boolean, enum, and text types in a single table
- **Quarterly-partitioned audit_logs** — `audit_logs_2026_q1`, `_q2`, etc. — maintains query performance as records grow
- **Append-only workflow_steps** — DB trigger blocks UPDATE and DELETE at the PostgreSQL level
- **RLS policies** — customers see only their project's sheets at stage ≥ 5
- **Auto-sequences via triggers** — `TCS-001`, `WF-001` assigned on INSERT; no application logic required

### ENUMs Defined
`component_category` · `parameter_data_type` · `compliance_status` · `workflow_stage` · `approval_action` · `user_role` · `project_type` · `project_status` · `document_format` · `document_type`

---

## 5. Approval Workflow

### 7-Stage Pipeline

```
┌─────────┐    ┌────────────┐    ┌───────────┐    ┌────────────┐
│  DRAFT  │ ──► │ ENG REVIEW │ ──► │ TECH LEAD │ ──► │ MANAGEMENT │
│ Engineer│    │Sr. Engineer│    │ Tech Lead │    │ Commercial │
└─────────┘    └────────────┘    └───────────┘    └────────────┘
                                                         │
                    ┌────────────────────────────────────┘
                    ▼
             ┌─────────────┐    ┌─────────────┐    ┌────────┐
             │  CUSTOMER   │ ──► │  CUSTOMER   │ ──► │ LOCKED │
             │ SUBMISSION  │    │   SIGN-OFF  │    │  🔒    │
             │ Commercial  │    │  Customer   │    │ System │
             └─────────────┘    └─────────────┘    └────────┘
```

### Reject / Revision Loop
Any stage 2, 3, or 4 reviewer can reject with mandatory comment → sheet returns to **Draft** with incremented revision (r1 → r2 → r3). All rejection steps recorded immutably.

### Role × Stage Matrix

| Role | Draft | Eng. Review | Tech Lead | Management | Cust. Sub. | Sign-off | Locked |
|---|---|---|---|---|---|---|---|
| Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 👁 |
| Engineer | ✓ | — | — | — | — | — | 👁 |
| Reviewer | 👁 | ✓ | ✓ | — | — | — | 👁 |
| Commercial | 👁 | 👁 | 👁 | ✓ | ✓ | — | 👁 |
| Customer | — | — | — | — | 👁 | ✓ | 👁 |

`✓` = can act · `👁` = read-only · `—` = no access

### Stored Procedure
All stage transitions go through `advance_workflow()` PostgreSQL stored procedure — single atomic operation covering: workflow update + sheet stage update + step insert + audit log write.

---

## 6. Backend Services

### Service Map

```
app/
├── api/v1/endpoints/
│   ├── oems.py              # OEM CRUD
│   ├── components.py        # Component model CRUD
│   ├── parameters.py        # Parameter schema + values
│   ├── projects.py          # Project management
│   ├── sheets.py            # Technical compliance sheets
│   ├── workflow.py          # Approval workflow + steps
│   ├── comparison.py        # Comparison sets
│   ├── documents.py         # Document generation + download
│   └── ai.py               # AI datasheet extraction
├── services/
│   ├── parameter_engine.py  # Schema mapping + validation + scoring
│   ├── workflow_engine.py   # State machine + transition logic
│   ├── compliance_engine.py # Auto-evaluate + compliance %
│   ├── doc_generator.py     # PDF/XLSX/PPTX generation
│   ├── ai_extraction.py     # Claude API integration
│   └── audit_service.py     # Append-only audit logging
├── tasks/
│   ├── doc_tasks.py         # Celery: async doc generation
│   ├── ai_tasks.py          # Celery: async AI extraction
│   └── notification_tasks.py # Celery: email dispatch
├── models/                  # SQLAlchemy ORM models
├── schemas/                 # Pydantic v2 schemas
├── core/
│   ├── config.py            # Settings (pydantic-settings)
│   ├── security.py          # JWT verification + RBAC
│   └── database.py          # Async engine + session factory
└── main.py                  # FastAPI app entry point
```

### Key API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/oems` | List all OEMs with compliance scores |
| `POST` | `/api/v1/components` | Add new component model |
| `POST` | `/api/v1/sheets` | Create compliance sheet |
| `POST` | `/api/v1/workflow/{id}/advance` | Advance workflow stage |
| `GET` | `/api/v1/comparison/{id}/matrix` | Get comparison matrix |
| `POST` | `/api/v1/documents/generate` | Trigger async document generation |
| `POST` | `/api/v1/ai/extract` | Upload PDF and trigger AI extraction |
| `GET` | `/api/v1/audit/{entity_id}` | Get audit trail for entity |

---

## 7. Frontend Modules

| Module | Route | Description |
|---|---|---|
| Overview | `/` | Stats, recent approvals, activity feed, project strip |
| OEM Library | `/oem` | OEM cards, compliance scores, filter by category |
| Components | `/components` | Parameter table per component model |
| Compliance Builder | `/compliance` | Create/edit compliance sheets from templates |
| Approval Workflow | `/workflow` | Pipeline view, pending queue, stage actions |
| Comparison Engine | `/compare` | Side-by-side parameter comparison, score bars |
| Projects | `/projects` | Project cards with stage progress |
| Export Centre | `/documents` | Document type selector, download, recent exports |
| Customer Portal | `/customer/[token]` | Scoped external sign-off portal |
| Settings | `/settings` | User profile, notifications, role management (Admin) |

---

## 8. Security & RBAC

### Authentication Flow
```
Browser → Keycloak login → JWT (RS256) issued
→ All API requests carry Bearer token
→ FastAPI middleware verifies signature + extracts role claim
→ Route dependencies enforce role-based access
→ PostgreSQL RLS provides second enforcement layer
```

### Keycloak Configuration
- Realm: `unityess`
- Client: `compliance-portal-backend`
- Token expiry: 60 minutes
- Refresh token: 8 hours
- Roles mapped as JWT claims: `realm_access.roles`

### PostgreSQL Row-Level Security
```sql
-- Internal users: full access
-- Customer users: project-scoped, stage ≥ customer_submission only
-- Set at session level: app.user_role, app.user_id
```

### Security Headers (Nginx)
`Strict-Transport-Security` · `Content-Security-Policy` · `X-Frame-Options: DENY` · `X-Content-Type-Options: nosniff` · `Referrer-Policy: no-referrer`

---

## 9. Document Generation

### Supported Formats

| Format | Library | Use Case |
|---|---|---|
| PDF | WeasyPrint | Compliance sheets, customer packages, audit reports |
| Excel | openpyxl | Parameter matrices, comparison tables, version diffs |
| PPTX | python-pptx | OEM comparison decks, management presentations |

### Generation Flow
1. API receives export request → returns `task_id` immediately
2. Celery worker picks up task
3. Template rendered (Jinja2 for PDF HTML, direct API for XLSX/PPTX)
4. File uploaded to MinIO with SHA-256 checksum
5. `generated_documents` record updated with `is_ready = true`
6. Client polls `/api/v1/documents/{task_id}/status` → receives signed URL

### Branding
All outputs follow Ornate Solar brand identity:
- Font: **Chivo** (all weights)
- Primary colour: `#F26B4E`
- Dual logo header: Ornate Solar (left) + UnityESS (right)
- Paper: A4 · Currency: ₹ INR · Indian number formatting

---

## 10. AI Extraction

### Pipeline
```
Upload PDF → MinIO storage → Celery task queued
→ Claude API (claude-sonnet-4-6) → Structured JSON extraction
→ Map to standard parameter schema → Confidence scoring (0.00–1.00)
→ Low confidence (< 0.80) flagged for engineer review
→ Draft compliance sheet created → Notification sent
```

### System Prompt Strategy
- Structured output: JSON only, no prose
- Parameter codes from standard schema injected into prompt
- Component type determines which parameters to extract
- Handles prismatic cells, PCS specs, BMS parameters
- Falls back to manual entry on extraction failure (< 0.60 confidence)

### Confidence Thresholds
| Score | Action |
|---|---|
| ≥ 0.90 | Auto-verified |
| 0.80 – 0.89 | Flagged for review |
| < 0.80 | Requires manual entry |

---

## 11. Deployment

### Infrastructure (AWS ap-south-1)

| Service | Instance | Purpose |
|---|---|---|
| Next.js | Vercel | Frontend CDN |
| FastAPI | EC2 t3.medium | API + Celery workers |
| PostgreSQL | RDS db.t3.large | Primary database |
| Read Replica | RDS db.t3.medium | Reporting queries |
| Redis | ElastiCache r7g.medium | Queue + cache |
| MinIO | EC2 t3.small | Object storage |
| Keycloak | EC2 t3.small | Identity provider |

### CI/CD Pipeline (GitHub Actions)
```
push to main →
  lint (ruff, mypy) →
  test (pytest, 80% coverage required) →
  build Docker image →
  push to ECR →
  deploy to EC2 (rolling) →
  run Alembic migrations →
  health check →
  notify Slack
```

### Docker Compose (Production)
```yaml
services:
  api:        FastAPI + Uvicorn
  worker:     Celery (4 workers)
  beat:       Celery beat (scheduled tasks)
  flower:     Celery monitoring UI
  nginx:      Reverse proxy
  keycloak:   Identity provider
```

---

## 12. Environment Variables

See `.env.example` for full reference. Critical variables:

```bash
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_CLIENT_SECRET=...
ANTHROPIC_API_KEY=sk-ant-...
STORAGE_ACCESS_KEY=...
STORAGE_SECRET_KEY=...
SECRET_KEY=...  # 64-char random string
```

---

## 13. Development Setup

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker + Docker Compose
- PostgreSQL 16 client

### Quick Start

```bash
# Clone
git clone https://github.com/ornate-agencies/compliance-portal
cd compliance-portal

# Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in values

# Start infrastructure
docker compose up -d postgres redis minio keycloak

# Run migrations
alembic upgrade head

# Seed data (component types + standard parameters)
python scripts/seed.py

# Start API
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 14. API Reference

### Authentication
All endpoints require `Authorization: Bearer <jwt_token>` except `/health` and `/auth/token`.

### Response Format
```json
{
  "data": { ... },
  "meta": { "page": 1, "total": 84, "per_page": 20 },
  "error": null
}
```

### Error Codes
| Code | Meaning |
|---|---|
| `400` | Validation error (Pydantic) |
| `401` | Missing / invalid JWT |
| `403` | Insufficient role for this action |
| `404` | Entity not found |
| `409` | Conflict (e.g., duplicate model name) |
| `423` | Sheet is locked — no modifications permitted |
| `429` | Rate limit exceeded |
| `503` | Celery worker unavailable |

---

## 15. Data Immutability

Three categories of immutable data, enforced at the **PostgreSQL level** — cannot be bypassed by application code:

### 1. Locked Technical Sheets
```sql
-- Trigger: trg_sheet_immutability
-- Any UPDATE to a locked sheet raises EXCEPTION
-- Any DELETE on a locked sheet raises EXCEPTION
```

### 2. Workflow Steps
```sql
-- Trigger: trg_wf_step_immutability
-- No UPDATE or DELETE permitted on workflow_steps — ever
-- Steps are append-only from the moment of creation
```

### 3. Audit Logs
```sql
-- Trigger: trg_audit_immutability
-- No UPDATE or DELETE on audit_logs — ever
-- Quarterly partitions for performance; immutability applies to all partitions
```

### Version Snapshots
At every stage transition, `create_sheet_version()` stored procedure saves a complete JSONB snapshot of the sheet + model + OEM + results into `sheet_versions`. At lock, the `lock_hash` (SHA-256) is computed and stored.

---

## 16. Roadmap

### v2.2 (Q2 2026)
- [ ] Elasticsearch integration for full-text parameter search
- [ ] Bulk import from Excel (OEM parameter bulk upload)
- [ ] WhatsApp notification on pending approval (>48h)
- [ ] CERC BESS Regulation 2022 compliance template

### v2.3 (Q3 2026)
- [ ] Tender analysis module — auto-map tender specs to OEM models
- [ ] Multi-language support (Hindi UI)
- [ ] Mobile app (React Native)
- [ ] Integration with SAP for purchase order linkage

### v3.0 (Q4 2026)
- [ ] Marketplace: share compliance sheets across Ornate projects
- [ ] AI-powered OEM recommendation engine
- [ ] Public OEM compliance scorecards (industry benchmark)

---

## Regulatory References

| Standard | Scope | URL |
|---|---|---|
| IEC 62619:2022 | Battery safety | iec.ch |
| IEC 62477-1 | PCS safety | iec.ch |
| IEC 61850 | Communication | iec.ch |
| IS 16270:2014 | Indian battery standard | bis.gov.in |
| CEA Grid Connectivity Standards 2023 | Grid connection | cea.nic.in |
| CERC BESS Regulations 2022 | Commercial dispatch | cercind.gov.in |
| IT Act 2000 | Data residency | meity.gov.in |

---

## Contact

| Role | Name | Contact |
|---|---|---|
| Product Manager | Kedar Bala | kedar@ornateagencies.com |
| Company | Ornate Agencies Pvt. Ltd. | ornatesolar.com |
| Location | New Delhi, India | — |

---

*Last updated: March 2026 · UnityESS Technical Compliance Portal v2.1*  
*Ornate Agencies Pvt. Ltd. · Confidential*
