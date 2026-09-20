-- =============================================================================
-- Test 017
-- Validate migration 014: versioned commercial offer workflow
--
-- Expectations:
--   - migration 014 is registered exactly once;
--   - real_estate.offre exists with the expected physical structure;
--   - every offer belongs to an existing presentation;
--   - offer versions are positive and unique within one presentation;
--   - offer amounts are strictly positive;
--   - only supported business statuses are accepted;
--   - expiration must occur after the offer date;
--   - SOUMISE and EXPIREE offers have no decision timestamp;
--   - ACCEPTEE / REFUSEE / RETIREE / REVISEE require a decision timestamp;
--   - at most one accepted offer exists per presentation;
--   - valid historical revisions can coexist;
--   - no persistent business test data is created.
--
-- Mutation tests run inside a transaction that is rolled back at the end.
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;


-- =============================================================================
-- 1. Migration registry
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM migration_control.schema_version
    WHERE version = '014';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: expected migration_control version 014 exactly once, found %',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: migration 014 registered exactly once';
END;
$$;


-- =============================================================================
-- 2. OFFRE table exists
-- =============================================================================

DO $$
BEGIN
    IF to_regclass('real_estate.offre') IS NULL THEN
        RAISE EXCEPTION
            'FAIL: real_estate.offre does not exist';
    END IF;

    RAISE NOTICE
        'PASS: real_estate.offre exists';
END;
$$;


-- =============================================================================
-- 3. Expected columns exist
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM information_schema.columns
    WHERE table_schema = 'real_estate'
      AND table_name = 'offre'
      AND column_name IN (
          'id_offre',
          'id_presentation',
          'numero_version',
          'montant',
          'date_offre',
          'date_expiration',
          'date_decision',
          'statut',
          'commentaire',
          'date_creation'
      );

    IF v_count <> 10 THEN
        RAISE EXCEPTION
            'FAIL: expected 10 OFFRE columns, found %',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: OFFRE contains the expected 10 columns';
END;
$$;


-- =============================================================================
-- 4. Required constraints exist
-- =============================================================================

DO $$
DECLARE
    v_pk INTEGER;
    v_fk INTEGER;
    v_unique INTEGER;
    v_version_check INTEGER;
    v_amount_check INTEGER;
    v_status_check INTEGER;
    v_expiration_check INTEGER;
    v_decision_check INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_pk
    FROM pg_constraint
    WHERE conrelid = 'real_estate.offre'::regclass
      AND conname = 'pk_offre'
      AND contype = 'p';

    SELECT COUNT(*)
    INTO v_fk
    FROM pg_constraint
    WHERE conrelid = 'real_estate.offre'::regclass
      AND conname = 'fk_offre_presentation'
      AND contype = 'f';

    SELECT COUNT(*)
    INTO v_unique
    FROM pg_constraint
    WHERE conrelid = 'real_estate.offre'::regclass
      AND conname = 'uq_offre_presentation_version'
      AND contype = 'u';

    SELECT COUNT(*)
    INTO v_version_check
    FROM pg_constraint
    WHERE conrelid = 'real_estate.offre'::regclass
      AND conname = 'ck_offre_numero_version'
      AND contype = 'c';

    SELECT COUNT(*)
    INTO v_amount_check
    FROM pg_constraint
    WHERE conrelid = 'real_estate.offre'::regclass
      AND conname = 'ck_offre_montant'
      AND contype = 'c';

    SELECT COUNT(*)
    INTO v_status_check
    FROM pg_constraint
    WHERE conrelid = 'real_estate.offre'::regclass
      AND conname = 'ck_offre_statut'
      AND contype = 'c';

    SELECT COUNT(*)
    INTO v_expiration_check
    FROM pg_constraint
    WHERE conrelid = 'real_estate.offre'::regclass
      AND conname = 'ck_offre_expiration'
      AND contype = 'c';

    SELECT COUNT(*)
    INTO v_decision_check
    FROM pg_constraint
    WHERE conrelid = 'real_estate.offre'::regclass
      AND conname = 'ck_offre_decision'
      AND contype = 'c';

    IF v_pk <> 1 THEN
        RAISE EXCEPTION 'FAIL: pk_offre missing';
    END IF;

    IF v_fk <> 1 THEN
        RAISE EXCEPTION 'FAIL: fk_offre_presentation missing';
    END IF;

    IF v_unique <> 1 THEN
        RAISE EXCEPTION
            'FAIL: uq_offre_presentation_version missing';
    END IF;

    IF v_version_check <> 1 THEN
        RAISE EXCEPTION
            'FAIL: ck_offre_numero_version missing';
    END IF;

    IF v_amount_check <> 1 THEN
        RAISE EXCEPTION
            'FAIL: ck_offre_montant missing';
    END IF;

    IF v_status_check <> 1 THEN
        RAISE EXCEPTION
            'FAIL: ck_offre_statut missing';
    END IF;

    IF v_expiration_check <> 1 THEN
        RAISE EXCEPTION
            'FAIL: ck_offre_expiration missing';
    END IF;

    IF v_decision_check <> 1 THEN
        RAISE EXCEPTION
            'FAIL: ck_offre_decision missing';
    END IF;

    RAISE NOTICE
        'PASS: OFFRE PK, FK, UNIQUE and CHECK constraints exist';
