-- =============================================================================
-- Test 016
-- Validate migration 013: explicit demande client ownership
--
-- Expectations:
--   - migration 013 is registered exactly once;
--   - LEGACY demandes recover their owner from the linked mandate;
--   - GENERATED historical/synthetic demandes may remain ownerless;
--   - non-GENERATED demandes cannot exist without an owner;
--   - mandate-linked demandes must have an owner;
--   - demande owner and mandate owner must match;
--   - valid same-client mandate ownership remains accepted;
--   - FK, CHECK and constraint-trigger objects exist.
--
-- Mutation tests are executed inside subtransactions and intentionally fail.
-- No persistent business test data is created.
-- =============================================================================


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
    WHERE version = '013';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: expected migration_control version 013 exactly once, found %',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: migration 013 registered exactly once';
END;
$$;


-- =============================================================================
-- 2. Explicit ownership column exists
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM information_schema.columns
    WHERE table_schema = 'real_estate'
      AND table_name = 'demande'
      AND column_name = 'id_client'
      AND data_type = 'bigint';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: real_estate.demande.id_client BIGINT does not exist';
    END IF;

    RAISE NOTICE
        'PASS: demande.id_client BIGINT exists';
END;
$$;


-- =============================================================================
-- 3. LEGACY demandes must have deterministic ownership from mandate
-- =============================================================================

DO $$
DECLARE
    v_legacy_count INTEGER;
    v_invalid_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_legacy_count
    FROM real_estate.demande
    WHERE origine = 'LEGACY';

    SELECT COUNT(*)
    INTO v_invalid_count
    FROM real_estate.demande d
    LEFT JOIN real_estate.mandat m
      ON m.id_mandat = d.id_mandat
    WHERE d.origine = 'LEGACY'
      AND (
             d.id_mandat IS NULL
          OR d.id_client IS NULL
          OR m.id_mandat IS NULL
          OR d.id_client IS DISTINCT FROM m.id_client
      );

    IF v_invalid_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % LEGACY demandes have invalid client ownership',
            v_invalid_count;
    END IF;

    RAISE NOTICE
        'PASS: % LEGACY demandes have deterministic mandate-derived ownership',
        v_legacy_count;
END;
$$;


-- =============================================================================
-- 4. Current migrated dataset preserves the 17 known LEGACY demandes
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.demande
    WHERE origine = 'LEGACY';

    IF v_count <> 17 THEN
        RAISE EXCEPTION
            'FAIL: expected 17 LEGACY demandes in current migrated dataset, found %',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: current dataset contains the expected 17 LEGACY demandes';
END;
$$;


-- =============================================================================
-- 5. GENERATED demandes may remain intentionally ownerless
-- =============================================================================

DO $$
DECLARE
    v_generated INTEGER;
    v_ownerless INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_generated
    FROM real_estate.demande
    WHERE origine = 'GENERATED';

    SELECT COUNT(*)
    INTO v_ownerless
    FROM real_estate.demande
    WHERE origine = 'GENERATED'
      AND id_client IS NULL;

    RAISE NOTICE
        'PASS: GENERATED demandes=%; intentionally ownerless=%',
        v_generated,
        v_ownerless;
END;
$$;


-- =============================================================================
-- 6. No real business demande may be ownerless
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.demande
    WHERE origine <> 'GENERATED'
      AND id_client IS NULL;

    IF v_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % non-GENERATED demandes have no client owner',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: every non-GENERATED demande has a client owner';
END;
$$;


-- =============================================================================
-- 7. Every mandate-linked demande must match mandate ownership
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.demande d
    JOIN real_estate.mandat m
      ON m.id_mandat = d.id_mandat
    WHERE d.id_client IS NULL
       OR d.id_client IS DISTINCT FROM m.id_client;

    IF v_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % mandate-linked demandes have inconsistent client ownership',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: all mandate-linked demandes match mandate client ownership';
END;
$$;


-- =============================================================================
-- 8. Required database objects exist
-- =============================================================================

