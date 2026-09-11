-- =============================================================================
-- 010_demande_affectation.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate the DEMANDE_AFFECTATION model introduced by migration 007.
--
-- Scope:
--   - table and migration presence;
--   - legacy backfill reconciliation;
--   - allowed status lifecycle;
--   - foreign-key integrity;
--   - current-assignment uniqueness;
--   - refusal history;
--   - decision timestamp rules;
--   - refusal-reason rules.
--
-- Test discipline:
--   - read-only validations run against existing migrated data;
--   - behavioral tests use temporary rows inside a transaction;
--   - all temporary rows are rolled back at the end.
-- =============================================================================

\set ON_ERROR_STOP on


-- =============================================================================
-- 0. MIGRATION 007 IS REGISTERED
-- =============================================================================

DO $$
DECLARE
    v_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM migration_control.schema_version
    WHERE version = '007';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'TEST FAILED: migration 007 registration count is %, expected 1',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: migration 007 is registered exactly once';
END
$$;


-- =============================================================================
-- 1. DEMANDE_AFFECTATION TABLE EXISTS
-- =============================================================================

DO $$
BEGIN
    IF to_regclass('real_estate.demande_affectation') IS NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: real_estate.demande_affectation does not exist';
    END IF;

    RAISE NOTICE
        'PASS: real_estate.demande_affectation exists';
END
$$;


-- =============================================================================
-- 2. LEGACY DEMANDES HAVE ONE ACCEPTED ASSIGNMENT
-- =============================================================================

DO $$
DECLARE
    v_legacy BIGINT;
    v_accepted BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_legacy
    FROM real_estate.demande
    WHERE origine = 'LEGACY';

    SELECT COUNT(*)
    INTO v_accepted
    FROM real_estate.demande d
    JOIN real_estate.demande_affectation da
      ON da.id_demande = d.id_demande
     AND da.statut = 'ACCEPTEE'
    WHERE d.origine = 'LEGACY';

    IF v_legacy <> v_accepted THEN
        RAISE EXCEPTION
            'TEST FAILED: expected % accepted legacy assignments, found %',
            v_legacy,
            v_accepted;
    END IF;

    RAISE NOTICE
        'PASS: all legacy demandes have one accepted assignment';
END
$$;


-- =============================================================================
-- 3. LEGACY ASSIGNMENT HUNTER MATCHES MANDATE HUNTER
-- =============================================================================

DO $$
DECLARE
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.demande_affectation da
    JOIN real_estate.demande d
      ON d.id_demande = da.id_demande
    JOIN real_estate.mandat m
      ON m.id_mandat = d.id_mandat
    WHERE d.origine = 'LEGACY'
      AND da.statut = 'ACCEPTEE'
      AND da.id_chasseur <> m.id_chasseur;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'TEST FAILED: % legacy assignments disagree with mandate hunter',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: legacy assignment hunter matches mandate hunter';
END
$$;


-- =============================================================================
-- 4. NO DEMANDE HAS MULTIPLE CURRENT ASSIGNMENTS
-- =============================================================================

DO $$
DECLARE
    v_duplicates BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_duplicates
    FROM (
        SELECT id_demande
        FROM real_estate.demande_affectation
        WHERE statut IN ('ASSIGNEE', 'ACCEPTEE')
        GROUP BY id_demande
        HAVING COUNT(*) > 1
    ) duplicate_rows;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'TEST FAILED: % demandes have multiple current assignments',
            v_duplicates;
    END IF;

    RAISE NOTICE
        'PASS: no demande has multiple current assignments';
END
$$;


-- =============================================================================
-- BEHAVIORAL TEST DATA
--
-- The remaining tests create isolated temporary business rows and are rolled
-- back at the end.
-- =============================================================================

BEGIN;

CREATE TEMP TABLE test_affectation_context (
    key   TEXT PRIMARY KEY,
    value BIGINT NOT NULL
) ON COMMIT DROP;


-- =============================================================================
-- 5. CREATE ISOLATED CLIENT
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.client (
        nom,
        prenom,
        email,
        telephone,
        statut,
        consentement_contact
    )
    VALUES (
        'TEST-AFFECTATION',
        'Client',
        'test.affectation.client@example.invalid',
        NULL,
        'ACTIF',
        FALSE
    )
    RETURNING id_client
)
INSERT INTO test_affectation_context (key, value)
SELECT 'client_id', id_client
FROM inserted;


