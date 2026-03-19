-- =============================================================================
-- UnityESS Technical Compliance Portal — PostgreSQL 16 Schema
-- Ornate Agencies Pvt. Ltd.
-- Compatible with: Neon Postgres (serverless), AWS RDS PostgreSQL 16
-- Run this file once on a fresh database. Idempotent via IF NOT EXISTS.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 0. EXTENSIONS
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";    -- for SHA-256 lock_hash
CREATE EXTENSION IF NOT EXISTS "pg_trgm";     -- for trigram full-text search on component names

-- ---------------------------------------------------------------------------
-- 1. ENUMS
-- ---------------------------------------------------------------------------

CREATE TYPE component_category AS ENUM (
    'battery_cell',
    'battery_module',
    'battery_pack',
    'bms',
    'pcs',
    'thermal_management',
    'fire_suppression',
    'enclosure',
    'switchgear',
    'communication'
);

CREATE TYPE parameter_data_type AS ENUM (
    'numeric',
    'range',
    'boolean',
    'enum',
    'text'
);

CREATE TYPE compliance_status AS ENUM (
    'pass',
    'fail',
    'waived',
    'pending'
);

CREATE TYPE workflow_stage AS ENUM (
    'draft',
    'engineering_review',
    'technical_lead',
    'management',
    'customer_submission',
    'customer_signoff',
    'locked'
);

CREATE TYPE approval_action AS ENUM (
    'submit',
    'approve',
    'reject',
    'waive',
    'lock'
);

CREATE TYPE user_role AS ENUM (
    'admin',
    'engineer',
    'reviewer',
    'commercial',
    'customer'
);

CREATE TYPE project_type AS ENUM (
    'utility',
    'ci',
    'btm',
    'hybrid'
);

CREATE TYPE project_status AS ENUM (
    'active',
    'on_hold',
    'completed',
    'cancelled'
);

CREATE TYPE document_format AS ENUM (
    'pdf',
    'excel',
    'pptx'
);

CREATE TYPE document_type AS ENUM (
    'compliance_sheet',
    'comparison_report',
    'customer_proposal',
    'audit_export',
    'full_project_pack'
);

CREATE TYPE extraction_source AS ENUM (
    'ai',
    'manual',
    'import'
);

-- ---------------------------------------------------------------------------
-- 2. USERS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    role            user_role NOT NULL DEFAULT 'engineer',
    organisation    TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    keycloak_sub    TEXT UNIQUE,                 -- Keycloak subject claim
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role  ON users(role);