END;
$$;


-- =============================================================================
-- 5. Required indexes exist
-- =============================================================================

DO $$
DECLARE
    v_presentation INTEGER;
    v_status INTEGER;
    v_date INTEGER;
    v_accepted INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_presentation
    FROM pg_indexes
    WHERE schemaname = 'real_estate'
      AND tablename = 'offre'
      AND indexname = 'idx_offre_presentation';

    SELECT COUNT(*)
    INTO v_status
    FROM pg_indexes
    WHERE schemaname = 'real_estate'
      AND tablename = 'offre'
      AND indexname = 'idx_offre_statut';

    SELECT COUNT(*)
    INTO v_date
    FROM pg_indexes
    WHERE schemaname = 'real_estate'
      AND tablename = 'offre'
      AND indexname = 'idx_offre_date_offre';

    SELECT COUNT(*)
    INTO v_accepted
    FROM pg_indexes
    WHERE schemaname = 'real_estate'
      AND tablename = 'offre'
      AND indexname = 'uq_offre_presentation_acceptee';

    IF v_presentation <> 1 THEN
        RAISE EXCEPTION
            'FAIL: idx_offre_presentation missing';
    END IF;

    IF v_status <> 1 THEN
        RAISE EXCEPTION
            'FAIL: idx_offre_statut missing';
    END IF;

    IF v_date <> 1 THEN
        RAISE EXCEPTION
            'FAIL: idx_offre_date_offre missing';
    END IF;

    IF v_accepted <> 1 THEN
        RAISE EXCEPTION
            'FAIL: uq_offre_presentation_acceptee missing';
    END IF;

    RAISE NOTICE
        'PASS: required OFFRE indexes exist';
END;
$$;


-- =============================================================================
-- 6. Test fixture
--
-- Reuse an existing presentation. All OFFRE rows created below are rolled
-- back at the end of this test file.
-- =============================================================================

CREATE TEMP TABLE test_offre_context (
    id_presentation BIGINT NOT NULL
) ON COMMIT DROP;


INSERT INTO test_offre_context (
    id_presentation
)
SELECT id_presentation
FROM real_estate.presentation
ORDER BY id_presentation
LIMIT 1;


DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM test_offre_context;

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: no presentation available for OFFRE tests';
    END IF;

    RAISE NOTICE
        'PASS: existing presentation selected as OFFRE test fixture';
END;
$$;


-- =============================================================================
-- 7. Valid SOUMISE offer must be accepted
-- =============================================================================

INSERT INTO real_estate.offre (
    id_presentation,
    numero_version,
    montant,
    date_offre,
    date_expiration,
    statut
)
SELECT
    id_presentation,
    900001,
    250000.00,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '7 days',
    'SOUMISE'
FROM test_offre_context;


DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.offre o
    JOIN test_offre_context t
      ON t.id_presentation = o.id_presentation
    WHERE o.numero_version = 900001
      AND o.montant = 250000.00
      AND o.statut = 'SOUMISE'
      AND o.date_decision IS NULL;

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: valid SOUMISE offer was not persisted';
    END IF;

    RAISE NOTICE
        'PASS: valid SOUMISE offer accepted';
END;
$$;


-- =============================================================================
-- 8. Duplicate version must be rejected
-- =============================================================================

DO $$
DECLARE
    v_presentation BIGINT;
BEGIN
    SELECT id_presentation
    INTO v_presentation
    FROM test_offre_context;

    BEGIN
        INSERT INTO real_estate.offre (
            id_presentation,
            numero_version,
            montant,
            statut
        )
        VALUES (
            v_presentation,
            900001,
            260000.00,
            'SOUMISE'
        );

        RAISE EXCEPTION
            'FAIL: duplicate offer version was accepted';

    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'PASS: duplicate offer version rejected';
    END;
END;
$$;


-- =============================================================================
-- 9. Non-positive version must be rejected
-- =============================================================================

