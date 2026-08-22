-- =============================================================================
-- 002_legacy_migration.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate migration 002 from Fil_Rouge_Depart to real_estate.
--
-- This test is READ-ONLY.
-- =============================================================================

\set ON_ERROR_STOP on


-- =============================================================================
-- 1. MIGRATION VERSION
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM migration_control.schema_version
        WHERE version = '002'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: migration 002 is not registered';
    END IF;

    RAISE NOTICE 'PASS: migration 002 is registered';
END
$$;


-- =============================================================================
-- 2. CLIENT COUNT
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM real_estate.client;

    IF actual_count <> 18 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 18 clients, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: 18 clients migrated';
END
$$;


-- =============================================================================
-- 3. CHASSEUR COUNT
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM real_estate.chasseur;

    IF actual_count <> 6 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 6 chasseurs, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: 6 chasseurs migrated';
END
$$;


-- =============================================================================
-- 4. SECTEUR COUNT
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM real_estate.secteur;

    IF actual_count <> 10 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 10 secteurs, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: 10 secteurs migrated';
END
$$;


-- =============================================================================
-- 5. MANDAT COUNT
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM real_estate.mandat
    WHERE reference_mandat LIKE 'LEGACY-MANDAT-%';

    IF actual_count <> 17 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 17 migrated mandates, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: 17 valid mandates migrated';
END
$$;


-- =============================================================================
-- 6. INVALID LEGACY MANDATE REJECTED
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM migration_control.legacy_rejection
    WHERE migration_version = '002'
      AND source_schema = 'Fil_Rouge_Depart'
      AND source_table = 'mandats'
      AND source_id = 13
      AND rejection_code = 'INVALID_CLIENT_ROLE';

    IF actual_count <> 1 THEN
        RAISE EXCEPTION
            'TEST FAILED: legacy mandate 13 rejection not found';
    END IF;

    RAISE NOTICE 'PASS: invalid legacy mandate 13 was rejected';
END
$$;


-- =============================================================================
-- 7. INVALID MANDATE MUST NOT EXIST IN TARGET
-- =============================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM real_estate.mandat
        WHERE reference_mandat = 'LEGACY-MANDAT-13'
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: invalid mandate 13 exists in target';
    END IF;

    RAISE NOTICE 'PASS: invalid mandate 13 is absent from target';
END
$$;


-- =============================================================================
-- 8. DEMANDES
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM real_estate.demande
    WHERE reference_demande LIKE 'LEGACY-DEMANDE-%';

    IF actual_count <> 17 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 17 demandes, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: 17 demandes created';
END
$$;


-- =============================================================================
-- 9. INITIAL DEMANDE VERSIONS
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM real_estate.demande_version
    WHERE numero_version = 1
      AND motif_modification = 'Migration depuis le SI hérité'
      AND auteur_systeme = TRUE
      AND active = TRUE;

    IF actual_count <> 17 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 17 initial demande versions, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: 17 initial demande versions created';
END
$$;


-- =============================================================================
-- 10. LEGACY SEARCH TEXT PRESERVED
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM real_estate.demande_version
    WHERE motif_modification = 'Migration depuis le SI hérité'
      AND description_recherche_legacy IS NOT NULL;

    IF actual_count <> 17 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 17 preserved legacy descriptions, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: all legacy search descriptions preserved';
END
$$;


-- =============================================================================
-- 11. COMMISSION SCALES
-- =============================================================================

DO $$
DECLARE
    actual_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM real_estate.bareme_commission;

    IF actual_count <> 6 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 6 commission scales, found %',
            actual_count;
    END IF;

    RAISE NOTICE 'PASS: 6 commission scales created';
END
$$;


-- =============================================================================
-- 12. COMMISSION PERCENTAGE CONVERSION
--
-- Legacy:
--   2.50 = 2.50 %
--
-- Target:
--   0.0250
-- =============================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM "Fil_Rouge_Depart".utilisateurs legacy
        JOIN real_estate.chasseur chasseur
          ON chasseur.email = legacy.email
        JOIN real_estate.bareme_commission bareme
          ON bareme.id_chasseur = chasseur.id_chasseur
        WHERE legacy.role = 'chasseur'
          AND legacy.taux_commission IS NOT NULL
          AND bareme.taux_commission
              <> (legacy.taux_commission / 100.0)::numeric(7,4)
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: commission percentage conversion mismatch';
    END IF;

    RAISE NOTICE 'PASS: commission percentages converted to ratios';
END
$$;


-- =============================================================================
-- 13. MANDAT RELATIONAL INTEGRITY
-- =============================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM real_estate.mandat m
        LEFT JOIN real_estate.client c
          ON c.id_client = m.id_client
        LEFT JOIN real_estate.chasseur h
          ON h.id_chasseur = m.id_chasseur
        WHERE c.id_client IS NULL
           OR h.id_chasseur IS NULL
    ) THEN
        RAISE EXCEPTION
            'TEST FAILED: migrated mandate has invalid client/chasseur relation';
    END IF;

    RAISE NOTICE 'PASS: migrated mandate relationships are valid';
END
$$;


-- =============================================================================
-- FINAL RESULT
-- =============================================================================

SELECT
    'PASS' AS status,
    'Legacy migration 002 validated successfully' AS result;