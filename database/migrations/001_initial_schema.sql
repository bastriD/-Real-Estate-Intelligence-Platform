-- =============================================================================
-- 001_schema_structure.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate the deployed PostgreSQL OLTP schema structure.
--
-- Validates:
--   - schema real_estate exists
--   - exactly 16 expected business tables exist
--   - every expected table is present
--   - primary keys exist
--   - important foreign keys exist
--   - important unique constraints exist
--   - visite and audit_log introduced by migration 004 exist
--
-- Important:
--   This test validates the current deployed OLTP model.
--   It does not modify business data.
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

    IF actual_count <> 16 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 16 tables, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: 16 real_estate tables found';
END
$$;


-- =============================================================================
-- 3. EXPECTED TABLES
-- =============================================================================

DO $$
DECLARE
    expected_table TEXT;
    expected_tables TEXT[] := ARRAY[
        'audit_log',
        'bareme_commission',
        'bien',
        'chasseur',
        'client',
        'commentaire',
        'demande',
        'demande_version',
        'document',
        'mandat',
        'mandat_secteur',
        'paiement',
        'presentation',
        'secteur',
        'source',
        'visite'
    ];
BEGIN
    FOREACH expected_table IN ARRAY expected_tables
    LOOP
        IF to_regclass(
            format('real_estate.%I', expected_table)
        ) IS NULL THEN
            RAISE EXCEPTION
                'TEST FAILED: expected table real_estate.% does not exist',
                expected_table;
        END IF;
    END LOOP;

    RAISE NOTICE 'PASS: all expected tables exist';
END
$$;


-- =============================================================================
-- 4. PRIMARY KEYS
-- =============================================================================

DO $$
DECLARE
    expected_table TEXT;
    expected_tables TEXT[] := ARRAY[
        'audit_log',
        'bareme_commission',
        'bien',
        'chasseur',
        'client',
        'commentaire',
        'demande',
        'demande_version',
        'document',
        'mandat',
        'mandat_secteur',
        'paiement',
        'presentation',
        'secteur',
        'source',
        'visite'
    ];
BEGIN
    FOREACH expected_table IN ARRAY expected_tables
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t
              ON t.oid = c.conrelid
            JOIN pg_namespace n
              ON n.oid = t.relnamespace
            WHERE n.nspname = 'real_estate'
              AND t.relname = expected_table
              AND c.contype = 'p'
        ) THEN
            RAISE EXCEPTION
                'TEST FAILED: primary key missing on real_estate.%',
                expected_table;
        END IF;
    END LOOP;

    RAISE NOTICE 'PASS: primary keys exist on all expected tables';
END
$$;


-- =============================================================================
-- 5. IMPORTANT FOREIGN KEYS
-- =============================================================================

DO $$
DECLARE
    constraint_name TEXT;
    expected_constraints TEXT[] := ARRAY[
        'fk_mandat_client',
        'fk_mandat_chasseur',
        'fk_mandat_secteur_mandat',
        'fk_mandat_secteur_secteur',
        'fk_demande_mandat',
        'fk_demande_version_demande',
        'fk_bien_source',
        'fk_commentaire_demande_version',
        'fk_commentaire_bien',
        'fk_document_mandat',
        'fk_document_demande',
        'fk_presentation_demande_version',
        'fk_presentation_bien',
        'fk_paiement_mandat',
        'fk_paiement_bareme',
        'fk_visite_presentation'
    ];
BEGIN
    FOREACH constraint_name IN ARRAY expected_constraints
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t
              ON t.oid = c.conrelid
            JOIN pg_namespace n
              ON n.oid = t.relnamespace
            WHERE n.nspname = 'real_estate'
              AND c.conname = constraint_name
              AND c.contype = 'f'
        ) THEN
            RAISE EXCEPTION
                'TEST FAILED: expected foreign key % does not exist',
                constraint_name;
        END IF;
    END LOOP;

    RAISE NOTICE 'PASS: important foreign keys exist';
END
$$;


-- =============================================================================
-- 6. IMPORTANT UNIQUE CONSTRAINTS
-- =============================================================================

