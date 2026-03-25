# Workflow State Machine Specification — UnityESS Technical Compliance Portal
> For Cowork / developer handover. Formal state machine, stored procedure contracts, RBAC enforcement, and edge cases.  
> Version: 2.1 · March 2026

---

## 1. States

The `workflow_stage` column on `technical_sheets` (and `approval_workflows.current_stage`) uses this PostgreSQL enum:

```sql
CREATE TYPE workflow_stage AS ENUM (
  'draft',
  'engineering_review',
  'technical_lead',
  'management',
  'customer_submission',
  'customer_signoff',
  'locked'
);
```

### State Definitions

| State | DB Value | Description | Sheet Editable? | Customer Visible? |
|---|---|---|---|---|
| Draft | `draft` | Initial state. Engineer builds and maps parameters. | ✓ Yes | No |
| Engineering Review | `engineering_review` | Senior engineer verifies parameter accuracy. | No | No |
| Technical Lead Approval | `technical_lead` | Tech lead validates regulatory compliance and signs. | No | No |
| Management Approval | `management` | Commercial/management alignment check and sign. | No | No |
| Customer Submission | `customer_submission` | Package delivered to customer. Customer portal unlocked. | No | ✓ Read-only |
| Customer Sign-off | `customer_signoff` | Customer reviewing. Lock imminent. | No | ✓ Read-only |
| Locked | `locked` | Permanent. SHA-256 hashed. No further writes at DB level. | No (trigger) | ✓ Read-only |

---

## 2. Valid Transitions Table

Every row in this table is a permitted state machine transition.  
Any combination NOT listed here must return `422 INVALID_TRANSITION`.

| From Stage | Action | To Stage | Permitted Roles | Compliance Check Required? |
|---|---|---|---|---|
| `draft` | `submit` | `engineering_review` | `engineer`, `admin` | ✓ All mandatory params must have values |
| `engineering_review` | `approve` | `technical_lead` | `reviewer`, `admin` | ✓ No mandatory params in `fail` status (waived OK) |
| `engineering_review` | `reject` | `draft` | `reviewer`, `admin` | No |
| `technical_lead` | `approve` | `management` | `reviewer`, `admin` | No |
| `technical_lead` | `reject` | `draft` | `reviewer`, `admin` | No |
| `management` | `approve` | `customer_submission` | `commercial`, `admin` | No |
| `management` | `reject` | `draft` | `commercial`, `admin` | No |
| `customer_submission` | `submit` | `customer_signoff` | `commercial`, `admin` | No |
| `customer_signoff` | `sign` | `locked` | `customer`, `admin` | No |
| `locked` | — | — | None | Sheet is permanently locked. No transitions. |

### Rejection Behaviour (special case)

When `action = reject` and transition is to `draft`:
1. `workflow_stage` on `technical_sheets` resets to `draft`
2. `revision` field increments: `r1` → `r2` → `r3` (string suffix, not integer)
3. Comment is **mandatory** (API enforces min 20 chars)
4. A `workflow_steps` row is inserted with `action = 'reject'` and `stage_to = 'draft'`
5. Sheet becomes editable again — engineer can update parameters and re-submit

Revision label format: `r{n}` for working revisions. Becomes `v1.0` on first lock, `v1.1` on second lock (if unlocked by admin — rare).

---

## 3. Compliance Gate Rules

These rules are enforced inside `advance_workflow()` **before** the transition is written.

### Gate: `draft` → `engineering_review`
```
All mandatory standard parameters in the template MUST have a non-null value.
If any mandatory parameter_value is NULL → raise COMPLIANCE_INCOMPLETE
  error detail: { "missing_params": ["CELL_CAPACITY_AH", ...] }
```

### Gate: `engineering_review` → `technical_lead`
```
No mandatory parameter may have compliance_status = 'fail'.
Waived parameters (compliance_status = 'waived') ARE acceptable — they need a waiver_reason.
If any mandatory parameter has status 'fail' → raise COMPLIANCE_GATE_FAIL
  error detail: { "failing_params": ["CELL_ENERGY_KWH", ...] }
```

