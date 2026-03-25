# Architecture Exploration: UnityESS OEM Portal

## Goal

Evolve the OEM Portal from a working POC into a maintainable, testable application that can handle real production traffic, persist data, and scale with new features (more OEMs, more RFQ types, more pipeline stages).

## Problem

The portal is **functionally complete but architecturally immature**:

1. **All data lives in memory** — lost on restart. `seed.py` is a 610-line god file holding 8 data domains
2. **Endpoints directly mutate global state** — no service layer, no transactions, race conditions possible
3. **Frontend pages are monolithic** — 400-500 line page files with inline config, forms, modals, charts, and filtering logic all in one component
4. **No type contracts** — API returns untyped dicts; frontend defines the same interfaces in multiple files
5. **No tests anywhere** — backend or frontend
6. **No data fetching abstraction** — every page has its own `useEffect → fetch → setState` boilerplate
7. **Configuration scattered** — OEM colors, stage configs, icon mappings duplicated across 5+ files

## Invariants

- Must remain a **Next.js 14 + FastAPI** stack (no framework migration)
- Must keep **shadcn/ui + Tailwind** design system
- Must preserve all **existing features** (dashboard, OEMs, RFQ extraction, pipeline, compliance, workflow, comparison, tech-signal)
- Must keep **Gemini → Claude → keyword** AI extraction fallback chain
- Demo mode with seed data must still work (for investor/customer demos)

## Non-Goals

- **Mobile app** — not in scope
- **Multi-tenancy** — single org for now
- **Microservices** — monolith is fine at this scale
- **Real-time collaboration** — not needed yet
- **CI/CD pipeline** — separate concern

## Constraints

