# API Specification — UnityESS Technical Compliance Portal
> For Cowork / developer handover. Complete endpoint definitions, request/response schemas, auth requirements, error contracts.  
> Version: 2.1 · March 2026

---

## Global Conventions

### Base URL
```
Production:  https://api.compliance.unityess.in/api/v1
Development: http://localhost:8000/api/v1
```

### Authentication
Every endpoint (except `/health` and `/auth/token`) requires:
```
Authorization: Bearer <jwt_token>
```
JWT issued by Keycloak. Contains claim `realm_access.roles` — array of role strings.  
Valid roles: `admin`, `engineer`, `reviewer`, `commercial`, `customer`

### Standard Response Envelope
```json
{
  "data": { ... } | [ ... ] | null,
  "meta": { "page": 1, "per_page": 20, "total": 84 },
  "error": null
}
```
On error:
```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "SHEET_LOCKED",
    "message": "This compliance sheet is locked and cannot be modified.",
    "detail": { "sheet_id": "uuid", "locked_at": "2026-01-15T10:22:00Z" }
  }
}
```

### Error Codes
| HTTP | Code | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Pydantic validation failure — `detail` contains field errors |
| 401 | `INVALID_TOKEN` | Missing, expired, or malformed JWT |
| 403 | `INSUFFICIENT_ROLE` | User role cannot perform this action at this workflow stage |
| 404 | `NOT_FOUND` | Entity does not exist |
| 409 | `DUPLICATE` | Unique constraint violation (e.g., model name already exists for this OEM) |
| 422 | `UNPROCESSABLE` | Business logic rejection — see `code` for specifics |
| 423 | `SHEET_LOCKED` | Sheet is at stage `locked` — no writes permitted |
| 429 | `RATE_LIMITED` | 1000 req/min per user; AI endpoint 10 req/min |
| 503 | `WORKER_UNAVAILABLE` | Celery worker not reachable (document generation / AI extraction) |

### Pagination
All list endpoints accept:
```
?page=1&per_page=20&sort_by=created_at&sort_dir=desc
```

### UUID Format
All IDs are UUID v4. In the DB schema they are `uuid` type with `gen_random_uuid()` default.

---

## Endpoint Groups