### All other transitions: No compliance gate.

---

## 4. Stored Procedure: `advance_workflow()`

This is the **single entry point** for all workflow transitions. The FastAPI workflow endpoint calls this procedure. It is an atomic transaction — all steps succeed or all roll back.

### Signature
```sql
CREATE OR REPLACE FUNCTION advance_workflow(
  p_sheet_id        UUID,
  p_action          approval_action,    -- 'approve','reject','submit','sign','lock'
  p_actor_id        UUID,
  p_actor_role      user_role,
  p_comment         TEXT DEFAULT NULL,
  p_digital_sig     TEXT DEFAULT NULL,
  p_ip_address      INET DEFAULT NULL,
  p_session_id      UUID DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
```

### Return Value (JSONB)
```json
{
  "success": true,
  "workflow_ref": "WF-091",
  "step_id": "uuid",
  "previous_stage": "engineering_review",
  "current_stage": "technical_lead",
  "action": "approve",
  "revision": "r2",
  "snapshot_saved": false,
  "locked": false
}
```

On error:
```json
{
  "success": false,
  "error_code": "INSUFFICIENT_ROLE",
  "error_message": "Role 'engineer' cannot approve at stage 'engineering_review'",
  "detail": {}
}
```

The FastAPI layer translates `success: false` + `error_code` into the appropriate HTTP error response.

### Internal Execution Order

```
BEGIN TRANSACTION

1. SELECT technical_sheet FOR UPDATE  (lock row for duration of transaction)

2. Validate sheet exists and is not locked
   → IF is_locked = true: return error SHEET_LOCKED

3. Look up current workflow stage from approval_workflows

4. Validate transition:
   a. Look up (current_stage, action) in valid_transitions
   → IF not found: return error INVALID_TRANSITION
   b. Check actor_role is in permitted_roles for this transition
   → IF not permitted: return error INSUFFICIENT_ROLE

5. Run compliance gate (if applicable — see Section 3)

6. Compute new stage (stage_to from valid_transitions table)

7. IF action = 'reject':
   a. Compute new_revision = increment_revision(current_revision)
   b. SET technical_sheets.revision = new_revision
   c. SET technical_sheets.workflow_stage = 'draft'

8. IF action = 'lock' OR new_stage = 'locked':
   a. Compute lock_hash = sha256(canonical_jsonb_snapshot(sheet_id))
   b. SET technical_sheets.is_locked = true
   c. SET technical_sheets.locked_at = NOW()
   d. SET technical_sheets.lock_hash = lock_hash
   e. CALL create_sheet_version(sheet_id, 'v1.0', lock_hash)

9. INSERT INTO workflow_steps (immutable from this point):
   (workflow_id, stage_from, stage_to, action, actor_id, actor_role,
    comment, digital_signature, ip_address, session_id, created_at)

10. UPDATE approval_workflows SET current_stage = new_stage, updated_at = NOW()

11. UPDATE technical_sheets SET workflow_stage = new_stage, updated_at = NOW()

12. INSERT INTO audit_logs (append-only):
    (entity_type='technical_sheet', entity_id=sheet_id, action='workflow_advance',
     actor_id, actor_role, old_values={stage: old}, new_values={stage: new},
     ip_address, session_id, created_at)

13. IF NOT (action = 'reject' OR action = 'lock'):
    CALL create_sheet_version(sheet_id, current_revision, NULL)
    -- saves snapshot at each forward stage

COMMIT TRANSACTION

14. Return success JSONB
```

### `create_sheet_version()` Procedure

Called at every forward transition and on lock.

```sql
CREATE OR REPLACE FUNCTION create_sheet_version(
  p_sheet_id    UUID,
  p_version_label TEXT,   -- 'r1', 'r2', 'v1.0'
  p_lock_hash   TEXT DEFAULT NULL
)
RETURNS UUID  -- returns new version record id
```