DO $$
DECLARE
    v_presentation BIGINT;
BEGIN
    SELECT id_presentation
    INTO v_presentation
    FROM test_offre_context;

    BEGIN
        INSERT INTO real_estate.offre (
            id_presentation,
            numero_version,
            montant,
            statut
        )
        VALUES (
            v_presentation,
            0,
            250000.00,
            'SOUMISE'
        );

        RAISE EXCEPTION
            'FAIL: non-positive offer version was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: non-positive offer version rejected';
    END;
END;
$$;


-- =============================================================================
-- 10. Non-positive amount must be rejected
-- =============================================================================

DO $$
DECLARE
    v_presentation BIGINT;
BEGIN
    SELECT id_presentation
    INTO v_presentation
    FROM test_offre_context;

    BEGIN
        INSERT INTO real_estate.offre (
            id_presentation,
            numero_version,
            montant,
            statut
        )
        VALUES (
            v_presentation,
            900002,
            0,
            'SOUMISE'
        );

        RAISE EXCEPTION
            'FAIL: non-positive offer amount was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: non-positive offer amount rejected';
    END;
END;
$$;


-- =============================================================================
-- 11. Unsupported status must be rejected
-- =============================================================================

DO $$
DECLARE
    v_presentation BIGINT;
BEGIN
    SELECT id_presentation
    INTO v_presentation
    FROM test_offre_context;

    BEGIN
        INSERT INTO real_estate.offre (
            id_presentation,
            numero_version,
            montant,
            statut
        )
        VALUES (
            v_presentation,
            900003,
            250000.00,
            'INCONNU'
        );

        RAISE EXCEPTION
            'FAIL: unsupported offer status was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: unsupported offer status rejected';
    END;
END;
$$;


-- =============================================================================
-- 12. Expiration must be after offer date
-- =============================================================================

DO $$
DECLARE
    v_presentation BIGINT;
BEGIN
    SELECT id_presentation
    INTO v_presentation
    FROM test_offre_context;

    BEGIN
        INSERT INTO real_estate.offre (
            id_presentation,
            numero_version,
            montant,
            date_offre,
            date_expiration,
            statut
        )
        VALUES (
            v_presentation,
            900004,
            250000.00,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP - INTERVAL '1 day',
            'SOUMISE'
        );

        RAISE EXCEPTION
            'FAIL: invalid offer expiration was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: expiration before offer date rejected';
    END;
END;
$$;


-- =============================================================================
-- 13. SOUMISE must not have a decision timestamp
-- =============================================================================

DO $$
DECLARE
    v_presentation BIGINT;
BEGIN
    SELECT id_presentation
    INTO v_presentation
    FROM test_offre_context;

    BEGIN
        INSERT INTO real_estate.offre (
            id_presentation,
            numero_version,
            montant,
            date_decision,
            statut
        )
        VALUES (
            v_presentation,
            900005,
            250000.00,
            CURRENT_TIMESTAMP,
            'SOUMISE'
        );

        RAISE EXCEPTION
            'FAIL: SOUMISE offer with decision timestamp was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: SOUMISE offer cannot have decision timestamp';
    END;
END;
$$;


-- =============================================================================
-- 14. Explicit decision status requires decision timestamp
-- =============================================================================

DO $$
DECLARE
    v_presentation BIGINT;
BEGIN
    SELECT id_presentation
    INTO v_presentation
    FROM test_offre_context;

    BEGIN
        INSERT INTO real_estate.offre (
            id_presentation,
            numero_version,
            montant,
            statut
        )
        VALUES (
            v_presentation,
            900006,
            250000.00,
            'REFUSEE'
        );

        RAISE EXCEPTION
            'FAIL: REFUSEE offer without decision timestamp was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: explicit decision status requires decision timestamp';
    END;
END;
$$;


-- =============================================================================
-- 15. EXPIREE must remain valid without decision timestamp
-- =============================================================================

INSERT INTO real_estate.offre (
    id_presentation,
    numero_version,
    montant,
    date_offre,
    date_expiration,
    statut
)
SELECT
    id_presentation,
    900007,
    245000.00,
    CURRENT_TIMESTAMP - INTERVAL '8 days',
    CURRENT_TIMESTAMP - INTERVAL '1 day',
    'EXPIREE'
FROM test_offre_context;


DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.offre o
    JOIN test_offre_context t
      ON t.id_presentation = o.id_presentation
    WHERE o.numero_version = 900007
      AND o.statut = 'EXPIREE'
      AND o.date_decision IS NULL;

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: valid EXPIREE offer was not accepted';
    END IF;

    RAISE NOTICE
        'PASS: EXPIREE offer valid without decision timestamp';
