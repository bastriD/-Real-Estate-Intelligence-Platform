-- =============================================================================
-- 001_schema_structure.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate the physical PostgreSQL V2 schema after deployment.
--
-- Scope:
--   - real_estate schema exists
--   - exactly 16 expected business tables exist
--   - required primary keys exist
--   - required foreign keys exist
--   - required CHECK constraints exist
--   - required partial unique index exists
--   - visite structure introduced by migration 004 exists
--   - audit_log structure introduced by migration 004 exists
--
-- This script is read-only.
-- =============================================================================

\set ON_ERROR_STOP on


-- =============================================================================
-- 1. SCHEMA EXISTS
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.schemata
        WHERE schema_name = 'real_estate'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: schema real_estate does not exist';
    END IF;

    RAISE NOTICE
        'PASS: schema real_estate exists';
END
$$;


-- =============================================================================
-- 2. EXPECTED TABLE COUNT
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM information_schema.tables
    WHERE table_schema = 'real_estate'
      AND table_type = 'BASE TABLE';

    IF actual_count <> 16 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 16 tables, found %',
            actual_count;
    END IF;

    RAISE NOTICE
        'PASS: 16 real_estate tables found';
END
$$;


-- =============================================================================
-- 3. EXPECTED TABLES
-- =============================================================================

DO $$
DECLARE
    missing_tables TEXT;
BEGIN
    SELECT string_agg(
        expected.table_name,
        ', '
        ORDER BY expected.table_name
    )
    INTO missing_tables
    FROM (
        VALUES
            ('audit_log'),
            ('bareme_commission'),
            ('bien'),
            ('chasseur'),
            ('client'),
            ('commentaire'),
            ('demande'),
            ('demande_version'),
            ('document'),
            ('mandat'),
            ('mandat_secteur'),
            ('paiement'),
            ('presentation'),
            ('secteur'),
            ('source'),
            ('visite')
    ) AS expected(table_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM information_schema.tables actual
        WHERE actual.table_schema = 'real_estate'
          AND actual.table_name = expected.table_name
          AND actual.table_type = 'BASE TABLE'
    );

    IF missing_tables IS NOT NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: missing tables: %',
            missing_tables;
    END IF;

    RAISE NOTICE
        'PASS: all expected tables exist';
END
$$;


-- =============================================================================
-- 4. PRIMARY KEYS
-- =============================================================================

DO $$
DECLARE
    missing_constraints TEXT;
BEGIN
    SELECT string_agg(
        expected.constraint_name,
        ', '
        ORDER BY expected.constraint_name
    )
    INTO missing_constraints
    FROM (
        VALUES
            ('pk_audit_log'),
            ('pk_bareme_commission'),
            ('pk_bien'),
            ('pk_chasseur'),
            ('pk_client'),
            ('pk_commentaire'),
            ('pk_demande'),
            ('pk_demande_version'),
            ('pk_document'),
            ('pk_mandat'),
            ('pk_mandat_secteur'),
            ('pk_paiement'),
            ('pk_presentation'),
            ('pk_secteur'),
            ('pk_source'),
            ('pk_visite')
    ) AS expected(constraint_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_namespace n
          ON n.oid = c.connamespace
        WHERE n.nspname = 'real_estate'
          AND c.conname = expected.constraint_name
          AND c.contype = 'p'
    );

    IF missing_constraints IS NOT NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: missing primary keys: %',
            missing_constraints;
    END IF;

    RAISE NOTICE
        'PASS: all expected primary keys exist';
END
$$;


-- =============================================================================
-- 5. CRITICAL FOREIGN KEYS
-- =============================================================================

DO $$
DECLARE
    missing_constraints TEXT;
BEGIN
    SELECT string_agg(
        expected.constraint_name,
        ', '
        ORDER BY expected.constraint_name
    )
    INTO missing_constraints
    FROM (
        VALUES
            ('fk_mandat_client'),
            ('fk_mandat_chasseur'),

            ('fk_mandat_secteur_mandat'),
            ('fk_mandat_secteur_secteur'),

            ('fk_demande_mandat'),

            ('fk_demande_version_demande'),
            ('fk_demande_version_client'),
            ('fk_demande_version_chasseur'),

            ('fk_bien_source'),

            ('fk_presentation_demande_version'),
            ('fk_presentation_bien'),

            ('fk_commentaire_demande_version'),
            ('fk_commentaire_bien'),
            ('fk_commentaire_client'),
            ('fk_commentaire_chasseur'),

            ('fk_document_bien'),

            ('fk_bareme_commission_chasseur'),

            ('fk_paiement_mandat'),
            ('fk_paiement_bareme'),

            ('fk_visite_presentation')
    ) AS expected(constraint_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_namespace n
          ON n.oid = c.connamespace
        WHERE n.nspname = 'real_estate'
          AND c.conname = expected.constraint_name
          AND c.contype = 'f'
    );

    IF missing_constraints IS NOT NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: missing foreign keys: %',
            missing_constraints;
    END IF;

    RAISE NOTICE
        'PASS: all expected foreign keys exist';
END
$$;


-- =============================================================================
-- 6. CRITICAL CHECK CONSTRAINTS
-- =============================================================================

DO $$
DECLARE
    missing_constraints TEXT;