What it stores in `sheet_versions`:
```sql
INSERT INTO sheet_versions (
  sheet_id,
  version_label,
  snapshot_data,    -- JSONB: full sheet + model + OEM + compliance_results
  lock_hash,        -- only non-null on locked versions
  created_by,       -- taken from current_setting('app.user_id')
  created_at
)
```

The `snapshot_data` JSONB structure:
```json
{
  "sheet": { "id": "...", "title": "...", "workflow_stage": "...", ... },
  "model": { "id": "...", "model_name": "...", "oem_name": "...", ... },
  "parameters": [ { "code": "...", "value_numeric": ..., "compliance_status": "...", ... } ],
  "compliance_summary": { "score": 94.5, "pass": 26, "fail": 1, "waived": 1 }
}
```

---

## 5. Stored Procedure: `compute_lock_hash()`

Called by `advance_workflow()` when `action = 'lock'`.

```sql
CREATE OR REPLACE FUNCTION compute_lock_hash(p_sheet_id UUID)
RETURNS TEXT  -- hex SHA-256 string
```

Canonical input to hash (deterministic — must produce same hash for same data):
```sql
SELECT encode(
  digest(
    jsonb_build_object(
      'sheet_id',     s.id::text,
      'sheet_number', s.sheet_number,
      'title',        s.title,
      'model_id',     s.component_model_id::text,
      'revision',     s.revision,
      'parameters',   (
        SELECT jsonb_agg(
          jsonb_build_object(
            'code', sp.code,
            'value_numeric', pv.value_numeric,
            'value_range_min', pv.value_range_min,
            'value_range_max', pv.value_range_max,
            'value_text', pv.value_text,
            'value_boolean', pv.value_boolean,
            'value_enum', pv.value_enum,
            'compliance_status', scr.compliance_status
          )
          ORDER BY sp.sort_order
        )
        FROM parameter_values pv
        JOIN standard_parameters sp ON sp.id = pv.standard_parameter_id
        LEFT JOIN sheet_compliance_results scr
          ON scr.sheet_id = s.id AND scr.standard_parameter_id = sp.id
        WHERE pv.component_model_id = s.component_model_id
      )
    )::text,
    'sha256'
  ),
  'hex'
)
FROM technical_sheets s WHERE s.id = p_sheet_id;
```

---

## 6. DB Triggers (All 8)

### Trigger 1: `trg_sheet_immutability`
```sql
-- ON UPDATE OR DELETE ON technical_sheets
-- BEFORE each row operation
IF OLD.is_locked = true THEN
  RAISE EXCEPTION 'Sheet % is locked and cannot be modified.', OLD.sheet_number
    USING ERRCODE = 'P0001';
END IF;
```

### Trigger 2: `trg_wf_step_immutability`
```sql
-- ON UPDATE OR DELETE ON workflow_steps
-- BEFORE each row operation
RAISE EXCEPTION 'Workflow steps are immutable and cannot be modified.'
  USING ERRCODE = 'P0002';
```

### Trigger 3: `trg_audit_immutability`
```sql
-- ON UPDATE OR DELETE ON audit_logs
-- BEFORE each row operation
RAISE EXCEPTION 'Audit log records are immutable.'
  USING ERRCODE = 'P0003';
```

### Trigger 4: `trg_sheet_number`
```sql
-- ON INSERT ON technical_sheets BEFORE
-- Assigns TCS-001, TCS-002, etc.
NEW.sheet_number := 'TCS-' || LPAD(nextval('sheet_number_seq')::text, 3, '0');
```

### Trigger 5: `trg_workflow_ref`
```sql
-- ON INSERT ON approval_workflows BEFORE
NEW.workflow_ref := 'WF-' || LPAD(nextval('workflow_ref_seq')::text, 3, '0');
```

### Trigger 6: `trg_parameter_count`
```sql
-- ON INSERT OR DELETE ON standard_parameters AFTER
UPDATE component_types
SET parameter_count = (
  SELECT COUNT(*) FROM standard_parameters WHERE component_type_id = NEW.component_type_id
)
WHERE id = NEW.component_type_id;
```

