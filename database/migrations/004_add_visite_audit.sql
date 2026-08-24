-- =============================================================================
-- 004_add_visite_audit.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Add visit management and technical audit traceability to the
--   real_estate transactional schema.
--
-- Context:
--   - A presentation identifies a property proposed for a demand version.
--   - A presentation may result in zero, one or several visits.
--   - Visits are required to preserve business history and support
--     hunter performance indicators.
--   - audit_log provides technical traceability for future governance,
--     security and operational auditing requirements.
--
-- Important:
--   - Does NOT modify legacy "Fil_Rouge_Depart".
--   - Does NOT invent historical visits.
--   - Does NOT migrate legacy rows because no corresponding legacy
--     entities exist.
--   - Registers migration version 004 in migration_control.schema_version.
-- =============================================================================

BEGIN;

-- =============================================================================
-- VISITE
-- =============================================================================

CREATE TABLE IF NOT EXISTS real_estate.visite (
    id_visite BIGINT GENERATED ALWAYS AS IDENTITY,

    date_visite TIMESTAMPTZ NOT NULL,

    statut VARCHAR(20) NOT NULL DEFAULT 'PLANIFIEE',

    compte_rendu TEXT,

    note SMALLINT,

    photos JSONB NOT NULL DEFAULT '[]'::jsonb,

    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    id_presentation BIGINT NOT NULL,

    CONSTRAINT pk_visite
        PRIMARY KEY (id_visite),

    CONSTRAINT fk_visite_presentation
        FOREIGN KEY (id_presentation)
        REFERENCES real_estate.presentation(id_presentation)
        ON DELETE RESTRICT,

    CONSTRAINT ck_visite_statut
        CHECK (
            statut IN (
                'PLANIFIEE',
                'REALISEE',
                'ANNULEE',
                'REPORTEE'
            )
        ),

    CONSTRAINT ck_visite_note
        CHECK (
            note IS NULL
            OR note BETWEEN 0 AND 5
        ),

    CONSTRAINT ck_visite_photos_array
        CHECK (
            jsonb_typeof(photos) = 'array'
        )
);

CREATE INDEX IF NOT EXISTS idx_visite_id_presentation
    ON real_estate.visite(id_presentation);

CREATE INDEX IF NOT EXISTS idx_visite_date
    ON real_estate.visite(date_visite);


-- =============================================================================
-- AUDIT_LOG
-- =============================================================================

CREATE TABLE IF NOT EXISTS real_estate.audit_log (
    id_audit BIGINT GENERATED ALWAYS AS IDENTITY,

    date_evenement TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    schema_name VARCHAR(120) NOT NULL DEFAULT 'real_estate',

    table_name VARCHAR(120) NOT NULL,

    operation VARCHAR(10) NOT NULL,

    record_id TEXT,

    utilisateur TEXT,

    ancienne_valeur JSONB,

    nouvelle_valeur JSONB,

    contexte JSONB NOT NULL DEFAULT '{}'::jsonb,

    CONSTRAINT pk_audit_log
        PRIMARY KEY (id_audit),

    CONSTRAINT ck_audit_log_operation
        CHECK (
            operation IN (
                'INSERT',
                'UPDATE',
                'DELETE'
            )
        ),

    CONSTRAINT ck_audit_log_contexte_object
        CHECK (
            jsonb_typeof(contexte) = 'object'
        )
);

CREATE INDEX IF NOT EXISTS idx_audit_log_date_evenement
    ON real_estate.audit_log(date_evenement);

CREATE INDEX IF NOT EXISTS idx_audit_log_table_name
    ON real_estate.audit_log(table_name);

CREATE INDEX IF NOT EXISTS idx_audit_log_record
    ON real_estate.audit_log(
        schema_name,
        table_name,
        record_id
    );


-- =============================================================================
-- MIGRATION REGISTRY
-- =============================================================================

INSERT INTO migration_control.schema_version (
    version,
    description
)
VALUES (
    '004',
    'Add visite and audit_log to real_estate OLTP schema'
)
ON CONFLICT (version) DO NOTHING;


COMMIT;