-- =============================================================================
-- 6. CREATE TWO ISOLATED HUNTERS
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.chasseur (
        nom,
        prenom,
        email,
        telephone,
        date_entree,
        statut
    )
    VALUES (
        'TEST-AFFECTATION',
        'Hunter-A',
        'test.affectation.hunter.a@example.invalid',
        NULL,
        CURRENT_DATE,
        'ACTIF'
    )
    RETURNING id_chasseur
)
INSERT INTO test_affectation_context (key, value)
SELECT 'chasseur_a_id', id_chasseur
FROM inserted;


WITH inserted AS (
    INSERT INTO real_estate.chasseur (
        nom,
        prenom,
        email,
        telephone,
        date_entree,
        statut
    )
    VALUES (
        'TEST-AFFECTATION',
        'Hunter-B',
        'test.affectation.hunter.b@example.invalid',
        NULL,
        CURRENT_DATE,
        'ACTIF'
    )
    RETURNING id_chasseur
)
INSERT INTO test_affectation_context (key, value)
SELECT 'chasseur_b_id', id_chasseur
FROM inserted;


-- =============================================================================
-- 7. CREATE PRE-MANDATE DEMANDE
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.demande (
        reference_demande,
        statut,
        id_mandat,
        origine
    )
    VALUES (
        'TEST-AFFECTATION-001',
        'ACTIVE',
        NULL,
        'API'
    )
    RETURNING id_demande
)
INSERT INTO test_affectation_context (key, value)
SELECT 'demande_id', id_demande
FROM inserted;


-- =============================================================================
-- 8. PENDING ASSIGNMENT IS ACCEPTED
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
    v_chasseur_a BIGINT;
    v_affectation_id BIGINT;
BEGIN
    SELECT value INTO v_demande_id
    FROM test_affectation_context
    WHERE key = 'demande_id';

    SELECT value INTO v_chasseur_a
    FROM test_affectation_context
    WHERE key = 'chasseur_a_id';

    INSERT INTO real_estate.demande_affectation (
        id_demande,
        id_chasseur,
        statut
    )
    VALUES (
        v_demande_id,
        v_chasseur_a,
        'ASSIGNEE'
    )
    RETURNING id_affectation
    INTO v_affectation_id;

    INSERT INTO test_affectation_context (key, value)
    VALUES ('affectation_a_id', v_affectation_id);

    RAISE NOTICE
        'PASS: pending assignment created successfully';
END
$$;


-- =============================================================================
-- 9. SECOND CURRENT ASSIGNMENT MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
    v_chasseur_b BIGINT;
BEGIN
    SELECT value INTO v_demande_id
    FROM test_affectation_context
    WHERE key = 'demande_id';

    SELECT value INTO v_chasseur_b
    FROM test_affectation_context
    WHERE key = 'chasseur_b_id';

    BEGIN
        INSERT INTO real_estate.demande_affectation (
            id_demande,
            id_chasseur,
            statut
        )
        VALUES (
            v_demande_id,
            v_chasseur_b,
            'ASSIGNEE'
        );

        RAISE EXCEPTION
            'TEST FAILED: second current assignment was accepted';

    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'PASS: second current assignment rejected';
    END;
END
$$;


-- =============================================================================
-- 10. PENDING ASSIGNMENT CANNOT HAVE DECISION TIMESTAMP
-- =============================================================================

DO $$
DECLARE
    v_affectation_id BIGINT;
BEGIN
    SELECT value INTO v_affectation_id
    FROM test_affectation_context
    WHERE key = 'affectation_a_id';

    BEGIN
        UPDATE real_estate.demande_affectation
        SET date_decision = CURRENT_TIMESTAMP
        WHERE id_affectation = v_affectation_id;

        RAISE EXCEPTION
            'TEST FAILED: pending assignment with decision timestamp was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: pending assignment with decision timestamp rejected';
    END;
END
$$;


-- =============================================================================
-- 11. ACCEPTED ASSIGNMENT REQUIRES DECISION TIMESTAMP
-- =============================================================================