### Trigger 7: `trg_updated_at_sheets`
```sql
-- ON UPDATE ON technical_sheets BEFORE
NEW.updated_at := NOW();
```

### Trigger 8: `trg_updated_at_models`
```sql
-- ON UPDATE ON component_models BEFORE
NEW.updated_at := NOW();
```

---

## 7. PostgreSQL Row-Level Security (RLS)

RLS is enabled on `technical_sheets` only. All other tables rely on API-layer RBAC.

```sql
ALTER TABLE technical_sheets ENABLE ROW LEVEL SECURITY;
```

### Policy: Internal Users (all non-customer roles)
```sql
CREATE POLICY internal_user_policy ON technical_sheets
  USING (
    current_setting('app.user_role') IN ('admin','engineer','reviewer','commercial')
  );
```

### Policy: Customer Users
```sql
CREATE POLICY customer_policy ON technical_sheets
  USING (
    current_setting('app.user_role') = 'customer'
    AND workflow_stage IN ('customer_submission','customer_signoff','locked')
    AND project_id IN (
      SELECT project_id FROM project_members
      WHERE user_id = current_setting('app.user_id')::uuid
    )
  );
```

### Setting Session Variables (FastAPI middleware)
Before every DB query, the middleware executes:
```sql
SET LOCAL app.user_id = '<uuid>';
SET LOCAL app.user_role = '<role>';
```

This is done within the same transaction context using SQLAlchemy's `event.listen(engine, 'connect', ...)` or per-request using `await session.execute(text("SET LOCAL app.user_id = :uid"), {"uid": user_id})`.

---

## 8. RBAC Middleware (FastAPI)

### Dependency: `require_role(*allowed_roles)`
```python
def require_role(*roles):
    def dependency(token_data: TokenData = Depends(verify_jwt)):
        if token_data.role not in roles:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "INSUFFICIENT_ROLE",
                    "message": f"Role '{token_data.role}' cannot access this endpoint."
                }
            )
        return token_data
    return dependency
```

Usage on route:
```python
@router.post("/workflow/advance")
async def advance_workflow(
    ...,
    current_user: TokenData = Depends(require_role("admin","engineer","reviewer","commercial","customer"))
):
    # Role is valid. The stored procedure handles per-transition role enforcement.
```

Most endpoints accept all authenticated roles at the route level, then let the stored procedure enforce which role can take which action. This avoids duplicating the role-transition matrix in Python.

Exception: endpoints that are admin-only (`DELETE /oems`, `POST /standard-parameters`, etc.) use `require_role("admin")` at the route level.

---

## 9. Notification Events

After every successful `advance_workflow()` call, a Celery task is dispatched:

```python
send_workflow_notification.delay(
    step_id=step_id,
    sheet_id=sheet_id,
    action=action,
    from_stage=previous_stage,
    to_stage=current_stage,
    actor_name=actor_name
)
```

### Notification Matrix

| Transition | Notify Who | Channel | Template |
|---|---|---|---|
| `draft` → `engineering_review` | All reviewers | Email + In-app | `workflow_pending_review` |
| `engineering_review` → `technical_lead` | Tech leads | Email + In-app | `workflow_pending_approval` |
| `technical_lead` → `management` | Commercial team | Email + In-app | `workflow_pending_mgmt` |
| `management` → `customer_submission` | Commercial + Customer contact | Email | `workflow_submitted_customer` |
| `customer_submission` → `customer_signoff` | Engineers + Reviewers | In-app | `workflow_customer_reviewing` |
| `customer_signoff` → `locked` | All project members | Email + In-app | `workflow_locked` |
| Any → `draft` (reject) | Sheet creator (engineer) | Email + In-app | `workflow_rejected` |

Email templates are Jinja2 HTML in `app/templates/email/`.  
In-app notifications are stored in a `notifications` table (not in main schema — simple append-only table, no immutability trigger needed).

### 48-Hour Escalation
Celery beat runs `check_stale_workflows` daily at 02:00 IST.  
Any sheet stuck at the same stage for > 48 hours generates a WhatsApp message to Kedar Bala (roadmap item — Q2 2026, not yet implemented).

