-- =============================================================================
-- 004_visite_audit.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate the schema objects introduced by:
--   database/migrations/004_add_visite_audit.sql
--
-- Scope:
--   - real_estate.visite
--   - real_estate.audit_log
--
-- This test script validates:
--   - table existence
--   - required columns
--   - foreign keys
--   - check constraints
--   - indexes
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. TABLE EXISTENCE
-- =============================================================================

DO $$
BEGIN
    IF to_regclass('real_estate.visite') IS NULL THEN
        RAISE EXCEPTION 'Missing table: real_estate.visite';
    END IF;

    IF to_regclass('real_estate.audit_log') IS NULL THEN
        RAISE EXCEPTION 'Missing table: real_estate.audit_log';
    END IF;
END
$$;


-- =============================================================================
-- 2. VISITE REQUIRED COLUMNS
-- =============================================================================

DO $$
DECLARE
    missing_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO missing_count
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
    ) AS required(column_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM information_schema.columns c
        WHERE c.table_schema = 'real_estate'
          AND c.table_name = 'visite'
          AND c.column_name = required.column_name
    );

    IF missing_count > 0 THEN
        RAISE EXCEPTION
            'real_estate.visite is missing % required column(s)',
            missing_count;
    END IF;
END
$$;


-- =============================================================================
-- 3. AUDIT_LOG REQUIRED COLUMNS
-- =============================================================================

DO $$
DECLARE
    missing_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO missing_count
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
    ) AS required(column_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM information_schema.columns c
        WHERE c.table_schema = 'real_estate'
          AND c.table_name = 'audit_log'
          AND c.column_name = required.column_name
    );

    IF missing_count > 0 THEN
        RAISE EXCEPTION
            'real_estate.audit_log is missing % required column(s)',
            missing_count;
    END IF;
END
$$;


-- =============================================================================
-- 4. VISITE FOREIGN KEY
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_class t
          ON t.oid = c.conrelid
        JOIN pg_namespace n
          ON n.oid = t.relnamespace
        WHERE n.nspname = 'real_estate'
          AND t.relname = 'visite'
          AND c.contype = 'f'
          AND c.conname = 'fk_visite_presentation'
    ) THEN
        RAISE EXCEPTION
            'Missing foreign key: fk_visite_presentation';
    END IF;
END
$$;


-- =============================================================================
-- 5. VISITE CHECK CONSTRAINTS
-- =============================================================================

DO $$
DECLARE
    constraint_name TEXT;
BEGIN
    FOREACH constraint_name IN ARRAY ARRAY[
        'ck_visite_statut',
        'ck_visite_note',
        'ck_visite_photos_array'
    ]
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t
              ON t.oid = c.conrelid
            JOIN pg_namespace n
              ON n.oid = t.relnamespace
            WHERE n.nspname = 'real_estate'
              AND t.relname = 'visite'
              AND c.conname = constraint_name
        ) THEN
            RAISE EXCEPTION
                'Missing VISITE constraint: %',
                constraint_name;
        END IF;
    END LOOP;
END
$$;


-- =============================================================================
-- 6. AUDIT_LOG CHECK CONSTRAINTS
-- =============================================================================

DO $$
DECLARE
    constraint_name TEXT;
BEGIN
    FOREACH constraint_name IN ARRAY ARRAY[
        'ck_audit_log_operation',
        'ck_audit_log_contexte_object'
    ]
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t
              ON t.oid = c.conrelid
            JOIN pg_namespace n
              ON n.oid = t.relnamespace
            WHERE n.nspname = 'real_estate'
              AND t.relname = 'audit_log'
              AND c.conname = constraint_name
        ) THEN
            RAISE EXCEPTION
                'Missing AUDIT_LOG constraint: %',
                constraint_name;
        END IF;
    END LOOP;
END
$$;


-- =============================================================================
-- 7. REQUIRED INDEXES
-- =============================================================================

DO $$
DECLARE
    index_name TEXT;
BEGIN
    FOREACH index_name IN ARRAY ARRAY[
        'idx_visite_id_presentation',
        'idx_visite_date',
        'idx_audit_log_date_evenement',
        'idx_audit_log_table_name',
        'idx_audit_log_record'
    ]
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_indexes
            WHERE schemaname = 'real_estate'
              AND indexname = index_name
        ) THEN
            RAISE EXCEPTION
                'Missing index: %',
                index_name;
        END IF;
    END LOOP;
END
$$;


-- =============================================================================
-- 8. BASIC CONSTRAINT BEHAVIOUR
-- =============================================================================

DO $$
BEGIN
    BEGIN
        INSERT INTO real_estate.visite (
            date_visite,
            statut,
            note,
            photos,
            id_presentation
        )
        VALUES (
            CURRENT_TIMESTAMP,
            'INVALID_STATUS',
            3,
            '[]'::jsonb,
            -1
        );

        RAISE EXCEPTION
            'VISITE invalid status constraint was not enforced';

    EXCEPTION
        WHEN check_violation THEN
            NULL;
    END;
END
$$;


DO $$
BEGIN
    BEGIN
        INSERT INTO real_estate.audit_log (
            table_name,
            operation
        )
        VALUES (
            'test',
            'INVALID'
        );

        RAISE EXCEPTION
            'AUDIT_LOG invalid operation constraint was not enforced';

    EXCEPTION
        WHEN check_violation THEN
            NULL;
    END;
END
$$;


ROLLBACK;