DO $$
DECLARE
    v_affectation_id BIGINT;
BEGIN
    SELECT value INTO v_affectation_id
    FROM test_affectation_context
    WHERE key = 'affectation_a_id';

    BEGIN
        UPDATE real_estate.demande_affectation
        SET statut = 'ACCEPTEE'
        WHERE id_affectation = v_affectation_id;

        RAISE EXCEPTION
            'TEST FAILED: accepted assignment without decision timestamp was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: accepted assignment without decision timestamp rejected';
    END;
END
$$;


-- =============================================================================
-- 12. REFUSE FIRST ASSIGNMENT
-- =============================================================================

DO $$
DECLARE
    v_affectation_id BIGINT;
BEGIN
    SELECT value INTO v_affectation_id
    FROM test_affectation_context
    WHERE key = 'affectation_a_id';

    UPDATE real_estate.demande_affectation
    SET
        statut = 'REFUSEE',
        date_decision = CURRENT_TIMESTAMP,
        motif_refus = 'TEST refusal'
    WHERE id_affectation = v_affectation_id;

    RAISE NOTICE
        'PASS: assignment refusal persisted';
END
$$;


-- =============================================================================
-- 13. NEW ASSIGNMENT AFTER REFUSAL IS ACCEPTED
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
    v_chasseur_b BIGINT;
    v_affectation_id BIGINT;
BEGIN
    SELECT value INTO v_demande_id
    FROM test_affectation_context
    WHERE key = 'demande_id';

    SELECT value INTO v_chasseur_b
    FROM test_affectation_context
    WHERE key = 'chasseur_b_id';

    INSERT INTO real_estate.demande_affectation (
        id_demande,
        id_chasseur,
        statut
    )
    VALUES (
        v_demande_id,
        v_chasseur_b,
        'ASSIGNEE'
    )
    RETURNING id_affectation
    INTO v_affectation_id;

    INSERT INTO test_affectation_context (key, value)
    VALUES ('affectation_b_id', v_affectation_id);

    RAISE NOTICE
        'PASS: reassignment after refusal created successfully';
END
$$;


-- =============================================================================
-- 14. ACCEPT SECOND ASSIGNMENT
-- =============================================================================

DO $$
DECLARE
    v_affectation_id BIGINT;
BEGIN
    SELECT value INTO v_affectation_id
    FROM test_affectation_context
    WHERE key = 'affectation_b_id';

    UPDATE real_estate.demande_affectation
    SET
        statut = 'ACCEPTEE',
        date_decision = CURRENT_TIMESTAMP
    WHERE id_affectation = v_affectation_id;

    RAISE NOTICE
        'PASS: assignment acceptance persisted';
END
$$;


-- =============================================================================
-- 15. NEW PENDING ASSIGNMENT AFTER ACCEPTANCE MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
    v_chasseur_a BIGINT;
BEGIN
    SELECT value INTO v_demande_id
    FROM test_affectation_context
    WHERE key = 'demande_id';

    SELECT value INTO v_chasseur_a
    FROM test_affectation_context
    WHERE key = 'chasseur_a_id';

    BEGIN
        INSERT INTO real_estate.demande_affectation (
            id_demande,
            id_chasseur,
            statut
        )
        VALUES (
            v_demande_id,
            v_chasseur_a,
            'ASSIGNEE'
        );

        RAISE EXCEPTION
            'TEST FAILED: pending assignment after acceptance was accepted';

    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'PASS: pending assignment after acceptance rejected';
    END;
END
$$;


-- =============================================================================
-- 16. INVALID STATUS MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_affectation_id BIGINT;
BEGIN
    SELECT value INTO v_affectation_id
    FROM test_affectation_context
    WHERE key = 'affectation_b_id';

    BEGIN
        UPDATE real_estate.demande_affectation
        SET statut = 'INCONNU'
        WHERE id_affectation = v_affectation_id;

        RAISE EXCEPTION
            'TEST FAILED: invalid assignment status was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: invalid assignment status rejected';
    END;
END
$$;