---

## 10. Edge Cases & Rules

### 10.1 Admin Override
`admin` role can perform any action at any stage. This is enforced in the stored procedure's role check — if `p_actor_role = 'admin'`, skip the role whitelist check and proceed directly to compliance gate.

### 10.2 Re-locking After Admin Unlock
Admin can set `is_locked = false` directly (bypassing normal workflow) to correct a locked sheet. This is a raw SQL operation — not exposed via API. If this happens:
- A new workflow step is inserted with `action = 'admin_unlock'`
- Revision becomes `v1.1` on next lock
- `lock_hash` is re-computed

### 10.3 Concurrent Advance Attempts
The `SELECT ... FOR UPDATE` in `advance_workflow()` prevents race conditions. If two users try to advance the same sheet simultaneously, one will block and then fail with `INVALID_TRANSITION` (since the first one already changed the stage).

### 10.4 Customer Signs Wrong Sheet
Customer can only call `advance_workflow()` on sheets at `customer_signoff` stage in their assigned project. The RLS policy on `technical_sheets` prevents them from querying sheets outside their project. The stored procedure additionally checks `p_actor_role = 'customer'` is only valid for the `sign` action.

### 10.5 AI-Extracted Sheet → Workflow
When a sheet is created from AI extraction (`POST /ai/extract/{id}/confirm`), the system:
1. Calls `PUT /component-models/{id}/parameters` to write confirmed values
2. Auto-creates a `technical_sheet` with `revision = 'r1'` and `workflow_stage = 'draft'`
3. Auto-runs compliance evaluation (`POST /sheets/{id}/evaluate`)
4. Engineer then reviews and submits manually — AI extraction does NOT auto-advance to `engineering_review`

### 10.6 Template Change After Sheet Created
Template parameters can be added after a sheet is created. If a new mandatory parameter is added to a template, existing sheets in `draft` or `engineering_review` will fail the compliance gate on next advance attempt. The engineer must fill the new parameter value before re-submitting.

### 10.7 Compliance Evaluation on Model Change
If an engineer changes a parameter value for a component model (e.g., via `PUT /component-models/{id}/parameters`), the compliance results on ALL sheets using that model are **not** automatically re-evaluated. The engineer must explicitly call `POST /sheets/{id}/evaluate` to refresh. This is intentional — avoids silent changes to sheets under review.

---

## 11. `approval_action` Enum → HTTP Action Map

```sql
CREATE TYPE approval_action AS ENUM (
  'approve',   -- forward, reviewer/tech-lead/management
  'reject',    -- backward to draft
  'submit',    -- draft→review, management→customer_submission
  'sign',      -- customer_signoff→locked (customer digital sign)
  'lock'       -- alias for 'sign' used internally by advance_workflow
);
```

The API accepts `action` as a string. The stored procedure maps:
- `submit` = used by engineer (draft→review) and commercial (management→customer_submission)
- `approve` = used by reviewer and tech lead
- `sign` = used by customer (customer_signoff→locked)

Do not expose `lock` as an API action — it is only used internally by the procedure when processing `sign`.

---

## 12. Revision Label Logic

```python
def increment_revision(current: str) -> str:
    """
    'r1' → 'r2'
    'r9' → 'r10'
    'v1.0' → should not be called on locked sheets (raises error)
    """
    if current.startswith('v'):
        raise ValueError("Cannot increment a locked revision label")
    n = int(current[1:])
    return f"r{n + 1}"

def revision_on_lock(current: str) -> str:
    """
    First lock: any 'r*' → 'v1.0'
    Admin re-lock: 'v1.0' → 'v1.1', 'v1.1' → 'v1.2'
    """
    if current.startswith('r'):
        return 'v1.0'
    parts = current[1:].split('.')
    return f"v{parts[0]}.{int(parts[1]) + 1}"
```

---

*End of workflow-spec.md — UnityESS Technical Compliance Portal v2.1*