1. [Health](#1-health)
2. [Auth](#2-auth)
3. [OEMs](#3-oems)
4. [Component Types](#4-component-types)
5. [Standard Parameters](#5-standard-parameters)
6. [Component Models](#6-component-models)
7. [Parameter Values](#7-parameter-values)
8. [Projects](#8-projects)
9. [Compliance Templates](#9-compliance-templates)
10. [Technical Sheets](#10-technical-sheets)
11. [Workflow](#11-workflow)
12. [Comparison](#12-comparison)
13. [Documents](#13-documents)
14. [AI Extraction](#14-ai-extraction)
15. [Audit](#15-audit)
16. [Users](#16-users)

---

## 1. Health

### `GET /health`
Public. No auth.

**Response 200:**
```json
{
  "status": "ok",
  "db": "ok",
  "redis": "ok",
  "worker": "ok",
  "version": "2.1.0"
}
```

---

## 2. Auth

Auth is handled by Keycloak. The FastAPI backend does **not** issue tokens — it only validates them.

### `POST /auth/token` (Keycloak proxy — dev only)
In production, the frontend hits Keycloak directly. This endpoint is only exposed in development for convenience.

**Request:**
```json
{ "username": "string", "password": "string" }
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### JWT Claim Structure
```json
{
  "sub": "uuid",
  "preferred_username": "kedar.bala",
  "email": "kedar@ornateagencies.com",
  "realm_access": {
    "roles": ["engineer", "default-roles-unityess"]
  },
  "exp": 1712345678
}
```
The backend reads `realm_access.roles[0]` as the user's role. If a user has multiple roles, `admin` takes precedence, then `reviewer`, then others.

---

## 3. OEMs

### `GET /oems`
Roles: all

**Query params:** `?category=battery_cell&country=CN&search=catl`

**Response 200 — `data` array:**
```json
[
  {
    "id": "uuid",
    "name": "CATL",
    "country_code": "CN",
    "website": "https://catl.com",
    "contact_email": "india@catl.com",
    "contact_name": "Zhang Wei",
    "is_approved": true,
    "compliance_score": 98.2,
    "model_count": 8,
    "categories": ["battery_cell"],
    "created_at": "2025-06-01T00:00:00Z",
    "updated_at": "2026-01-10T00:00:00Z"
  }
]
```

### `POST /oems`
Roles: `admin`, `engineer`

**Request body:**
```json
{
  "name": "string (required, unique)",
  "country_code": "string (2-char ISO, required)",
  "website": "string (url, optional)",
  "contact_email": "string (email, optional)",
  "contact_name": "string (optional)",
  "notes": "string (optional)"
}
```

**Response 201:** Full OEM object (same as GET item)

### `GET /oems/{oem_id}`
Roles: all

**Response 200:** Full OEM object + `models` array (summary only — id, name, category, compliance_score)

### `PATCH /oems/{oem_id}`
Roles: `admin`, `engineer`

**Request body:** Any subset of POST fields.

**Response 200:** Updated OEM object.

### `DELETE /oems/{oem_id}`
Roles: `admin` only

Only permitted if OEM has zero component models. Returns `422 UNPROCESSABLE` with code `OEM_HAS_MODELS` otherwise.

---

## 4. Component Types

### `GET /component-types`
Roles: all

**Response 200 — `data` array:**
```json
[
  {
    "id": "uuid",
    "name": "Battery Cell",
    "slug": "battery_cell",
    "category": "battery_cell",
    "parameter_count": 28,
    "description": "LFP prismatic or cylindrical battery cells"
  }
]
```

Valid `category` enum values: `battery_cell`, `battery_module`, `battery_pack`, `pcs`, `bms`, `ems`, `transformer`, `hvac`, `fire_suppression`, `structure`, `bos`

### `GET /component-types/{type_id}/parameters`
Roles: all

Returns all standard parameters for this component type. Used to build the compliance template UI.

**Response 200 — `data` array:** See Standard Parameters schema below.

---

## 5. Standard Parameters

### `GET /standard-parameters`
Roles: all

**Query params:** `?component_type_id=uuid&mandatory_only=true`

**Response 200 — `data` array:**
```json
[
  {
    "id": "uuid",
    "component_type_id": "uuid",
    "code": "CELL_CAPACITY_AH",
    "display_name": "Nominal Capacity",
    "unit": "Ah",
    "data_type": "numeric",
    "is_mandatory": true,
    "sort_order": 1,
    "validation_rules": {
      "min": 50,
      "max": 500
    },
    "regulatory_reference": "IEC 62619:2022 Cl. 7.2",
    "description": "Nominal rated capacity at 0.2C discharge rate at 25°C"
  }
]
```

`data_type` enum: `numeric`, `range`, `text`, `boolean`, `enum`, `percentage`, `temperature_range`

`validation_rules` structure per type:
- `numeric`: `{ "min": number, "max": number }`
- `range`: `{ "min_low": number, "max_high": number }`
- `enum`: `{ "options": ["string"] }`
- `percentage`: `{ "min": 0, "max": 100 }`
- `temperature_range`: `{ "min": -40, "max": 85 }`
- `text`: `{ "max_length": 500 }`
- `boolean`: `{}`

### `POST /standard-parameters`
Roles: `admin` only

**Request body:**
```json
{
  "component_type_id": "uuid (required)",
  "code": "string (required, unique within component_type, SCREAMING_SNAKE_CASE)",
  "display_name": "string (required)",
  "unit": "string (optional, SI unit symbol)",
  "data_type": "numeric|range|text|boolean|enum|percentage|temperature_range (required)",
  "is_mandatory": "boolean (default: true)",
  "sort_order": "integer (default: next available)",
  "validation_rules": "object (required, structure depends on data_type)",
  "regulatory_reference": "string (optional, e.g. 'IEC 62619:2022 Cl. 7.2')",
  "description": "string (optional)"
}
```

**Response 201:** Full standard parameter object.

---

## 6. Component Models

### `GET /component-models`
Roles: all

**Query params:** `?oem_id=uuid&component_type_id=uuid&search=280ah`

**Response 200 — `data` array:**
```json
[
  {
    "id": "uuid",
    "oem_id": "uuid",
    "oem_name": "CATL",
    "component_type_id": "uuid",
    "component_type_name": "Battery Cell",
    "component_type_slug": "battery_cell",
    "model_name": "CATL-LFP-280AH-3.2V",
    "model_number": "EVE-LF280K",
    "datasheet_url": "https://storage.../catl-280ah.pdf",
    "compliance_score": 97.5,
    "parameter_fill_rate": 100.0,
    "is_active": true,
    "created_at": "2025-08-15T00:00:00Z"
  }
]
```

### `POST /component-models`
Roles: `admin`, `engineer`

**Request body:**
```json
{
  "oem_id": "uuid (required)",
  "component_type_id": "uuid (required)",
  "model_name": "string (required, unique within OEM)",
  "model_number": "string (optional)",
  "notes": "string (optional)"
}
```

**Response 201:** Full component model object.

### `GET /component-models/{model_id}`
Roles: all

**Response 200:** Component model object + `parameter_values` array (all params for this model, including nulls for unmapped ones).

### `PATCH /component-models/{model_id}`
Roles: `admin`, `engineer`

### `DELETE /component-models/{model_id}`
Roles: `admin` only. Blocked if model is referenced in any technical sheet.

---

## 7. Parameter Values

### `GET /component-models/{model_id}/parameters`
Roles: all

Returns all standard parameters for the model's component type, with each OEM value filled in (or null if not yet mapped).

**Response 200 — `data` array:**
```json
[
  {
    "id": "uuid (null if not yet set)",
    "standard_parameter_id": "uuid",
    "code": "CELL_CAPACITY_AH",
    "display_name": "Nominal Capacity",
    "unit": "Ah",
    "data_type": "numeric",
    "is_mandatory": true,
    "value_numeric": 280.0,
    "value_range_min": null,
    "value_range_max": null,
    "value_text": null,
    "value_boolean": null,
    "value_enum": null,
    "confidence_score": 0.95,
    "source": "ai_extracted",
    "notes": "Extracted from datasheet p.3",
    "regulatory_reference": "IEC 62619:2022 Cl. 7.2"
  }
]
```

`source` enum: `manual`, `ai_extracted`, `imported`

### `PUT /component-models/{model_id}/parameters`
Roles: `admin`, `engineer`

Bulk upsert — replaces/creates all parameter values for the model in one operation. Used by the parameter mapping UI and after AI extraction review.

**Request body:**
```json
{
  "values": [
    {
      "standard_parameter_id": "uuid",
      "value_numeric": 280.0,
      "value_range_min": null,
      "value_range_max": null,
      "value_text": null,
      "value_boolean": null,
      "value_enum": null,
      "notes": "string (optional)",
      "source": "manual|ai_extracted|imported"
    }
  ]
}
```

Only the value field matching `data_type` should be non-null. Backend validates this.

**Response 200:**
```json
{ "updated": 28, "created": 0, "validation_errors": [] }
```

`validation_errors` array contains any parameters that failed validation rules — they are skipped, not rejected wholesale.

### `PATCH /component-models/{model_id}/parameters/{param_id}`
Roles: `admin`, `engineer`

Single parameter value update.

---

## 8. Projects

### `GET /projects`
Roles: all (customers see only their assigned project)

**Query params:** `?status=active&project_type=utility&search=barh`

**Response 200 — `data` array:**
```json
[
  {
    "id": "uuid",
    "project_code": "PRJ-2025-001",
    "name": "NTPC Barh BESS",
    "client_name": "NGSL",
    "project_type": "utility",
    "capacity_mw": 200.0,
    "energy_mwh": 400.0,
    "location": "Barh, Bihar",
    "status": "active",
    "current_stage": "technical_lead",
    "sheet_count": 12,
    "locked_sheet_count": 1,
    "created_at": "2025-09-01T00:00:00Z"
  }
]
```

`project_type` enum: `utility`, `ci`, `btm`, `hybrid`
`status` enum: `pipeline`, `active`, `on_hold`, `completed`, `cancelled`

### `POST /projects`
Roles: `admin`, `commercial`

**Request body:**
```json
{
  "name": "string (required)",
  "client_name": "string (required)",
  "project_type": "utility|ci|btm|hybrid (required)",
  "capacity_mw": "float (optional)",
  "energy_mwh": "float (optional)",
  "location": "string (optional)",
  "notes": "string (optional)"
}
```

**Response 201:** Full project object.

### `GET /projects/{project_id}`
Roles: all (customers scoped)

**Response 200:** Project object + `sheets` summary array + `team_members` array.

### `PATCH /projects/{project_id}`
Roles: `admin`, `commercial`

### `POST /projects/{project_id}/members`
Roles: `admin`

Assign a user to a project. Required for customer users — they cannot see a project unless explicitly assigned.

**Request body:**
```json
{ "user_id": "uuid", "role": "engineer|reviewer|commercial|customer" }
```

---

## 9. Compliance Templates

### `GET /compliance-templates`
Roles: all

**Query params:** `?component_type_id=uuid`

**Response 200 — `data` array:**
```json
[
  {
    "id": "uuid",
    "name": "Battery Cell LFP — Standard",
    "component_type_id": "uuid",
    "component_type_name": "Battery Cell",
    "version": "1.2",
    "is_default": true,
    "parameter_count": 24,
    "created_at": "2025-07-01T00:00:00Z"
  }
]
```

### `GET /compliance-templates/{template_id}`
Roles: all

**Response 200:** Template object + `parameters` array — each item includes the standard parameter definition plus `acceptance_criteria` and `is_mandatory_in_template` (may differ from base standard parameter).

```json
{
  "id": "uuid",
  "name": "Battery Cell LFP — Standard",
  "parameters": [
    {
      "standard_parameter_id": "uuid",
      "code": "CELL_CAPACITY_AH",
      "display_name": "Nominal Capacity",
      "acceptance_criteria": "≥ 260 Ah",
      "is_mandatory_in_template": true,
      "sort_order": 1
    }
  ]
}
```

### `POST /compliance-templates`
Roles: `admin`

**Request body:**
```json
{
  "name": "string (required)",
  "component_type_id": "uuid (required)",
  "is_default": "boolean (default: false)",
  "parameters": [
    {
      "standard_parameter_id": "uuid",
      "acceptance_criteria": "string (optional)",
      "is_mandatory_in_template": "boolean",
      "sort_order": "integer"
    }
  ]
}
```

---

## 10. Technical Sheets

### `GET /projects/{project_id}/sheets`
Roles: all (customers see only sheets at stage ≥ `customer_submission`)

**Response 200 — `data` array:**
```json
[
  {
    "id": "uuid",
    "sheet_number": "TCS-047",
    "title": "Battery Cell — CATL 280Ah LFP",
    "project_id": "uuid",
    "component_model_id": "uuid",
    "component_model_name": "CATL-LFP-280AH-3.2V",
    "template_id": "uuid",
    "workflow_stage": "technical_lead",
    "compliance_score": 94.5,
    "compliance_status": "partial",
    "revision": "r2",
    "is_locked": false,
    "lock_hash": null,
    "created_by": "uuid",
    "created_at": "2026-01-10T00:00:00Z",
    "updated_at": "2026-02-14T00:00:00Z"
  }
]
```

`workflow_stage` enum: `draft`, `engineering_review`, `technical_lead`, `management`, `customer_submission`, `customer_signoff`, `locked`

`compliance_status` enum: `pending`, `partial`, `compliant`, `non_compliant`

### `POST /projects/{project_id}/sheets`
Roles: `admin`, `engineer`

Creates a new compliance sheet and auto-triggers compliance evaluation against the template.

**Request body:**
```json
{
  "title": "string (required)",
  "component_model_id": "uuid (required)",
  "template_id": "uuid (required)",
  "notes": "string (optional)"
}
```

**Response 201:** Full sheet object.  
**Side effects:** 
- Creates `approval_workflow` record (stage: `draft`)
- Runs compliance evaluation → creates `sheet_compliance_results` rows
- Writes audit log entry

### `GET /projects/{project_id}/sheets/{sheet_id}`
Roles: all (customers scoped)

**Response 200:** Full sheet object +
- `compliance_results` array (per-parameter pass/fail/waived)
- `workflow` object (current stage, history summary)
- `model` summary (OEM name, model name)
- `versions` array (revision history — id, revision label, created_at, created_by)

**Full compliance_results item:**
```json
{
  "id": "uuid",
  "standard_parameter_id": "uuid",
  "code": "CELL_CAPACITY_AH",
  "display_name": "Nominal Capacity",
  "unit": "Ah",
  "oem_value_numeric": 280.0,
  "acceptance_criteria": "≥ 260 Ah",
  "compliance_status": "pass",
  "waiver_reason": null,
  "evaluated_at": "2026-01-10T10:00:00Z"
}
```

`compliance_status` per result: `pass`, `fail`, `waived`, `not_evaluated`

### `PATCH /projects/{project_id}/sheets/{sheet_id}`
Roles: `admin`, `engineer` — only when stage = `draft`  
Returns `423 SHEET_LOCKED` if `is_locked = true`.

**Request body:**
```json
{
  "title": "string (optional)",
  "notes": "string (optional)"
}
```

Metadata only. Parameter values are updated via the component model endpoint.

### `POST /projects/{project_id}/sheets/{sheet_id}/evaluate`
Roles: `admin`, `engineer`

Re-runs compliance evaluation against current parameter values. Call this after editing parameter values.

**Response 200:**
```json
{
  "compliance_score": 96.5,
  "compliance_status": "compliant",
  "pass_count": 26,
  "fail_count": 1,
  "waived_count": 1,
  "not_evaluated_count": 0
}
```

### `POST /projects/{project_id}/sheets/{sheet_id}/waive`
Roles: `reviewer`, `admin`

Waive a failing parameter result with a mandatory reason.

**Request body:**
```json
{
  "standard_parameter_id": "uuid",
  "waiver_reason": "string (required, min 20 chars)"
}
```

**Response 200:** Updated compliance result.

---

## 11. Workflow

### `GET /projects/{project_id}/sheets/{sheet_id}/workflow`
Roles: all

**Response 200:**
```json
{
  "id": "uuid",
  "workflow_ref": "WF-091",
  "sheet_id": "uuid",
  "current_stage": "technical_lead",
  "started_at": "2026-01-10T00:00:00Z",
  "steps": [
    {
      "id": "uuid",
      "stage_from": "draft",
      "stage_to": "engineering_review",
      "action": "approve",
      "actor_id": "uuid",
      "actor_name": "Anushtha K.",
      "actor_role": "engineer",
      "comment": "Parameters verified against datasheet v3.1",
      "digital_signature": "base64string (optional)",
      "ip_address": "10.0.1.42",
      "created_at": "2026-01-12T09:15:00Z"
    }
  ]
}
```

`action` enum: `approve`, `reject`, `submit`, `sign`, `lock`

### `POST /projects/{project_id}/sheets/{sheet_id}/workflow/advance`
Roles: see Role × Stage Matrix in workflow-spec.md  
This is the **primary workflow action endpoint**.

**Request body:**
```json
{
  "action": "approve|reject|submit|sign|lock (required)",
  "comment": "string (required when action=reject, min 20 chars; optional otherwise)",
  "digital_signature": "string (base64, optional)"
}
```

**Response 200:**
```json
{
  "workflow_ref": "WF-091",
  "previous_stage": "engineering_review",
  "current_stage": "technical_lead",
  "action_taken": "approve",
  "step_id": "uuid",
  "sheet_number": "TCS-047",
  "snapshot_saved": true
}
```

**What happens internally (advance_workflow() stored procedure):**
1. Validate transition is permitted (stage + role check)
2. For `reject`: reset `workflow_stage` on sheet to `draft`, increment revision suffix
3. For `lock`: set `is_locked = true`, compute and store `lock_hash`, call `create_sheet_version()`
4. Insert row into `workflow_steps` (immutable from this point)
5. Insert row into `audit_logs`
6. Update `approval_workflows.current_stage`
7. Update `technical_sheets.workflow_stage` and `updated_at`
8. Return result

**Error cases:**
- `403 INSUFFICIENT_ROLE` — user's role cannot take this action at this stage
- `422 INVALID_TRANSITION` — action not valid for current stage (e.g., trying to lock at draft)
- `422 COMPLIANCE_INCOMPLETE` — cannot advance past `engineering_review` if mandatory parameters are failing (unless waived)
- `423 SHEET_LOCKED` — sheet is already at stage `locked`

### `GET /workflow/pending`
Roles: all — returns only items pending the current user's action

**Response 200 — `data` array:**
```json
[
  {
    "sheet_id": "uuid",
    "sheet_number": "TCS-047",
    "sheet_title": "Battery Cell — CATL 280Ah",
    "project_name": "NTPC Barh",
    "workflow_stage": "technical_lead",
    "waiting_since": "2026-02-10T00:00:00Z",
    "waiting_hours": 72,
    "compliance_score": 94.5
  }
]
```

### `GET /workflow/activity`
Roles: `admin`, `reviewer`, `commercial`

Last 50 workflow actions across all sheets. Used for the activity feed on the dashboard Overview module.

---

## 12. Comparison

### `POST /comparison`
Roles: all

Create a new comparison set.

**Request body:**
```json
{
  "name": "string (required)",
  "project_id": "uuid (optional — link to project)",
  "component_type_id": "uuid (required)",
  "model_ids": ["uuid", "uuid", "uuid"],
  "parameter_ids": ["uuid", "uuid"] 
}
```
If `parameter_ids` is empty, all standard parameters for the component type are included.

**Response 201:**
```json
{ "id": "uuid", "name": "string", "component_type_id": "uuid" }
```

### `GET /comparison/{comparison_id}/matrix`
Roles: all

Primary data endpoint for the comparison UI.

**Response 200:**
```json
{
  "id": "uuid",
  "name": "Lishen vs CATL vs HiTHIUM",
  "component_type": "Battery Cell",
  "models": [
    { "id": "uuid", "oem_name": "Lishen", "model_name": "LR1865SK", "compliance_score": 91.2 },
    { "id": "uuid", "oem_name": "CATL", "model_name": "CATL-LFP-280AH", "compliance_score": 97.5 },
    { "id": "uuid", "oem_name": "HiTHIUM", "model_name": "HTL-LFP-280K", "compliance_score": 87.4 }
  ],
  "parameters": [
    {
      "code": "CELL_CAPACITY_AH",
      "display_name": "Nominal Capacity",
      "unit": "Ah",
      "is_mandatory": true,
      "values": [
        { "model_id": "uuid", "value_numeric": 271.0, "display_value": "271 Ah" },
        { "model_id": "uuid", "value_numeric": 280.0, "display_value": "280 Ah" },
        { "model_id": "uuid", "value_numeric": 280.0, "display_value": "280 Ah" }
      ]
    }
  ]
}
```

### `GET /comparison` 
Roles: all

List saved comparison sets. Query: `?project_id=uuid`

---

## 13. Documents

### `POST /documents/generate`
Roles: `admin`, `engineer`, `reviewer`, `commercial`

Triggers async document generation. Returns immediately with a `task_id`.

**Request body:**
```json
{
  "document_type": "compliance_sheet|comparison_report|customer_package|audit_report|version_diff (required)",
  "format": "pdf|xlsx|pptx (required)",
  "entity_id": "uuid (required — sheet_id, comparison_id, or project_id depending on type)",
  "options": {
    "include_signatures": true,
    "include_audit_trail": false,
    "version_a": "uuid (for version_diff only)",
    "version_b": "uuid (for version_diff only)"
  }
}
```

**Response 202:**
```json
{
  "task_id": "celery-task-uuid",
  "document_id": "uuid",
  "status": "queued",
  "estimated_seconds": 15
}
```

### `GET /documents/{document_id}/status`
Roles: all

Poll for generation status.

**Response 200:**
```json
{
  "document_id": "uuid",
  "task_id": "celery-task-uuid",
  "status": "queued|processing|ready|failed",
  "progress_pct": 60,
  "download_url": "https://minio.../signed-url (only when status=ready)",
  "url_expires_at": "2026-03-13T12:00:00Z",
  "file_size_bytes": 245780,
  "sha256_checksum": "abc123...",
  "error_message": null
}
```

Frontend should poll every 2 seconds. `download_url` is a MinIO signed URL valid for 24 hours.

### `GET /documents`
Roles: all

List recently generated documents for the current user.

**Query params:** `?entity_id=uuid&document_type=compliance_sheet&format=pdf`

---

## 14. AI Extraction

### `POST /ai/extract`
Roles: `admin`, `engineer`

Rate limit: 10 requests/min.

Accepts a PDF datasheet upload. Starts async Celery task. Returns immediately.

**Request:** `multipart/form-data`
```
file: <PDF binary> (required, max 20 MB)
oem_id: uuid (required)
component_type_id: uuid (required)
model_name: string (required — used to create component model if it doesn't exist)
```

**Response 202:**
```json
{
  "task_id": "celery-task-uuid",
  "extraction_id": "uuid",
  "status": "queued",
  "model_id": "uuid (newly created or existing if model_name matched)"
}
```

### `GET /ai/extract/{extraction_id}/status`
Roles: `admin`, `engineer`

Poll for extraction status. Frontend polls every 3 seconds.

**Response 200:**
```json
{
  "extraction_id": "uuid",
  "status": "queued|processing|complete|failed",
  "model_id": "uuid",
  "parameters_extracted": 24,
  "parameters_total": 28,
  "low_confidence_count": 3,
  "results": [
    {
      "standard_parameter_id": "uuid",
      "code": "CELL_CAPACITY_AH",
      "display_name": "Nominal Capacity",
      "extracted_value": 280.0,
      "display_value": "280 Ah",
      "confidence_score": 0.97,
      "confidence_label": "high",
      "needs_review": false,
      "source_text": "Nominal capacity: 280 Ah at 0.2C"
    }
  ],
  "error_message": null
}
```

`confidence_label`:
- `high`: ≥ 0.90
- `medium`: 0.80–0.89 — flagged for review
- `low`: < 0.80 — must be manually entered

### `POST /ai/extract/{extraction_id}/confirm`
Roles: `admin`, `engineer`

After engineer reviews the extraction results, confirm to write them to `parameter_values`.

**Request body:**
```json
{
  "confirmed_values": [
    {
      "standard_parameter_id": "uuid",
      "accept": true,
      "override_value_numeric": null
    },
    {
      "standard_parameter_id": "uuid",
      "accept": false,
      "override_value_numeric": 285.0
    }
  ]
}
```

**Response 200:**
```json
{ "written": 24, "overridden": 1, "skipped": 3 }
```

---

## 15. Audit

### `GET /audit`
Roles: `admin` only

**Query params:** `?entity_type=technical_sheet&entity_id=uuid&actor_id=uuid&from=2026-01-01&to=2026-03-01`

**Response 200 — `data` array:**
```json
[
  {
    "id": "uuid",
    "entity_type": "technical_sheet",
    "entity_id": "uuid",
    "action": "workflow_advance",
    "actor_id": "uuid",
    "actor_name": "Anushtha K.",
    "actor_role": "engineer",
    "old_values": { "workflow_stage": "draft" },
    "new_values": { "workflow_stage": "engineering_review" },
    "ip_address": "10.0.1.42",
    "session_id": "uuid",
    "created_at": "2026-01-12T09:15:00Z"
  }
]
```

`entity_type` enum: `oem`, `component_model`, `parameter_value`, `technical_sheet`, `compliance_result`, `approval_workflow`

### `GET /audit/sheet/{sheet_id}`
Roles: `admin`, `reviewer`, `commercial` — complete audit trail for one sheet, ordered chronologically.

---

## 16. Users

### `GET /users/me`
Roles: all

**Response 200:**
```json
{
  "id": "uuid",
  "keycloak_sub": "uuid",
  "username": "kedar.bala",
  "email": "kedar@ornateagencies.com",
  "full_name": "Kedar Bala",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-06-01T00:00:00Z"
}
```

### `GET /users`
Roles: `admin` only

Lists all users in the system (synced from Keycloak on first login).

### `PATCH /users/{user_id}`
Roles: `admin` only

**Request body:**
```json
{ "is_active": false, "full_name": "string" }
```
Role changes must be done in Keycloak — not via this endpoint.

---

## Frontend → API Mapping

| Portal Module | Primary Endpoints Called |
|---|---|
| Overview | `GET /workflow/pending`, `GET /workflow/activity`, `GET /projects` |
| OEM Library | `GET /oems`, `GET /oems/{id}`, `GET /component-models?oem_id=` |
| Components | `GET /component-models/{id}`, `GET /component-models/{id}/parameters`, `PUT /component-models/{id}/parameters` |
| Compliance Builder | `GET /compliance-templates`, `POST /projects/{id}/sheets`, `POST /projects/{id}/sheets/{id}/evaluate` |
| Approval Workflow | `GET /workflow/pending`, `GET /projects/{id}/sheets/{id}/workflow`, `POST /projects/{id}/sheets/{id}/workflow/advance` |
| Compare | `POST /comparison`, `GET /comparison/{id}/matrix` |
| Projects | `GET /projects`, `GET /projects/{id}` |
| Export Centre | `POST /documents/generate`, `GET /documents/{id}/status`, `GET /documents` |
| AI Upload | `POST /ai/extract`, `GET /ai/extract/{id}/status`, `POST /ai/extract/{id}/confirm` |
| Customer Portal | `GET /projects/{id}/sheets` (stage-scoped), `GET /projects/{id}/sheets/{id}`, `POST /projects/{id}/sheets/{id}/workflow/advance` (sign action only) |

---

## Celery Task Names

| Task | Module | Triggered By |
|---|---|---|
| `tasks.doc_tasks.generate_document` | doc_tasks.py | `POST /documents/generate` |
| `tasks.ai_tasks.extract_parameters` | ai_tasks.py | `POST /ai/extract` |
| `tasks.notification_tasks.send_workflow_notification` | notification_tasks.py | After every `workflow/advance` |
| `tasks.notification_tasks.send_document_ready` | notification_tasks.py | After doc generation completes |
| `tasks.doc_tasks.audit_snapshot` | doc_tasks.py | Celery beat — daily at 02:00 IST |

---

*End of api-spec.md — UnityESS Technical Compliance Portal v2.1*