DO $$
DECLARE
    v_fk INTEGER;
    v_check INTEGER;
    v_trigger INTEGER;
    v_index INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_fk
    FROM pg_constraint
    WHERE conrelid = 'real_estate.demande'::regclass
      AND conname = 'fk_demande_client'
      AND contype = 'f';

    SELECT COUNT(*)
    INTO v_check
    FROM pg_constraint
    WHERE conrelid = 'real_estate.demande'::regclass
      AND conname = 'ck_demande_client_owner'
      AND contype = 'c';

    SELECT COUNT(*)
    INTO v_trigger
    FROM pg_trigger
    WHERE tgrelid = 'real_estate.demande'::regclass
      AND tgname = 'trg_demande_mandat_client'
      AND NOT tgisinternal;

    SELECT COUNT(*)
    INTO v_index
    FROM pg_indexes
    WHERE schemaname = 'real_estate'
      AND tablename = 'demande'
      AND indexname = 'idx_demande_client';

    IF v_fk <> 1 THEN
        RAISE EXCEPTION 'FAIL: fk_demande_client missing';
    END IF;

    IF v_check <> 1 THEN
        RAISE EXCEPTION 'FAIL: ck_demande_client_owner missing';
    END IF;

    IF v_trigger <> 1 THEN
        RAISE EXCEPTION 'FAIL: trg_demande_mandat_client missing';
    END IF;

    IF v_index <> 1 THEN
        RAISE EXCEPTION 'FAIL: idx_demande_client missing';
    END IF;

    RAISE NOTICE
        'PASS: ownership FK, CHECK, constraint trigger and index exist';
END;
$$;


-- =============================================================================
-- 9. Constraint trigger must be DEFERRABLE and INITIALLY IMMEDIATE
-- =============================================================================

DO $$
DECLARE
    v_deferrable BOOLEAN;
    v_initially_deferred BOOLEAN;
BEGIN
    SELECT
        tgdeferrable,
        tginitdeferred
    INTO
        v_deferrable,
        v_initially_deferred
    FROM pg_trigger
    WHERE tgrelid = 'real_estate.demande'::regclass
      AND tgname = 'trg_demande_mandat_client'
      AND NOT tgisinternal;

    IF v_deferrable IS DISTINCT FROM TRUE THEN
        RAISE EXCEPTION
            'FAIL: trg_demande_mandat_client is not DEFERRABLE';
    END IF;

    IF v_initially_deferred IS DISTINCT FROM FALSE THEN
        RAISE EXCEPTION
            'FAIL: trg_demande_mandat_client is not INITIALLY IMMEDIATE';
    END IF;

    RAISE NOTICE
        'PASS: mandate/client trigger is DEFERRABLE INITIALLY IMMEDIATE';
END;
$$;


-- =============================================================================
-- 10. CHECK constraint must reject ownerless business demandes
--
-- Reuse an existing row so the test does not depend on knowing every NOT NULL
-- column required for a fresh INSERT.
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
BEGIN
    SELECT id_demande
    INTO v_demande_id
    FROM real_estate.demande
    WHERE origine = 'LEGACY'
    ORDER BY id_demande
    LIMIT 1;

    IF v_demande_id IS NULL THEN
        RAISE EXCEPTION
            'FAIL: no LEGACY demande available for ownership constraint test';
    END IF;

    BEGIN
        UPDATE real_estate.demande
        SET id_client = NULL
        WHERE id_demande = v_demande_id;

        RAISE EXCEPTION
            'FAIL: ownerless business demande was accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: ownerless business demande rejected by CHECK constraint';
    END;
END;
$$;


-- =============================================================================
-- 11. GENERATED demande may remain ownerless when it has no mandate
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
BEGIN
    SELECT id_demande
    INTO v_demande_id
    FROM real_estate.demande
    WHERE origine = 'GENERATED'
      AND id_mandat IS NULL
      AND id_client IS NULL
    ORDER BY id_demande
    LIMIT 1;

    IF v_demande_id IS NULL THEN
        RAISE EXCEPTION
            'FAIL: no ownerless GENERATED demande available for validation';
    END IF;

    UPDATE real_estate.demande
    SET id_client = NULL
    WHERE id_demande = v_demande_id;

    RAISE NOTICE
        'PASS: ownerless GENERATED demande without mandate remains valid';
END;
$$;


-- =============================================================================
-- 12. Trigger must reject mandate/client mismatch
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
    v_wrong_client BIGINT;