DO $$
DECLARE
    constraint_name TEXT;
    expected_constraints TEXT[] := ARRAY[
        'uq_client_email',
        'uq_chasseur_email',
        'uq_secteur_localisation',
        'uq_demande_mandat',
        'uq_demande_version',
        'uq_bien_source_reference',
        'uq_presentation',
        'uq_paiement_mandat'
    ];
BEGIN
    FOREACH constraint_name IN ARRAY expected_constraints
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t
              ON t.oid = c.conrelid
            JOIN pg_namespace n
              ON n.oid = t.relnamespace
            WHERE n.nspname = 'real_estate'
              AND c.conname = constraint_name
              AND c.contype = 'u'
        ) THEN
            RAISE EXCEPTION
                'TEST FAILED: expected unique constraint % does not exist',
                constraint_name;
        END IF;
    END LOOP;

    RAISE NOTICE 'PASS: important unique constraints exist';
END
$$;


-- =============================================================================
-- 7. VISITE STRUCTURE
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'real_estate'
          AND table_name = 'visite'
          AND column_name = 'id_visite'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.visite.id_visite missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'real_estate'
          AND table_name = 'visite'
          AND column_name = 'id_presentation'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.visite.id_presentation missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'real_estate'
          AND table_name = 'visite'
          AND column_name = 'date_visite'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.visite.date_visite missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'real_estate'
          AND table_name = 'visite'
          AND column_name = 'statut'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.visite.statut missing';
    END IF;

    RAISE NOTICE 'PASS: real_estate.visite structure validated';
END
$$;


-- =============================================================================
-- 8. AUDIT_LOG STRUCTURE
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'real_estate'
          AND table_name = 'audit_log'
          AND column_name = 'id_audit'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.audit_log.id_audit missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'real_estate'
          AND table_name = 'audit_log'
          AND column_name = 'date_evenement'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.audit_log.date_evenement missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'real_estate'
          AND table_name = 'audit_log'
          AND column_name = 'table_name'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.audit_log.table_name missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'real_estate'
          AND table_name = 'audit_log'
          AND column_name = 'operation'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.audit_log.operation missing';
    END IF;

    RAISE NOTICE 'PASS: real_estate.audit_log structure validated';
END
$$;


-- =============================================================================
-- 9. MIGRATION 004 CONSTRAINTS
-- =============================================================================

DO $$
DECLARE
    constraint_name TEXT;
    expected_constraints TEXT[] := ARRAY[
        'fk_visite_presentation',
        'ck_visite_statut',
        'ck_visite_note',
        'ck_visite_photos_array',
        'ck_audit_log_operation',
        'ck_audit_log_contexte_object'
    ];
BEGIN
    FOREACH constraint_name IN ARRAY expected_constraints
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t
              ON t.oid = c.conrelid
            JOIN pg_namespace n
              ON n.oid = t.relnamespace
            WHERE n.nspname = 'real_estate'
              AND c.conname = constraint_name
        ) THEN
            RAISE EXCEPTION
                'TEST FAILED: migration 004 constraint % does not exist',
                constraint_name;
        END IF;
    END LOOP;

    RAISE NOTICE 'PASS: migration 004 constraints validated';
END
$$;


-- =============================================================================
-- 10. MIGRATION 004 INDEXES
-- =============================================================================

DO $$
DECLARE
    index_name TEXT;
    expected_indexes TEXT[] := ARRAY[
        'idx_visite_id_presentation',
        'idx_visite_date',
        'idx_audit_log_date_evenement',
        'idx_audit_log_table_name',
        'idx_audit_log_record'
    ];
BEGIN
    FOREACH index_name IN ARRAY expected_indexes
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_indexes
            WHERE schemaname = 'real_estate'
              AND indexname = index_name
        ) THEN
            RAISE EXCEPTION
                'TEST FAILED: expected index % does not exist',
                index_name;
        END IF;
    END LOOP;

    RAISE NOTICE 'PASS: migration 004 indexes validated';
END
$$;


-- =============================================================================
-- FINAL RESULT
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'PASS: real_estate schema structure validated successfully';
    RAISE NOTICE 'PASS: 16 OLTP business tables validated';
    RAISE NOTICE 'PASS: visite and audit_log validated';
    RAISE NOTICE '============================================================';
END
$$;