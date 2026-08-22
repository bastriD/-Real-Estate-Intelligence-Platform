-- =============================================================================
-- 001_schema_structure.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate the physical PostgreSQL V2 schema after deployment.
--
-- Scope:
--   - real_estate schema exists
--   - exactly 14 expected business tables exist
--   - required constraints exist
--   - required partial unique index exists
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
        RAISE EXCEPTION 'TEST FAILED: schema real_estate does not exist';
    END IF;

    RAISE NOTICE 'PASS: schema real_estate exists';
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

    IF actual_count <> 14 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 14 tables, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: 14 real_estate tables found';
END
$$;


-- =============================================================================
-- 3. EXPECTED TABLES
-- =============================================================================

DO $$
DECLARE
    missing_tables TEXT;
BEGIN
    SELECT string_agg(expected.table_name, ', ' ORDER BY expected.table_name)
    INTO missing_tables
    FROM (
        VALUES
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
            ('source')
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

    RAISE NOTICE 'PASS: all expected tables exist';
END
$$;


-- =============================================================================
-- 4. PRIMARY KEYS
-- =============================================================================

DO $$
DECLARE
    missing_constraints TEXT;
BEGIN
    SELECT string_agg(expected.constraint_name, ', ')
    INTO missing_constraints
    FROM (
        VALUES
            ('pk_client'),
            ('pk_chasseur'),
            ('pk_secteur'),
            ('pk_source'),
            ('pk_mandat'),
            ('pk_mandat_secteur'),
            ('pk_demande'),
            ('pk_demande_version'),
            ('pk_bien'),
            ('pk_presentation'),
            ('pk_commentaire'),
            ('pk_document'),
            ('pk_bareme_commission'),
            ('pk_paiement')
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

    RAISE NOTICE 'PASS: all expected primary keys exist';
END
$$;


-- =============================================================================
-- 5. CRITICAL FOREIGN KEYS
-- =============================================================================

DO $$
DECLARE
    missing_constraints TEXT;
BEGIN
    SELECT string_agg(expected.constraint_name, ', ')
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
            ('fk_paiement_bareme')
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

    RAISE NOTICE 'PASS: all expected foreign keys exist';
END
$$;


-- =============================================================================
-- 6. CRITICAL CHECK CONSTRAINTS
-- =============================================================================

DO $$
DECLARE
    missing_constraints TEXT;
BEGIN
    SELECT string_agg(expected.constraint_name, ', ')
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
            ('ck_paiement_montant_achat')
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

    RAISE NOTICE 'PASS: critical CHECK constraints exist';
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

    RAISE NOTICE 'PASS: one-active-version partial unique index exists';
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

    RAISE NOTICE 'PASS: legacy search description preservation column exists';
END
$$;


-- =============================================================================
-- FINAL RESULT
-- =============================================================================

SELECT
    'PASS' AS status,
    'PostgreSQL V2 schema structure validated successfully' AS result;