BEGIN
    SELECT
        d.id_demande,
        c.id_client
    INTO
        v_demande_id,
        v_wrong_client
    FROM real_estate.demande d
    JOIN real_estate.mandat m
      ON m.id_mandat = d.id_mandat
    CROSS JOIN LATERAL (
        SELECT c2.id_client
        FROM real_estate.client c2
        WHERE c2.id_client <> m.id_client
        ORDER BY c2.id_client
        LIMIT 1
    ) c
    WHERE d.origine = 'LEGACY'
    ORDER BY d.id_demande
    LIMIT 1;

    IF v_demande_id IS NULL OR v_wrong_client IS NULL THEN
        RAISE EXCEPTION
            'FAIL: insufficient fixture data for mandate/client mismatch test';
    END IF;

    BEGIN
        UPDATE real_estate.demande
        SET id_client = v_wrong_client
        WHERE id_demande = v_demande_id;

        RAISE EXCEPTION
            'FAIL: cross-client mandate ownership was accepted';
    EXCEPTION
        WHEN raise_exception THEN
            IF SQLERRM LIKE 'Demande client % does not match mandat % client %' THEN
                RAISE NOTICE
                    'PASS: cross-client mandate ownership rejected by constraint trigger';
            ELSE
                RAISE;
            END IF;
    END;
END;
$$;


-- =============================================================================
-- 13. Trigger must reject ownerless GENERATED demande linked to a mandate
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
    v_mandat_id BIGINT;
BEGIN
    SELECT id_demande
    INTO v_demande_id
    FROM real_estate.demande
    WHERE origine = 'GENERATED'
      AND id_client IS NULL
      AND id_mandat IS NULL
    ORDER BY id_demande
    LIMIT 1;

    SELECT id_mandat
    INTO v_mandat_id
    FROM real_estate.mandat
    ORDER BY id_mandat
    LIMIT 1;

    IF v_demande_id IS NULL OR v_mandat_id IS NULL THEN
        RAISE EXCEPTION
            'FAIL: insufficient fixture data for ownerless mandate-link test';
    END IF;

    BEGIN
        UPDATE real_estate.demande
        SET id_mandat = v_mandat_id
        WHERE id_demande = v_demande_id;

        RAISE EXCEPTION
            'FAIL: ownerless GENERATED demande was linked to a mandate';
    EXCEPTION
        WHEN raise_exception THEN
            IF SQLERRM LIKE 'Demande linked to mandat % must have a client owner' THEN
                RAISE NOTICE
                    'PASS: ownerless demande cannot be linked to a mandate';
            ELSE
                RAISE;
            END IF;
    END;
END;
$$;


-- =============================================================================
-- 14. Valid same-client mandate ownership must remain accepted
--
-- The UPDATE writes the existing valid values back to themselves. This fires
-- the constraint trigger without permanently changing business state.
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
BEGIN
    SELECT d.id_demande
    INTO v_demande_id
    FROM real_estate.demande d
    JOIN real_estate.mandat m
      ON m.id_mandat = d.id_mandat
    WHERE d.id_client = m.id_client
    ORDER BY d.id_demande
    LIMIT 1;

    IF v_demande_id IS NULL THEN
        RAISE EXCEPTION
            'FAIL: no same-client mandate-linked demande available';
    END IF;

    UPDATE real_estate.demande
    SET
        id_client = id_client,
        id_mandat = id_mandat
    WHERE id_demande = v_demande_id;

    RAISE NOTICE
        'PASS: same-client mandate ownership accepted';
END;
$$;


-- =============================================================================
-- 15. Human-readable evidence
-- =============================================================================

SELECT
    origine,
    COUNT(*) AS demandes,
    COUNT(id_client) AS avec_client,
    COUNT(*) - COUNT(id_client) AS sans_client,
    COUNT(id_mandat) AS avec_mandat
FROM real_estate.demande
GROUP BY origine
ORDER BY origine;


SELECT
    d.id_demande,
    d.reference_demande,
    d.origine,
    d.id_client,
    d.id_mandat,
    m.id_client AS mandat_client,
    CASE
        WHEN d.id_mandat IS NULL THEN 'NO_MANDAT'
        WHEN d.id_client = m.id_client THEN 'CONSISTENT'
        ELSE 'INCONSISTENT'
    END AS ownership_status
FROM real_estate.demande d
LEFT JOIN real_estate.mandat m
       ON m.id_mandat = d.id_mandat
ORDER BY d.id_demande;