-- ---------------------------------------------------------------------------
-- 3. OEM REPOSITORY
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS oems (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL UNIQUE,
    country_of_origin TEXT NOT NULL,
    website         TEXT,
    contact_email   TEXT,
    is_approved     BOOLEAN NOT NULL DEFAULT FALSE,
    notes           TEXT,
    created_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_oems_name ON oems USING gin(name gin_trgm_ops);

CREATE TABLE IF NOT EXISTS component_types (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL UNIQUE,
    category        component_category NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS component_models (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    oem_id          UUID NOT NULL REFERENCES oems(id) ON DELETE RESTRICT,
    component_type_id UUID NOT NULL REFERENCES component_types(id) ON DELETE RESTRICT,
    model_name      TEXT NOT NULL,
    datasheet_url   TEXT,
    datasheet_minio_key TEXT,                    -- MinIO object key for uploaded PDF
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    fill_rate       NUMERIC(5,2) CHECK (fill_rate BETWEEN 0 AND 100),
    compliance_score NUMERIC(5,2) CHECK (compliance_score BETWEEN 0 AND 100),
    created_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(oem_id, model_name)
);

CREATE INDEX IF NOT EXISTS idx_component_models_oem    ON component_models(oem_id);
CREATE INDEX IF NOT EXISTS idx_component_models_type   ON component_models(component_type_id);
CREATE INDEX IF NOT EXISTS idx_component_models_name   ON component_models USING gin(model_name gin_trgm_ops);

-- ---------------------------------------------------------------------------
-- 4. PARAMETER ENGINE
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS standard_parameters (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_type_id UUID NOT NULL REFERENCES component_types(id) ON DELETE RESTRICT,
    code            TEXT NOT NULL,               -- e.g. 'NOM_VOLTAGE', 'CYCLE_LIFE'
    display_name    TEXT NOT NULL,
    section         TEXT NOT NULL,               -- 'Electrical' | 'Thermal' | 'Safety' | 'Origin'
    data_type       parameter_data_type NOT NULL,
    unit            TEXT,                        -- e.g. 'V', 'Ah', '°C', '%'
    is_mandatory    BOOLEAN NOT NULL DEFAULT FALSE,
    acceptance_min  NUMERIC,
    acceptance_max  NUMERIC,
    acceptance_enum TEXT[],                      -- allowed string values for enum type
    regulatory_ref  TEXT,                        -- e.g. 'IEC 62619 Cl. 7.2'
    sort_order      INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(component_type_id, code)
);

CREATE INDEX IF NOT EXISTS idx_std_params_type    ON standard_parameters(component_type_id);
CREATE INDEX IF NOT EXISTS idx_std_params_section ON standard_parameters(section);

CREATE TABLE IF NOT EXISTS parameter_values (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_model_id UUID NOT NULL REFERENCES component_models(id) ON DELETE CASCADE,
    standard_parameter_id UUID NOT NULL REFERENCES standard_parameters(id) ON DELETE RESTRICT,
    value_raw       TEXT,                        -- always stored as text; cast on read
    value_jsonb     JSONB,                       -- for range / structured values: {"min":x,"max":y}
    confidence      NUMERIC(4,3) CHECK (confidence BETWEEN 0 AND 1),
    source          extraction_source NOT NULL DEFAULT 'manual',
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    extracted_at    TIMESTAMPTZ,
    verified_by     UUID REFERENCES users(id) ON DELETE SET NULL,
    verified_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(component_model_id, standard_parameter_id)
);

CREATE INDEX IF NOT EXISTS idx_param_values_model  ON parameter_values(component_model_id);
CREATE INDEX IF NOT EXISTS idx_param_values_param  ON parameter_values(standard_parameter_id);

-- ---------------------------------------------------------------------------
-- 5. PROJECTS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS projects (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL,
    client_name     TEXT NOT NULL,
    project_type    project_type NOT NULL,
    status          project_status NOT NULL DEFAULT 'active',
    capacity_kwh    NUMERIC(12,2),
    power_kw        NUMERIC(12,2),
    location        TEXT,
    state           TEXT,                        -- Indian state
    customer_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_client ON projects USING gin(client_name gin_trgm_ops);

-- ---------------------------------------------------------------------------
-- 6. COMPLIANCE TEMPLATES
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS compliance_templates (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL UNIQUE,
    component_type_id UUID NOT NULL REFERENCES component_types(id) ON DELETE RESTRICT,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS compliance_template_parameters (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    compliance_template_id  UUID NOT NULL REFERENCES compliance_templates(id) ON DELETE CASCADE,
    standard_parameter_id   UUID NOT NULL REFERENCES standard_parameters(id) ON DELETE RESTRICT,
    is_mandatory_override   BOOLEAN,             -- NULL = use standard_parameter.is_mandatory
    sort_order              INTEGER NOT NULL DEFAULT 0,
    UNIQUE(compliance_template_id, standard_parameter_id)
);

-- ---------------------------------------------------------------------------
-- 7. TECHNICAL SHEETS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS technical_sheets (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sheet_number    TEXT UNIQUE,                 -- auto-assigned: TCS-001, TCS-002, ...
    project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,
    component_model_id UUID NOT NULL REFERENCES component_models(id) ON DELETE RESTRICT,
    compliance_template_id UUID REFERENCES compliance_templates(id) ON DELETE SET NULL,
    stage           workflow_stage NOT NULL DEFAULT 'draft',
    revision        INTEGER NOT NULL DEFAULT 1,  -- increments on rejection
    compliance_score NUMERIC(5,2) CHECK (compliance_score BETWEEN 0 AND 100),
    pass_count      INTEGER NOT NULL DEFAULT 0,
    fail_count      INTEGER NOT NULL DEFAULT 0,
    waived_count    INTEGER NOT NULL DEFAULT 0,
    pending_count   INTEGER NOT NULL DEFAULT 0,
    is_locked       BOOLEAN NOT NULL DEFAULT FALSE,
    lock_hash       TEXT,                        -- SHA-256 of canonical JSON at lock time
    locked_at       TIMESTAMPTZ,
    locked_by       UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by      UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sheets_project   ON technical_sheets(project_id);
CREATE INDEX IF NOT EXISTS idx_sheets_model     ON technical_sheets(component_model_id);
CREATE INDEX IF NOT EXISTS idx_sheets_stage     ON technical_sheets(stage);
CREATE INDEX IF NOT EXISTS idx_sheets_locked    ON technical_sheets(is_locked);

CREATE TABLE IF NOT EXISTS sheet_compliance_results (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technical_sheet_id      UUID NOT NULL REFERENCES technical_sheets(id) ON DELETE CASCADE,
    standard_parameter_id   UUID NOT NULL REFERENCES standard_parameters(id) ON DELETE RESTRICT,
    oem_value               TEXT,
    status                  compliance_status NOT NULL DEFAULT 'pending',
    waive_reason            TEXT,
    waived_by               UUID REFERENCES users(id) ON DELETE SET NULL,
    waived_at               TIMESTAMPTZ,
    evaluated_at            TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(technical_sheet_id, standard_parameter_id)
);

CREATE INDEX IF NOT EXISTS idx_results_sheet   ON sheet_compliance_results(technical_sheet_id);
CREATE INDEX IF NOT EXISTS idx_results_status  ON sheet_compliance_results(status);

-- ---------------------------------------------------------------------------
-- 8. SHEET VERSIONS (immutable snapshots)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sheet_versions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technical_sheet_id UUID NOT NULL REFERENCES technical_sheets(id) ON DELETE CASCADE,
    revision        INTEGER NOT NULL,
    stage           workflow_stage NOT NULL,
    snapshot        JSONB NOT NULL,              -- full sheet + results + model + OEM at this moment
    created_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_versions_sheet ON sheet_versions(technical_sheet_id);

-- ---------------------------------------------------------------------------
-- 9. APPROVAL WORKFLOW
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS approval_workflows (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_number TEXT UNIQUE,                 -- auto-assigned: WF-001, WF-002, ...
    technical_sheet_id UUID NOT NULL UNIQUE REFERENCES technical_sheets(id) ON DELETE CASCADE,
    current_stage   workflow_stage NOT NULL DEFAULT 'draft',
    assigned_to     UUID REFERENCES users(id) ON DELETE SET NULL,
    due_date        DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workflows_sheet ON approval_workflows(technical_sheet_id);
CREATE INDEX IF NOT EXISTS idx_workflows_stage ON approval_workflows(current_stage);

CREATE TABLE IF NOT EXISTS workflow_steps (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id     UUID NOT NULL REFERENCES approval_workflows(id) ON DELETE CASCADE,
    stage           workflow_stage NOT NULL,
    action          approval_action NOT NULL,
    actor_id        UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    comment         TEXT,
    signature_hash  TEXT,                        -- SHA-256(actor_id || timestamp || sheet_id)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- NO updated_at — this table is append-only. Trigger enforces this.
);

CREATE INDEX IF NOT EXISTS idx_wf_steps_workflow ON workflow_steps(workflow_id);
CREATE INDEX IF NOT EXISTS idx_wf_steps_actor    ON workflow_steps(actor_id);

-- ---------------------------------------------------------------------------
-- 10. DOCUMENTS (export centre)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS documents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technical_sheet_id UUID REFERENCES technical_sheets(id) ON DELETE SET NULL,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    document_type   document_type NOT NULL,
    format          document_format NOT NULL,
    minio_key       TEXT,                        -- MinIO object key
    file_size_bytes BIGINT,
    sha256          TEXT,                        -- content hash for integrity
    generated_by    UUID REFERENCES users(id) ON DELETE SET NULL,
    celery_task_id  TEXT,                        -- track async generation task
    is_ready        BOOLEAN NOT NULL DEFAULT FALSE,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ready_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_documents_sheet   ON documents(technical_sheet_id);
CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id);

-- ---------------------------------------------------------------------------
-- 11. AI EXTRACTION JOBS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_extraction_jobs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_model_id UUID NOT NULL REFERENCES component_models(id) ON DELETE CASCADE,
    minio_key       TEXT NOT NULL,               -- uploaded datasheet PDF
    celery_task_id  TEXT,
    status          TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','done','failed')),
    parameters_extracted INTEGER DEFAULT 0,
    parameters_auto_verified INTEGER DEFAULT 0,  -- confidence >= 0.90
    parameters_flagged INTEGER DEFAULT 0,        -- 0.80 <= confidence < 0.90
    parameters_manual INTEGER DEFAULT 0,         -- confidence < 0.80
    raw_response    JSONB,                       -- full Claude API response stored for audit
    error_message   TEXT,
    triggered_by    UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

-- ---------------------------------------------------------------------------
-- 12. AUDIT LOGS (partitioned by quarter)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_logs (
    id              UUID NOT NULL DEFAULT uuid_generate_v4(),
    actor_id        UUID REFERENCES users(id) ON DELETE SET NULL,
    action          TEXT NOT NULL,               -- e.g. 'sheet.advance', 'oem.create'
    entity_type     TEXT NOT NULL,               -- 'technical_sheet', 'oem', etc.
    entity_id       UUID,
    old_values      JSONB,
    new_values      JSONB,
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Quarterly partitions — extend each quarter
CREATE TABLE IF NOT EXISTS audit_logs_2026_q1 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');

CREATE TABLE IF NOT EXISTS audit_logs_2026_q2 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');

CREATE TABLE IF NOT EXISTS audit_logs_2026_q3 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');

CREATE TABLE IF NOT EXISTS audit_logs_2026_q4 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');

CREATE TABLE IF NOT EXISTS audit_logs_2027_q1 PARTITION OF audit_logs
    FOR VALUES FROM ('2027-01-01') TO ('2027-04-01');

CREATE INDEX IF NOT EXISTS idx_audit_actor    ON audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity   ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_created  ON audit_logs(created_at DESC);

-- ---------------------------------------------------------------------------
-- 13. AUTO-SEQUENCE TRIGGERS (TCS-NNN, WF-NNN)
-- ---------------------------------------------------------------------------

-- Sheet number sequence
CREATE SEQUENCE IF NOT EXISTS seq_sheet_number START 1;

CREATE OR REPLACE FUNCTION assign_sheet_number()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.sheet_number IS NULL THEN
        NEW.sheet_number := 'TCS-' || LPAD(nextval('seq_sheet_number')::TEXT, 3, '0');
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_assign_sheet_number ON technical_sheets;
CREATE TRIGGER trg_assign_sheet_number
    BEFORE INSERT ON technical_sheets
    FOR EACH ROW EXECUTE FUNCTION assign_sheet_number();

-- Workflow number sequence
CREATE SEQUENCE IF NOT EXISTS seq_workflow_number START 1;

CREATE OR REPLACE FUNCTION assign_workflow_number()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.workflow_number IS NULL THEN
        NEW.workflow_number := 'WF-' || LPAD(nextval('seq_workflow_number')::TEXT, 3, '0');
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_assign_workflow_number ON approval_workflows;
CREATE TRIGGER trg_assign_workflow_number
    BEFORE INSERT ON approval_workflows
    FOR EACH ROW EXECUTE FUNCTION assign_workflow_number();

-- updated_at auto-update
CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_touch_oems ON oems;
CREATE TRIGGER trg_touch_oems BEFORE UPDATE ON oems FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_touch_component_models ON component_models;
CREATE TRIGGER trg_touch_component_models BEFORE UPDATE ON component_models FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_touch_parameter_values ON parameter_values;
CREATE TRIGGER trg_touch_parameter_values BEFORE UPDATE ON parameter_values FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_touch_projects ON projects;
CREATE TRIGGER trg_touch_projects BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_touch_technical_sheets ON technical_sheets;
CREATE TRIGGER trg_touch_technical_sheets BEFORE UPDATE ON technical_sheets FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_touch_sheet_results ON sheet_compliance_results;
CREATE TRIGGER trg_touch_sheet_results BEFORE UPDATE ON sheet_compliance_results FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_touch_workflows ON approval_workflows;
CREATE TRIGGER trg_touch_workflows BEFORE UPDATE ON approval_workflows FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

DROP TRIGGER IF EXISTS trg_touch_users ON users;
CREATE TRIGGER trg_touch_users BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- ---------------------------------------------------------------------------
-- 14. IMMUTABILITY TRIGGERS
-- ---------------------------------------------------------------------------

-- 14a. Locked technical sheet — no updates or deletes
CREATE OR REPLACE FUNCTION enforce_sheet_immutability()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.is_locked = TRUE THEN
        RAISE EXCEPTION 'Sheet % is locked and cannot be modified or deleted.', OLD.sheet_number
            USING ERRCODE = 'P0001';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_sheet_immutability ON technical_sheets;
CREATE TRIGGER trg_sheet_immutability
    BEFORE UPDATE OR DELETE ON technical_sheets
    FOR EACH ROW EXECUTE FUNCTION enforce_sheet_immutability();

-- 14b. Workflow steps — append-only (no UPDATE, no DELETE)
CREATE OR REPLACE FUNCTION enforce_wf_step_immutability()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'workflow_steps is append-only. UPDATE and DELETE are not permitted.'
        USING ERRCODE = 'P0002';
END;
$$;

DROP TRIGGER IF EXISTS trg_wf_step_immutability ON workflow_steps;
CREATE TRIGGER trg_wf_step_immutability
    BEFORE UPDATE OR DELETE ON workflow_steps
    FOR EACH ROW EXECUTE FUNCTION enforce_wf_step_immutability();

-- 14c. Audit logs — append-only
CREATE OR REPLACE FUNCTION enforce_audit_immutability()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'audit_logs is append-only. UPDATE and DELETE are not permitted.'
        USING ERRCODE = 'P0003';
END;
$$;

DROP TRIGGER IF EXISTS trg_audit_immutability ON audit_logs;
CREATE TRIGGER trg_audit_immutability
    BEFORE UPDATE OR DELETE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION enforce_audit_immutability();

-- ---------------------------------------------------------------------------
-- 15. STORED PROCEDURE: advance_workflow()
-- ---------------------------------------------------------------------------
-- Single atomic operation for all stage transitions.
-- Called by FastAPI; never call individual UPDATEs from application code.

CREATE OR REPLACE PROCEDURE advance_workflow(
    p_workflow_id   UUID,
    p_action        approval_action,
    p_actor_id      UUID,
    p_comment       TEXT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    v_sheet_id      UUID;
    v_current_stage workflow_stage;
    v_next_stage    workflow_stage;
    v_is_locked     BOOLEAN;
    v_sig_hash      TEXT;
    v_revision      INTEGER;
BEGIN
    -- Lock the workflow row for this transaction
    SELECT aw.technical_sheet_id, aw.current_stage, ts.is_locked, ts.revision
    INTO v_sheet_id, v_current_stage, v_is_locked, v_revision
    FROM approval_workflows aw
    JOIN technical_sheets ts ON ts.id = aw.technical_sheet_id
    WHERE aw.id = p_workflow_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Workflow % not found.', p_workflow_id USING ERRCODE = 'P0010';
    END IF;

    IF v_is_locked THEN
        RAISE EXCEPTION 'Sheet is locked. No further transitions permitted.' USING ERRCODE = 'P0001';
    END IF;

    -- Determine next stage
    v_next_stage := CASE
        WHEN p_action = 'reject'  THEN 'draft'::workflow_stage
        WHEN p_action = 'lock'    THEN 'locked'::workflow_stage
        WHEN v_current_stage = 'draft'               AND p_action = 'submit'  THEN 'engineering_review'
        WHEN v_current_stage = 'engineering_review'  AND p_action = 'approve' THEN 'technical_lead'
        WHEN v_current_stage = 'technical_lead'      AND p_action = 'approve' THEN 'management'
        WHEN v_current_stage = 'management'          AND p_action = 'approve' THEN 'customer_submission'
        WHEN v_current_stage = 'customer_submission' AND p_action = 'approve' THEN 'customer_signoff'
        WHEN v_current_stage = 'customer_signoff'    AND p_action = 'approve' THEN 'locked'
        ELSE RAISE_EXCEPTION_PLACEHOLDER
    END;

    -- Signature hash
    v_sig_hash := encode(
        digest(p_actor_id::TEXT || NOW()::TEXT || v_sheet_id::TEXT, 'sha256'),
        'hex'
    );

    -- Append workflow step (trigger blocks any future UPDATE/DELETE on this row)
    INSERT INTO workflow_steps (workflow_id, stage, action, actor_id, comment, signature_hash)
    VALUES (p_workflow_id, v_current_stage, p_action, p_actor_id, p_comment, v_sig_hash);

    -- If reject → increment revision on the sheet
    IF p_action = 'reject' THEN
        UPDATE technical_sheets
        SET revision = revision + 1,
            stage    = 'draft'
        WHERE id = v_sheet_id;
    ELSIF v_next_stage = 'locked' THEN
        UPDATE technical_sheets
        SET stage      = 'locked',
            is_locked  = TRUE,
            locked_at  = NOW(),
            locked_by  = p_actor_id,
            lock_hash  = encode(digest(v_sheet_id::TEXT || NOW()::TEXT, 'sha256'), 'hex')
        WHERE id = v_sheet_id;
    ELSE
        UPDATE technical_sheets SET stage = v_next_stage WHERE id = v_sheet_id;
    END IF;

    -- Update workflow current_stage
    UPDATE approval_workflows SET current_stage = v_next_stage WHERE id = p_workflow_id;

    -- Write audit log
    INSERT INTO audit_logs (actor_id, action, entity_type, entity_id, new_values)
    VALUES (
        p_actor_id,
        'workflow.' || p_action::TEXT,
        'approval_workflow',
        p_workflow_id,
        jsonb_build_object(
            'from_stage', v_current_stage,
            'to_stage',   v_next_stage,
            'comment',    p_comment
        )
    );

END;
$$;

-- Fix the ELSE RAISE in CASE — replace placeholder with real error
-- (Neon doesn't allow RAISE in CASE expressions; use IF/ELSIF instead)
CREATE OR REPLACE PROCEDURE advance_workflow(
    p_workflow_id   UUID,
    p_action        approval_action,
    p_actor_id      UUID,
    p_comment       TEXT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    v_sheet_id      UUID;
    v_current_stage workflow_stage;
    v_next_stage    workflow_stage;
    v_is_locked     BOOLEAN;
    v_sig_hash      TEXT;
BEGIN
    SELECT aw.technical_sheet_id, aw.current_stage, ts.is_locked
    INTO v_sheet_id, v_current_stage, v_is_locked
    FROM approval_workflows aw
    JOIN technical_sheets ts ON ts.id = aw.technical_sheet_id
    WHERE aw.id = p_workflow_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Workflow % not found.', p_workflow_id USING ERRCODE = 'P0010';
    END IF;

    IF v_is_locked THEN
        RAISE EXCEPTION 'Sheet is locked. No further transitions permitted.' USING ERRCODE = 'P0001';
    END IF;

    -- Determine next stage using IF/ELSIF (no RAISE in CASE on Neon)
    IF p_action = 'reject' THEN
        v_next_stage := 'draft';
    ELSIF p_action = 'lock' OR (v_current_stage = 'customer_signoff' AND p_action = 'approve') THEN
        v_next_stage := 'locked';
    ELSIF v_current_stage = 'draft' AND p_action = 'submit' THEN
        v_next_stage := 'engineering_review';
    ELSIF v_current_stage = 'engineering_review' AND p_action = 'approve' THEN
        v_next_stage := 'technical_lead';
    ELSIF v_current_stage = 'technical_lead' AND p_action = 'approve' THEN
        v_next_stage := 'management';
    ELSIF v_current_stage = 'management' AND p_action = 'approve' THEN
        v_next_stage := 'customer_submission';
    ELSIF v_current_stage = 'customer_submission' AND p_action = 'approve' THEN
        v_next_stage := 'customer_signoff';
    ELSE
        RAISE EXCEPTION 'Invalid transition: % from stage %.', p_action, v_current_stage
            USING ERRCODE = 'P0011';
    END IF;

    v_sig_hash := encode(
        digest(p_actor_id::TEXT || NOW()::TEXT || v_sheet_id::TEXT, 'sha256'),
        'hex'
    );

    INSERT INTO workflow_steps (workflow_id, stage, action, actor_id, comment, signature_hash)
    VALUES (p_workflow_id, v_current_stage, p_action, p_actor_id, p_comment, v_sig_hash);

    IF p_action = 'reject' THEN
        UPDATE technical_sheets
        SET revision = revision + 1, stage = 'draft'
        WHERE id = v_sheet_id;
    ELSIF v_next_stage = 'locked' THEN
        UPDATE technical_sheets
        SET stage = 'locked', is_locked = TRUE, locked_at = NOW(), locked_by = p_actor_id,
            lock_hash = encode(digest(v_sheet_id::TEXT || NOW()::TEXT, 'sha256'), 'hex')
        WHERE id = v_sheet_id;
    ELSE
        UPDATE technical_sheets SET stage = v_next_stage WHERE id = v_sheet_id;
    END IF;

    UPDATE approval_workflows SET current_stage = v_next_stage WHERE id = p_workflow_id;

    INSERT INTO audit_logs (actor_id, action, entity_type, entity_id, new_values)
    VALUES (
        p_actor_id,
        'workflow.' || p_action::TEXT,
        'approval_workflow',
        p_workflow_id,
        jsonb_build_object('from_stage', v_current_stage, 'to_stage', v_next_stage, 'comment', p_comment)
    );
END;
$$;

-- ---------------------------------------------------------------------------
-- 16. STORED PROCEDURE: create_sheet_version()
-- ---------------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE create_sheet_version(p_sheet_id UUID, p_actor_id UUID)
LANGUAGE plpgsql AS $$
DECLARE
    v_snapshot JSONB;
    v_revision INTEGER;
    v_stage    workflow_stage;
BEGIN
    SELECT
        jsonb_build_object(
            'sheet',   row_to_json(ts),
            'model',   row_to_json(cm),
            'oem',     row_to_json(o),
            'results', (
                SELECT jsonb_agg(row_to_json(r))
                FROM sheet_compliance_results r
                WHERE r.technical_sheet_id = ts.id
            )
        ),
        ts.revision,
        ts.stage
    INTO v_snapshot, v_revision, v_stage
    FROM technical_sheets ts
    JOIN component_models cm ON cm.id = ts.component_model_id
    JOIN oems o ON o.id = cm.oem_id
    WHERE ts.id = p_sheet_id;

    INSERT INTO sheet_versions (technical_sheet_id, revision, stage, snapshot, created_by)
    VALUES (p_sheet_id, v_revision, v_stage, v_snapshot, p_actor_id);
END;
$$;

-- ---------------------------------------------------------------------------
-- 17. ROW-LEVEL SECURITY
-- ---------------------------------------------------------------------------
-- Enable RLS on tables that require it.
-- Application passes the authenticated user's UUID via:
--   SET LOCAL app.current_user_id = '<uuid>';
--   SET LOCAL app.current_user_role = 'engineer';

ALTER TABLE technical_sheets ENABLE ROW LEVEL SECURITY;
ALTER TABLE sheet_compliance_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_steps ENABLE ROW LEVEL SECURITY;

-- Helper function: get current user role from session var
CREATE OR REPLACE FUNCTION current_user_role()
RETURNS user_role LANGUAGE sql STABLE AS $$
    SELECT NULLIF(current_setting('app.current_user_role', TRUE), '')::user_role;
$$;

CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID LANGUAGE sql STABLE AS $$
    SELECT NULLIF(current_setting('app.current_user_id', TRUE), '')::UUID;
$$;

-- Customers see only sheets in their project at stage >= customer_submission
DROP POLICY IF EXISTS policy_sheets_customer ON technical_sheets;
CREATE POLICY policy_sheets_customer ON technical_sheets
    FOR SELECT
    USING (
        current_user_role() != 'customer'
        OR (
            current_user_role() = 'customer'
            AND stage IN ('customer_submission', 'customer_signoff', 'locked')
            AND project_id IN (
                SELECT id FROM projects
                WHERE customer_user_id = current_user_id()
            )
        )
    );

-- Internal roles see everything
DROP POLICY IF EXISTS policy_sheets_internal ON technical_sheets;
CREATE POLICY policy_sheets_internal ON technical_sheets
    FOR ALL
    USING (current_user_role() IS NULL OR current_user_role() != 'customer');

-- Mirror policies for sheet_compliance_results
DROP POLICY IF EXISTS policy_results_customer ON sheet_compliance_results;
CREATE POLICY policy_results_customer ON sheet_compliance_results
    FOR SELECT
    USING (
        current_user_role() != 'customer'
        OR technical_sheet_id IN (
            SELECT id FROM technical_sheets
            WHERE stage IN ('customer_submission', 'customer_signoff', 'locked')
            AND project_id IN (
                SELECT id FROM projects
                WHERE customer_user_id = current_user_id()
            )
        )
    );

-- ---------------------------------------------------------------------------
-- 18. COMPLIANCE SCORE RECOMPUTE TRIGGER
-- ---------------------------------------------------------------------------
-- Automatically recalculate pass/fail/waived counts + compliance_score on the
-- parent technical_sheet whenever a sheet_compliance_results row changes.

CREATE OR REPLACE FUNCTION recompute_sheet_score()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_sheet_id UUID;
    v_pass     INTEGER;
    v_fail     INTEGER;
    v_waived   INTEGER;
    v_pending  INTEGER;
    v_total    INTEGER;
    v_score    NUMERIC(5,2);
BEGIN
    v_sheet_id := COALESCE(NEW.technical_sheet_id, OLD.technical_sheet_id);

    SELECT
        COUNT(*) FILTER (WHERE status = 'pass'),
        COUNT(*) FILTER (WHERE status = 'fail'),
        COUNT(*) FILTER (WHERE status = 'waived'),
        COUNT(*) FILTER (WHERE status = 'pending')
    INTO v_pass, v_fail, v_waived, v_pending
    FROM sheet_compliance_results
    WHERE technical_sheet_id = v_sheet_id;

    v_total := v_pass + v_fail + v_waived + v_pending;
    v_score := CASE WHEN v_total > 0
        THEN ROUND(((v_pass + v_waived)::NUMERIC / v_total) * 100, 2)
        ELSE 0 END;

    UPDATE technical_sheets
    SET pass_count       = v_pass,
        fail_count       = v_fail,
        waived_count     = v_waived,
        pending_count    = v_pending,
        compliance_score = v_score
    WHERE id = v_sheet_id;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_recompute_score ON sheet_compliance_results;
CREATE TRIGGER trg_recompute_score
    AFTER INSERT OR UPDATE OR DELETE ON sheet_compliance_results
    FOR EACH ROW EXECUTE FUNCTION recompute_sheet_score();

-- =============================================================================
-- SCHEMA COMPLETE
-- Tables: users, oems, component_types, component_models,
--         standard_parameters, parameter_values,
--         projects, compliance_templates, compliance_template_parameters,
--         technical_sheets, sheet_compliance_results, sheet_versions,
--         approval_workflows, workflow_steps,
--         documents, ai_extraction_jobs, audit_logs (partitioned)
-- ENUMs: 10
-- Triggers: 12
-- Stored procedures: 2 (advance_workflow, create_sheet_version)
-- Sequences: 2 (seq_sheet_number, seq_workflow_number)
-- =============================================================================