- Small team (1-2 developers)
- Product designer doing engineering (stronger on frontend, learning backend)
- No existing tests to protect against regressions
- Must keep app functional during migration (can't do a big-bang rewrite)

## External Surfaces

| Surface | Protocol | Consumers |
|---------|----------|-----------|
| REST API `/api/v1/*` | HTTP/JSON | Frontend SPA |
| JWT auth tokens | Bearer header | Frontend auth context |
| Gemini API | HTTPS | RFQ extraction |
| Claude API | HTTPS | RFQ extraction fallback |
| File uploads | multipart/form-data | RFQ datasheet upload |

## Current System

| Area | Current Owner | Inputs | Outputs | Dependencies | Pain |
|------|---------------|--------|---------|--------------|------|
| Auth | `auth.py` + hardcoded users | email/password | JWT token | None | Hardcoded creds, no hashing |
| OEM CRUD | `oems.py` + `seed.OEMS` | API calls | OEM records | seed.py | Direct global mutation |
| Components | `components.py` + `seed.COMPONENTS/PARAMETERS` | API + file upload | Component models + params | seed.py, Gemini API | 224 params in one dict |
| RFQ Extraction | `rfq.py` + `rfq_extraction.py` | PDF upload | Extracted requirements | Gemini, Claude, seed.py | No output validation, brittle regex |
| Pipeline | `pipeline.py` + `seed.PIPELINE` | API calls | Deal records | seed.py | New feature, not battle-tested |
| Workflow | `workflow.py` + `seed.WORKFLOWS` | stage advance | Updated stage | seed.py | State machine logic in endpoint |
| Dashboard | `dashboard.py` | None | Stats + charts | seed.py (reads all) | Coupled to all data domains |
| Comparison | `comparison.py` | model IDs | Comparison matrix | seed.py | Heavy computation inline |
| Frontend Pages | 11 page files (350-500 lines each) | API responses | Rendered UI | api.ts, auth context | Monolithic, duplicated config |
| API Client | `lib/api.ts` | Function calls | Typed-ish responses | localStorage token | No caching, no error handling |

---

## Option 1: Layered Services (Evolutionary)

### Architecture Shape
Add a **service layer** between endpoints and data, plus a **repository pattern** for data access. Frontend gets **shared types**, **custom hooks**, and **extracted components**.

```
Backend:                          Frontend:
endpoints/ ──→ services/ ──→ repos/    pages/ ──→ hooks/ ──→ api.ts
                  ↑                       ↑
              models.py              types/ + components/
```

### What Changes
**Backend:**
- New `app/services/` layer (oem_service, rfq_service, pipeline_service, workflow_service)
- New `app/repositories/` layer abstracting data access (starts with in-memory, swappable to DB)
- New `app/models/` with Pydantic request/response schemas
- Endpoints become thin controllers calling services
- Workflow gets a proper state machine class

**Frontend:**
- New `types/` directory with shared domain types (OEM, Component, Deal, RFQ, etc.)
- New `hooks/` directory with data-fetching hooks (`useOEMs()`, `usePipeline()`, etc.)
- Extract config objects to `lib/config.ts`
- Extract modal/dialog components from pages
- Extract chart components

### What Stays
- File/folder structure stays similar
- All current features preserved
- seed.py data stays as the in-memory implementation of repositories
- API route paths unchanged

### What Gets Simpler
- Pages drop from 400-500 lines to 150-250 lines
- Adding a new endpoint = write service + thin controller
- Swapping to a database = implement repository interface, no service changes
- Type errors caught at compile time

### What Gets Harder
- More files to navigate (service + repo + model per domain)
- Learning curve for repository pattern (new concept for the team)
- Need discipline to not bypass service layer

### Boundary Changes
- **New boundary:** Service layer (endpoints can't touch data directly)
- **New boundary:** Repository interface (services can't touch storage implementation)
- **Clearer boundary:** Frontend types directory (single source of truth for shapes)

### Ownership Model
- Each service owns its domain logic
- Each repository owns its data access
- Pages own rendering only

### Data Flow
```
Request → Endpoint → Service → Repository → Data Store
                        ↓
                   Pydantic Model
                        ↓
Response ← Endpoint ← Service
```

### Operational Model
- Same deployment (single FastAPI + single Next.js)
- Structured logging via Python `logging` module
- Error responses standardized via Pydantic

---

## Option 2: Thin Backend + Rich Frontend (Simplifying)

### Architecture Shape
Aggressively simplify the backend to a **thin data API** — just CRUD + AI extraction. Move all business logic (filtering, grouping, comparison, dashboard calculations) to the frontend. Use **React Query** for caching and state.

```
Backend: endpoints/ ──→ seed.py (or DB)     # Minimal, just data I/O
Frontend: pages/ ──→ React Query ──→ api.ts  # All logic here
              ↑
         lib/transforms.ts  # Filtering, grouping, calculations
```

### What Changes
**Backend:**
- Strip dashboard calculations, comparison matrix building, etc.
- Backend becomes: auth, CRUD for each entity, file upload + AI extraction
- Add Pydantic response models (still needed for API contract)
- Keep seed.py as-is or split by domain

**Frontend:**
- Add React Query for data fetching + caching
- Move filtering/grouping/calculation logic to `lib/transforms.ts`
- Extract components from pages
- Add shared types

### What Stays
- Backend stays simple (even simpler than now)
- Frontend stays the primary codebase
- AI extraction stays on backend (needs API keys)

### What Gets Simpler
- Backend is trivially testable (just CRUD)
- Frontend has full control over data transformation
- React Query eliminates manual loading/error states
- Fewer backend endpoints to maintain

### What Gets Harder
- Frontend bundle size grows (more logic shipped to browser)
- Complex calculations in browser (comparison matrix with 500+ params)
- Harder to share logic if a mobile app is ever needed
- Testing transforms requires JS test infrastructure

### Boundary Changes
- Backend becomes a data gateway, not a domain service
- All business rules live in one place (frontend)

### Ownership Model
- Backend owns: auth, persistence, AI extraction
- Frontend owns: everything else

### Data Flow
```
Backend: Request → Endpoint → Data Store → Response (raw data)
Frontend: Page → React Query → API → Cache → Transform → Render
```

---

## Option 3: Domain Modules (Structural)

### Architecture Shape
Reorganize into **vertical domain modules**, each containing its own endpoint, service, types, and seed data. Backend and frontend mirror each other's structure.

```
backend/app/domains/
├── oem/
│   ├── router.py
│   ├── service.py
│   ├── models.py
│   └── seed.py
├── rfq/
│   ├── router.py
│   ├── service.py
│   ├── extraction.py
│   ├── models.py
│   └── seed.py
├── pipeline/
│   ├── router.py
│   ├── service.py
│   ├── models.py
│   └── seed.py
└── shared/
    ├── auth.py
    └── types.py

frontend/features/
├── oem/
│   ├── components/
│   ├── hooks/
│   ├── types.ts
│   └── config.ts
├── rfq/
│   ├── components/
│   ├── hooks/
│   ├── types.ts
│   └── config.ts
└── pipeline/
    └── ...
```

### What Changes
- **Complete reorganization** of both backend and frontend directory structures
- Every domain becomes self-contained
- Shared types/utilities extracted to `shared/` modules
- seed.py split into per-domain seed files
- Pages become thin shells importing from feature modules

### What Stays
- All features preserved
- Same tech stack
- Same API contract (routes don't change)

### What Gets Simpler
- Working on one domain doesn't require understanding others
- New domains are copy-paste-modify of existing ones
- Each domain is independently testable
- Clear ownership per module

### What Gets Harder
- **Massive file reorganization** — every import path changes
- Cross-domain queries (dashboard needs data from all domains)
- Risk of over-modularization at this scale (6 domains × 4-5 files = 25+ new files)
- Next.js App Router doesn't natively support feature-based frontend structure (pages must live in `app/`)

### Boundary Changes
- Strong vertical boundaries between domains
- Shared module for cross-cutting concerns

### Ownership Model
- Each domain module is a self-contained unit
- Shared module owned collectively

### Data Flow
```
Request → Domain Router → Domain Service → Domain Repository → Domain Seed
                              ↓
                        Domain Models
```

---

## Option 4: Do Less — Fix the Worst Pain Points Only

### Architecture Shape
Keep the current architecture. Fix only the 3-4 most painful issues without restructuring.

**Targeted fixes:**
1. Split `seed.py` into 4 files (OEM, component, pipeline, rfq)
2. Add Pydantic response models to endpoints
3. Extract frontend types to `types/` directory
4. Add React Query for data fetching (replaces manual useEffect)

### What Changes
- seed.py split (straightforward file split, no new patterns)
- Response models added to existing endpoints
- Frontend gets `types/` dir and React Query integration
- Pages get slightly smaller via hook extraction

### What Stays
- Everything else — no service layer, no repository, no domain modules
- Endpoints still directly access data (just from split files)
- Pages still contain most logic (just with hooks for fetching)

### What Gets Simpler
- seed.py diffs become manageable
- API responses are typed and documented
- Frontend data fetching is cleaner
- Types stop being duplicated

### What Gets Harder
- Nothing gets harder — these are pure wins
- But structural problems remain (no service layer, no testability, no state machine)

### Boundary Changes
- None — same architecture, better hygiene

### Ownership Model
- Unchanged

---

## Tradeoff Matrix

| Dimension | Option 1: Layered Services | Option 2: Thin Backend | Option 3: Domain Modules | Option 4: Do Less |
|-----------|---------------------------|----------------------|--------------------------|-------------------|
| **Simplicity** | Medium — adds layers but each is simple | High — fewer backend concepts | Low — many new directories | Highest — minimal change |
| **Migration Difficulty** | Medium — incremental, domain by domain | Medium — React Query + logic migration | High — all import paths change | Low — independent fixes |
| **Cleanup Burden** | Low — old patterns replaced in-place | Low — backend gets simpler | High — must move every file | None |
| **Testability** | High — services testable in isolation | Medium — frontend logic needs JS tests | High — domains testable independently | Low — same problems |
| **Operability** | Better — structured logging, error handling | Same — logging still needed | Better — per-domain observability | Same |
| **Extensibility** | High — new features = new service + endpoint | Medium — new features split across FE/BE | High — new domain = new module | Low — same friction |
| **Learning Curve** | Medium — service/repo patterns | Low — React Query is familiar | High — new project structure | None |
| **Risk of Over-Engineering** | Low | Low | **High** — 6 domains is too few for this pattern | None |
| **Database Migration Path** | **Excellent** — swap repo implementation | Good — backend is simple | Good — per-domain repos | Poor — still coupled to globals |

## Assumptions

| Assumption | Why It Matters | How to Verify | Fastest Disproof |
|------------|----------------|---------------|------------------|
| Team will grow to 2-3 devs in next 6 months | Affects how much structure is worth investing in | Ask founder | If staying solo, Option 4 may suffice |
| Database migration is needed within 3 months | Justifies repository pattern investment | Product roadmap | If demos-only indefinitely, in-memory is fine |
| Frontend is the primary development surface | Affects where to invest architecture effort | Git commit frequency | If backend-heavy features coming, invest more there |
| Comparison matrix with 500+ params is expensive | Affects where computation should live | Profile actual response times | If <100ms, keep on backend |

## Risk Register

| Risk | Option(s) Affected | Likelihood | Impact | Mitigation |
|------|-------------------|------------|--------|------------|
| Over-engineering for current scale | Option 3 | High | Medium — wasted effort | Choose Option 1 or 4 instead |
| Breaking existing features during migration | Options 1, 2, 3 | Medium | High — demo failures | Migrate incrementally, test each domain |
| React Query learning curve | Options 1, 2 | Low | Low — good docs | Start with one page, expand |
| Repository pattern unfamiliar to team | Option 1 | Medium | Medium — slow progress | Start with simplest domain (OEM), use as template |
| Frontend becomes too heavy with business logic | Option 2 | Medium | Medium — perf issues | Profile early, keep transforms efficient |

## Pre-Mortem (per option)

### Option 1 Failed After 6 Months
| Failure Mode | Warning Signal | Prevention |
|--------------|----------------|------------|
| Service layer becomes pass-through (no real logic) | Services just forward to repos | Only create services when there's actual business logic |
| Team bypasses service layer for speed | Direct seed.py imports in new endpoints | Code review, linting rule |
| Repository interface too generic | Repository methods don't match actual queries | Design repos around use cases, not CRUD |

### Option 2 Failed After 6 Months
| Failure Mode | Warning Signal | Prevention |
|--------------|----------------|------------|
| Frontend bundle too large | Slow page loads, large JS bundles | Monitor bundle size, lazy-load transforms |
| Duplicated logic when mobile app needed | Same calculations reimplemented in Swift/Kotlin | Extract to shared API if this becomes real |

### Option 3 Failed After 6 Months
| Failure Mode | Warning Signal | Prevention |
|--------------|----------------|------------|
| Cross-domain queries become painful | Dashboard requires imports from 6 domain modules | Create a query/reporting module |
| Too many small files, hard to navigate | Developers can't find things | Good IDE setup, clear naming |
| Reorg itself takes too long, stalls other work | 2+ weeks of just moving files | Don't attempt until team has bandwidth |

## Disqualifiers

- **Option 3** is disqualified if the team stays at 1-2 developers — the overhead of maintaining 6 domain modules with 25+ files is not justified for a team this small
- **Option 2** is disqualified if backend business logic will grow significantly (e.g., automated RFQ scoring, approval workflows with complex rules)
- **Option 4** is disqualified if database migration is needed within 3 months — it doesn't create the abstraction layer needed for that
- **Option 1** is disqualified if the team wants to ship features fast with zero architecture investment — the upfront cost is real

## Validation Spikes

| Spike | Question Answered | Cost | Success Signal | Failure Signal |
|-------|-------------------|------|----------------|----------------|
| Implement `OEMService` + `OEMRepository` with in-memory impl | Does the layered pattern feel natural for this codebase? | 2-3 hours | Clean separation, endpoint becomes 5-10 lines | Service is pure pass-through, adds no value |
| Add React Query to one page (e.g., Pipeline) | Does RQ eliminate enough boilerplate to justify the dependency? | 1-2 hours | Page drops 30+ lines, caching works | Minimal code reduction, adds complexity |
| Split seed.py into 4 files | Is the data cleanly separable? | 30 min | Each file is independent, no circular refs | Domains are deeply interleaved |
| Add Pydantic models to pipeline endpoints | Does typed responses catch real bugs? | 1 hour | Catches at least one existing type mismatch | No issues found, feels like busywork |

---

## Recommendation

**Option 1: Layered Services** — with the scope of Option 4 as the **first milestone**.

### Why It Wins
- Best **database migration path** — the repository pattern is specifically designed for swapping storage backends
- **Incremental** — can be done one domain at a time while the app stays functional
- **Right-sized** for a growing team — adds enough structure to prevent chaos without the overhead of full domain modules
- **Teaches good patterns** — service/repository is the most widely used backend architecture pattern, good investment in your engineering growth
- Frontend improvements (types, hooks, extracted components) pair naturally with backend services

### Execution Order
1. **Week 1 (Option 4 scope):** Split seed.py, add Pydantic models, extract frontend types, add React Query to 1-2 pages
2. **Week 2-3:** Add service layer for Pipeline and RFQ (most active domains), extract workflow state machine
3. **Week 4:** Add repository interface, implement in-memory repos, swap endpoints to use services
4. **Week 5+:** Frontend component extraction, remaining domain services, database migration prep

### Why the Runner-Up Loses
**Option 4 (Do Less)** is the runner-up. It's the right *first step* but doesn't set up for database migration. If you only do Option 4, you'll need to do Option 1 anyway when persistence becomes a requirement — so start with Option 4's scope but aim for Option 1's architecture.

### Why the Other Options Lose
- **Option 2 (Thin Backend)** puts too much logic on the frontend. The portal has real backend business logic (workflow state machines, RFQ extraction, compliance scoring) that belongs server-side
- **Option 3 (Domain Modules)** is over-engineered for 1-2 developers and 6 domains. The reorganization cost is high and the benefits don't justify it until the team grows to 4+

### What Could Change the Recommendation
- If database migration is **not** needed in the next 6 months → do Option 4 only
- If the team grows to **4+ developers** within 3 months → reconsider Option 3
- If the product pivots to being **frontend-heavy** (e.g., offline-first, complex client-side calculations) → reconsider Option 2

### What Must Be Validated Before Committing
- Run the `OEMService` + `OEMRepository` spike (2-3 hours) to confirm the pattern feels natural
- Run the React Query spike on Pipeline page (1-2 hours) to confirm frontend benefit

---

## Handoff to audit-and-migrate

### Chosen Architecture
Option 1: Layered Services with Option 4 as first milestone

### Decision Rationale
Best balance of incremental migration, database readiness, team learning, and feature velocity for a 1-2 person team building a production BESS compliance portal.

### Invariants
- Next.js 14 + FastAPI stack preserved
- All 11 features remain functional throughout migration
- shadcn/ui + Tailwind design system unchanged
- Demo mode with seed data must always work
- AI extraction fallback chain (Gemini → Claude → keyword) preserved

### Non-Goals
- No microservices, no multi-tenancy, no mobile app
- No CI/CD setup (separate concern)
- No database migration yet (just prep the abstraction layer)

### Critical Workflows
1. RFQ Upload → AI Extraction → Requirement Display → OEM Matching
2. Pipeline Deal → Stage Advancement → Activity History
3. Component Upload → Parameter Extraction → Compliance Scoring
4. Workflow Stage → Approval Chain → Lock

### External Surfaces
- REST API at `/api/v1/*` (routes unchanged)
- JWT auth (currently hardcoded, to be improved)
- Gemini + Claude API keys in `.env`
- File upload via multipart/form-data

### Known Hotspots
- `seed.py` (610 lines, 8 data domains in one file)
- `technical-data/page.tsx` (400+ lines, most complex frontend page)
- `rfq_extraction.py` (422 lines, AI + regex extraction)
- `workflow.py` (state machine logic buried in endpoint)
- Frontend: OEM_INFO, STAGE_CONFIG duplicated across 5+ files

### Leading Migration Risks
- Breaking existing features during service layer introduction
- Over-abstracting repositories for domains that are simple CRUD
- React Query integration causing unexpected cache invalidation behavior

### Expected Deletion Zones
- Inline `useEffect` fetch patterns in all pages (replaced by React Query hooks)
- Duplicate type definitions across page files (replaced by `types/`)
- Duplicate config objects (OEM_INFO, STAGE_CONFIG) across pages (replaced by `lib/config.ts`)
- Direct seed.py imports in endpoints (replaced by service layer)

### Validation Spikes Already Run
- None yet — recommended before committing

### What Still Needs Proof
- Repository pattern doesn't become pure pass-through for simple domains
- React Query actually reduces meaningful boilerplate
- seed.py data is cleanly separable into domain files