-- =============================================================================
-- 17. REFUSAL REASON ON NON-REFUSED ASSIGNMENT MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_affectation_id BIGINT;
BEGIN
    SELECT value INTO v_affectation_id
    FROM test_affectation_context
    WHERE key = 'affectation_b_id';

    BEGIN
        UPDATE real_estate.demande_affectation
        SET motif_refus = 'Invalid refusal reason'
        WHERE id_affectation = v_affectation_id;

        RAISE EXCEPTION
            'TEST FAILED: refusal reason on accepted assignment was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: refusal reason on non-refused assignment rejected';
    END;
END
$$;


-- =============================================================================
-- 18. INVALID DEMANDE FOREIGN KEY MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_chasseur_a BIGINT;
BEGIN
    SELECT value INTO v_chasseur_a
    FROM test_affectation_context
    WHERE key = 'chasseur_a_id';

    BEGIN
        INSERT INTO real_estate.demande_affectation (
            id_demande,
            id_chasseur,
            statut
        )
        VALUES (
            999999999999,
            v_chasseur_a,
            'ASSIGNEE'
        );

        RAISE EXCEPTION
            'TEST FAILED: invalid demande foreign key was accepted';

    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE
                'PASS: invalid demande foreign key rejected';
    END;
END
$$;


-- =============================================================================
-- 19. INVALID CHASSEUR FOREIGN KEY MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
BEGIN
    INSERT INTO real_estate.demande (
        reference_demande,
        statut,
        id_mandat,
        origine
    )
    VALUES (
        'TEST-AFFECTATION-FK-CHASSEUR',
        'ACTIVE',
        NULL,
        'API'
    )
    RETURNING id_demande
    INTO v_demande_id;

    BEGIN
        INSERT INTO real_estate.demande_affectation (
            id_demande,
            id_chasseur,
            statut
        )
        VALUES (
            v_demande_id,
            999999999999,
            'ASSIGNEE'
        );

        RAISE EXCEPTION
            'TEST FAILED: invalid chasseur foreign key was accepted';

    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE
                'PASS: invalid chasseur foreign key rejected';
    END;
END
$$;


-- =============================================================================
-- 20. DECISION DATE BEFORE ASSIGNMENT DATE MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
    v_chasseur_a BIGINT;
BEGIN
    SELECT value INTO v_chasseur_a
    FROM test_affectation_context
    WHERE key = 'chasseur_a_id';

    INSERT INTO real_estate.demande (
        reference_demande,
        statut,
        id_mandat,
        origine
    )
    VALUES (
        'TEST-AFFECTATION-DATE-CHECK',
        'ACTIVE',
        NULL,
        'API'
    )
    RETURNING id_demande
    INTO v_demande_id;

    BEGIN
        INSERT INTO real_estate.demande_affectation (
            id_demande,
            id_chasseur,
            statut,
            date_affectation,
            date_decision
        )
        VALUES (
            v_demande_id,
            v_chasseur_a,
            'REFUSEE',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP - INTERVAL '1 day'
        );

        RAISE EXCEPTION
            'TEST FAILED: decision date before assignment date was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: decision date before assignment date rejected';
    END;
END
$$;


-- =============================================================================
-- 21. REFUSAL HISTORY IS PRESERVED
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
    v_refused BIGINT;
    v_accepted BIGINT;
BEGIN
    SELECT value INTO v_demande_id
    FROM test_affectation_context
    WHERE key = 'demande_id';

    SELECT COUNT(*)
    INTO v_refused
    FROM real_estate.demande_affectation
    WHERE id_demande = v_demande_id
      AND statut = 'REFUSEE';

    SELECT COUNT(*)
    INTO v_accepted
    FROM real_estate.demande_affectation
    WHERE id_demande = v_demande_id
      AND statut = 'ACCEPTEE';

    IF v_refused <> 1 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 1 refused historical assignment, found %',
            v_refused;
    END IF;

    IF v_accepted <> 1 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 1 accepted current assignment, found %',
            v_accepted;
    END IF;

    RAISE NOTICE
        'PASS: refusal history preserved alongside accepted owner';
END
$$;


-- =============================================================================
-- FINAL RESULT
-- =============================================================================

SELECT
    'PASS' AS status,
    'Demande assignment constraints and lifecycle validated successfully' AS result;


-- =============================================================================
-- CLEANUP
--
-- All behavioral test rows are rolled back.
-- Existing migrated data remains untouched.
-- =============================================================================

ROLLBACK;