END;
$$;


-- =============================================================================
-- 16. Valid revision history must coexist
-- =============================================================================

UPDATE real_estate.offre o
SET
    statut = 'REVISEE',
    date_decision = CURRENT_TIMESTAMP
FROM test_offre_context t
WHERE o.id_presentation = t.id_presentation
  AND o.numero_version = 900001;


INSERT INTO real_estate.offre (
    id_presentation,
    numero_version,
    montant,
    date_expiration,
    statut
)
SELECT
    id_presentation,
    900008,
    255000.00,
    CURRENT_TIMESTAMP + INTERVAL '7 days',
    'SOUMISE'
FROM test_offre_context;


DO $$
DECLARE
    v_revised INTEGER;
    v_current INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_revised
    FROM real_estate.offre o
    JOIN test_offre_context t
      ON t.id_presentation = o.id_presentation
    WHERE o.numero_version = 900001
      AND o.statut = 'REVISEE'
      AND o.date_decision IS NOT NULL;

    SELECT COUNT(*)
    INTO v_current
    FROM real_estate.offre o
    JOIN test_offre_context t
      ON t.id_presentation = o.id_presentation
    WHERE o.numero_version = 900008
      AND o.statut = 'SOUMISE'
      AND o.date_decision IS NULL;

    IF v_revised <> 1 OR v_current <> 1 THEN
        RAISE EXCEPTION
            'FAIL: valid offer revision history was not preserved';
    END IF;

    RAISE NOTICE
        'PASS: revised offer and new submitted version coexist';
END;
$$;


-- =============================================================================
-- 17. First accepted offer must be valid
-- =============================================================================

UPDATE real_estate.offre o
SET
    statut = 'ACCEPTEE',
    date_decision = CURRENT_TIMESTAMP
FROM test_offre_context t
WHERE o.id_presentation = t.id_presentation
  AND o.numero_version = 900008;


DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.offre o
    JOIN test_offre_context t
      ON t.id_presentation = o.id_presentation
    WHERE o.statut = 'ACCEPTEE';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: expected exactly one accepted test offer, found %',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: first accepted offer is valid';
END;
$$;


-- =============================================================================
-- 18. Second accepted offer for same presentation must be rejected
-- =============================================================================

DO $$
DECLARE
    v_presentation BIGINT;
BEGIN
    SELECT id_presentation
    INTO v_presentation
    FROM test_offre_context;

    BEGIN
        INSERT INTO real_estate.offre (
            id_presentation,
            numero_version,
            montant,
            date_decision,
            statut
        )
        VALUES (
            v_presentation,
            900009,
            260000.00,
            CURRENT_TIMESTAMP,
            'ACCEPTEE'
        );

        RAISE EXCEPTION
            'FAIL: second accepted offer for presentation was accepted';

    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'PASS: second accepted offer for presentation rejected';
    END;
END;
$$;


-- =============================================================================
-- 19. Unknown presentation must be rejected
-- =============================================================================

DO $$
DECLARE
    v_unknown_presentation BIGINT;
BEGIN
    SELECT COALESCE(MAX(id_presentation), 0) + 1000000
    INTO v_unknown_presentation
    FROM real_estate.presentation;

    BEGIN
        INSERT INTO real_estate.offre (
            id_presentation,
            numero_version,
            montant,
            statut
        )
        VALUES (
            v_unknown_presentation,
            900010,
            250000.00,
            'SOUMISE'
        );

        RAISE EXCEPTION
            'FAIL: offer referencing unknown presentation was accepted';

    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE
                'PASS: unknown presentation rejected by FK';
    END;
END;
$$;


-- =============================================================================
-- 20. Human-readable evidence
-- =============================================================================

SELECT
    o.id_offre,
    o.id_presentation,
    o.numero_version,
    o.montant,
    o.statut,
    o.date_offre,
    o.date_expiration,
    o.date_decision
FROM real_estate.offre o
JOIN test_offre_context t
  ON t.id_presentation = o.id_presentation
WHERE o.numero_version >= 900000
ORDER BY o.numero_version;


SELECT
    o.id_presentation,
    COUNT(*) AS offer_versions,
    COUNT(*) FILTER (
        WHERE o.statut = 'ACCEPTEE'
    ) AS accepted_offers
FROM real_estate.offre o
JOIN test_offre_context t
  ON t.id_presentation = o.id_presentation
WHERE o.numero_version >= 900000
GROUP BY o.id_presentation;


-- =============================================================================
-- 21. Leave database business state unchanged
-- =============================================================================

ROLLBACK;