BEGIN
    SELECT string_agg(
        expected.constraint_name,
        ', '
        ORDER BY expected.constraint_name
    )
    INTO missing_constraints
    FROM (
        VALUES
            ('ck_mandat_type'),
            ('ck_mandat_mode_signature'),
            ('ck_mandat_dates'),

            ('ck_demande_version_auteur'),
            ('ck_demande_version_budget_range'),
            ('ck_demande_version_dpe'),

            ('ck_bien_dpe'),

            ('ck_presentation_score'),

            ('ck_commentaire_auteur'),

            ('ck_bareme_taux'),

            ('ck_paiement_montant_achat'),

            ('ck_visite_statut'),
            ('ck_visite_note'),
            ('ck_visite_photos_array'),

            ('ck_audit_log_operation'),
            ('ck_audit_log_contexte_object')
    ) AS expected(constraint_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_namespace n
          ON n.oid = c.connamespace
        WHERE n.nspname = 'real_estate'
          AND c.conname = expected.constraint_name
          AND c.contype = 'c'
    );

    IF missing_constraints IS NOT NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: missing CHECK constraints: %',
            missing_constraints;
    END IF;

    RAISE NOTICE
        'PASS: critical CHECK constraints exist';
END
$$;


-- =============================================================================
-- 7. ONE ACTIVE DEMANDE VERSION INDEX
-- =============================================================================

DO $$
DECLARE
    index_definition TEXT;
BEGIN
    SELECT indexdef
    INTO index_definition
    FROM pg_indexes
    WHERE schemaname = 'real_estate'
      AND tablename = 'demande_version'
      AND indexname = 'uq_demande_version_active';

    IF index_definition IS NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: uq_demande_version_active does not exist';
    END IF;

    IF index_definition NOT ILIKE '%UNIQUE INDEX%'
       OR index_definition NOT ILIKE '%WHERE (active = true)%'
    THEN
        RAISE EXCEPTION
            'TEST FAILED: uq_demande_version_active is not the expected partial unique index';
    END IF;

    RAISE NOTICE
        'PASS: one-active-version partial unique index exists';
END
$$;


-- =============================================================================
-- 8. LEGACY PRESERVATION COLUMN
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'real_estate'
          AND table_name = 'demande_version'
          AND column_name = 'description_recherche_legacy'
          AND data_type = 'text'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: demande_version.description_recherche_legacy is missing';
    END IF;

    RAISE NOTICE
        'PASS: legacy search description preservation column exists';
END
$$;


-- =============================================================================
-- 9. VISITE STRUCTURE
-- =============================================================================

DO $$
DECLARE
    missing_columns TEXT;
BEGIN
    SELECT string_agg(
        expected.column_name,
        ', '
        ORDER BY expected.column_name
    )
    INTO missing_columns
    FROM (
        VALUES
            ('id_visite'),
            ('date_visite'),
            ('statut'),
            ('compte_rendu'),
            ('note'),
            ('photos'),
            ('date_creation'),
            ('id_presentation')
    ) AS expected(column_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM information_schema.columns actual
        WHERE actual.table_schema = 'real_estate'
          AND actual.table_name = 'visite'
          AND actual.column_name = expected.column_name
    );

    IF missing_columns IS NOT NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.visite missing columns: %',
            missing_columns;
    END IF;

    RAISE NOTICE
        'PASS: real_estate.visite structure validated';
END
$$;


-- =============================================================================
-- 10. AUDIT_LOG STRUCTURE
-- =============================================================================

DO $$
DECLARE
    missing_columns TEXT;
BEGIN
    SELECT string_agg(
        expected.column_name,
        ', '
        ORDER BY expected.column_name
    )
    INTO missing_columns
    FROM (
        VALUES
            ('id_audit'),
            ('date_evenement'),
            ('schema_name'),
            ('table_name'),
            ('operation'),
            ('record_id'),
            ('utilisateur'),
            ('ancienne_valeur'),
            ('nouvelle_valeur'),
            ('contexte')
    ) AS expected(column_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM information_schema.columns actual
        WHERE actual.table_schema = 'real_estate'
          AND actual.table_name = 'audit_log'
          AND actual.column_name = expected.column_name
    );

    IF missing_columns IS NOT NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.audit_log missing columns: %',
            missing_columns;
    END IF;

    RAISE NOTICE
        'PASS: real_estate.audit_log structure validated';
END
$$;


-- =============================================================================
-- 11. MIGRATION 004 INDEXES
-- =============================================================================

DO $$
DECLARE
    missing_indexes TEXT;
BEGIN
    SELECT string_agg(
        expected.index_name,
        ', '
        ORDER BY expected.index_name
    )
    INTO missing_indexes
    FROM (
        VALUES
            ('idx_visite_id_presentation'),
            ('idx_visite_date'),
            ('idx_audit_log_date_evenement'),
            ('idx_audit_log_table_name'),
            ('idx_audit_log_record')
    ) AS expected(index_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM pg_indexes actual
        WHERE actual.schemaname = 'real_estate'
          AND actual.indexname = expected.index_name
    );

    IF missing_indexes IS NOT NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: migration 004 missing indexes: %',
            missing_indexes;
    END IF;

    RAISE NOTICE
        'PASS: migration 004 indexes exist';
END
$$;


-- =============================================================================
-- FINAL RESULT
-- =============================================================================

SELECT
    'PASS' AS status,
    'PostgreSQL V2 schema structure validated successfully - 16 tables including visite and audit_log'
        AS result;