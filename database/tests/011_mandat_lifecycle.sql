-- =============================================================================
-- Database test 011
-- Mandat contractual lifecycle
--
-- Validates migration 008:
--
--   1. migration 008 is registered
--   2. historical Mandats have an INITIAL period
--   3. historical values are preserved
--   4. new INITIAL periods last exactly six calendar months
--   5. INITIAL period starts on Mandat signature date
--   6. only one INITIAL period is allowed
--   7. renewal numbering is sequential
--   8. renewal starts at previous period end
--   9. renewal lasts exactly six calendar months
--  10. legacy flag cannot be used for new renewals
--  11. contractual periods are immutable
--
-- Test data is executed inside a transaction and rolled back.
--
-- Negative identifiers are used deliberately so test execution does not
-- consume production identity sequence values.
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;


-- =============================================================================
-- 1. MIGRATION REGISTRATION
-- =============================================================================

DO $$
DECLARE
    migration_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO migration_count
    FROM migration_control.schema_version
    WHERE version = '008';

    IF migration_count <> 1 THEN
        RAISE EXCEPTION
            'TEST FAILED: migration 008 is not registered exactly once';
    END IF;

    RAISE NOTICE
        'PASS: migration 008 is registered';

END;
$$;


-- =============================================================================
-- 2. EVERY EXISTING MANDAT MUST HAVE AN INITIAL PERIOD
-- =============================================================================

DO $$
DECLARE
    missing_initial_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO missing_initial_count
    FROM real_estate.mandat m
    WHERE NOT EXISTS (
        SELECT 1
        FROM real_estate.mandat_periode mp
        WHERE mp.id_mandat = m.id_mandat
          AND mp.numero_periode = 1
          AND mp.type_periode = 'INITIAL'
    );

    IF missing_initial_count <> 0 THEN
        RAISE EXCEPTION
            'TEST FAILED: % Mandat(s) have no INITIAL contractual period',
            missing_initial_count;
    END IF;

    RAISE NOTICE
        'PASS: every existing Mandat has an INITIAL contractual period';

END;
$$;


-- =============================================================================
-- 3. LEGACY BACKFILL MUST PRESERVE ORIGINAL VALUES
-- =============================================================================

DO $$
DECLARE
    mismatch_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO mismatch_count
    FROM real_estate.mandat m
    JOIN real_estate.mandat_periode mp
        ON mp.id_mandat = m.id_mandat
    WHERE mp.numero_periode = 1
      AND mp.type_periode = 'INITIAL'
      AND mp.est_historique_legacy = TRUE
      AND (
          mp.date_debut <> m.date_debut
          OR mp.date_fin <> m.date_fin
      );

    IF mismatch_count <> 0 THEN
        RAISE EXCEPTION
            'TEST FAILED: % legacy period(s) do not preserve Mandat dates',
            mismatch_count;
    END IF;

    RAISE NOTICE
        'PASS: legacy contractual dates are preserved';

END;
$$;


-- =============================================================================
-- 4. PREPARE ISOLATED TEST MANDAT
-- =============================================================================

DO $$
DECLARE
    test_client_id BIGINT;
    test_chasseur_id BIGINT;
BEGIN

    SELECT id_client
    INTO test_client_id
    FROM real_estate.client
    ORDER BY id_client
    LIMIT 1;

    IF test_client_id IS NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: no Client exists for Mandat lifecycle test';
    END IF;


    SELECT id_chasseur
    INTO test_chasseur_id
    FROM real_estate.chasseur
    ORDER BY id_chasseur
    LIMIT 1;

    IF test_chasseur_id IS NULL THEN
        RAISE EXCEPTION
            'TEST FAILED: no Chasseur exists for Mandat lifecycle test';
    END IF;


    INSERT INTO real_estate.mandat (
        id_mandat,
        reference_mandat,
        type_mandat,
        date_signature,
        mode_signature,
        date_debut,
        date_fin,
        statut,
        commentaire,
        id_client,
        id_chasseur
    )
    OVERRIDING SYSTEM VALUE
    VALUES (
        -8008,
        'TEST-MANDAT-LIFECYCLE-008',
        'EXCLUSIF',
        DATE '2026-01-31',
        'ELECTRONIQUE',
        DATE '2026-01-31',
        DATE '2026-07-31',
        'ACTIF',
        'Temporary database lifecycle test',
        test_client_id,
        test_chasseur_id
    );

    RAISE NOTICE
        'PASS: isolated lifecycle test Mandat created';

END;
$$;


-- =============================================================================
-- 5. VALID INITIAL PERIOD
-- =============================================================================

INSERT INTO real_estate.mandat_periode (
    id_mandat_periode,
    id_mandat,
    numero_periode,
    type_periode,
    date_debut,
    date_fin,
    date_renouvellement,
    commentaire,
    est_historique_legacy
)
OVERRIDING SYSTEM VALUE
VALUES (
    -800801,
    -8008,
    1,
    'INITIAL',
    DATE '2026-01-31',
    DATE '2026-07-31',
    NULL,
    'Initial test period',
    FALSE
);


DO $$
DECLARE
    period_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO period_count
    FROM real_estate.mandat_periode
    WHERE id_mandat = -8008
      AND numero_periode = 1
      AND type_periode = 'INITIAL'
      AND date_debut = DATE '2026-01-31'
      AND date_fin = DATE '2026-07-31'
      AND est_historique_legacy = FALSE;

    IF period_count <> 1 THEN
        RAISE EXCEPTION
            'TEST FAILED: valid INITIAL period was not created correctly';
    END IF;

    RAISE NOTICE
        'PASS: valid six-calendar-month INITIAL period accepted';

END;
$$;


-- =============================================================================
-- 6. INVALID SIX-MONTH DURATION MUST FAIL
-- =============================================================================

DO $$
DECLARE
    rejected BOOLEAN := FALSE;
BEGIN

    BEGIN

        INSERT INTO real_estate.mandat_periode (
            id_mandat_periode,
            id_mandat,
            numero_periode,
            type_periode,
            date_debut,
            date_fin,
            date_renouvellement,
            est_historique_legacy
        )
        OVERRIDING SYSTEM VALUE
        VALUES (
            -800802,
            -8008,
            2,
            'RENOUVELLEMENT',
            DATE '2026-07-31',
            DATE '2026-12-31',
            DATE '2026-07-31',
            FALSE
        );

    EXCEPTION
        WHEN OTHERS THEN
            rejected := TRUE;
    END;


    IF rejected = FALSE THEN
        RAISE EXCEPTION
            'TEST FAILED: renewal shorter than six calendar months was accepted';
    END IF;

    RAISE NOTICE
        'PASS: invalid renewal duration rejected';

END;
$$;


-- =============================================================================
-- 7. INVALID PERIOD NUMBER MUST FAIL
-- =============================================================================

DO $$
DECLARE
    rejected BOOLEAN := FALSE;
BEGIN

    BEGIN

        INSERT INTO real_estate.mandat_periode (
            id_mandat_periode,
            id_mandat,
            numero_periode,
            type_periode,
            date_debut,
            date_fin,
            date_renouvellement,
            est_historique_legacy
        )
        OVERRIDING SYSTEM VALUE
        VALUES (
            -800803,
            -8008,
            3,
            'RENOUVELLEMENT',
            DATE '2026-07-31',
            DATE '2027-01-31',
            DATE '2026-07-31',
            FALSE
        );

    EXCEPTION
        WHEN OTHERS THEN
            rejected := TRUE;
    END;


    IF rejected = FALSE THEN
        RAISE EXCEPTION
            'TEST FAILED: non-sequential renewal number was accepted';
    END IF;

    RAISE NOTICE
        'PASS: non-sequential renewal number rejected';

END;
$$;


-- =============================================================================
-- 8. VALID FIRST RENEWAL
-- =============================================================================

INSERT INTO real_estate.mandat_periode (
    id_mandat_periode,
    id_mandat,
    numero_periode,
    type_periode,
    date_debut,
    date_fin,
    date_renouvellement,
    commentaire,
    est_historique_legacy
)
OVERRIDING SYSTEM VALUE
VALUES (
    -800804,
    -8008,
    2,
    'RENOUVELLEMENT',
    DATE '2026-07-31',
    DATE '2027-01-31',
    DATE '2026-07-31',
    'First renewal test period',
    FALSE
);


DO $$
DECLARE
    renewal_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO renewal_count
    FROM real_estate.mandat_periode
    WHERE id_mandat = -8008
      AND numero_periode = 2
      AND type_periode = 'RENOUVELLEMENT'
      AND date_debut = DATE '2026-07-31'
      AND date_fin = DATE '2027-01-31'
      AND date_renouvellement = DATE '2026-07-31';

    IF renewal_count <> 1 THEN
        RAISE EXCEPTION
            'TEST FAILED: valid first renewal was not created correctly';
    END IF;

    RAISE NOTICE
        'PASS: first renewal created correctly';

END;
$$;


-- =============================================================================
-- 9. RENEWAL MUST START AT PREVIOUS PERIOD END
-- =============================================================================

DO $$
DECLARE
    rejected BOOLEAN := FALSE;
BEGIN

    BEGIN

        INSERT INTO real_estate.mandat_periode (
            id_mandat_periode,
            id_mandat,
            numero_periode,
            type_periode,
            date_debut,
            date_fin,
            date_renouvellement,
            est_historique_legacy
        )
        OVERRIDING SYSTEM VALUE
        VALUES (
            -800805,
            -8008,
            3,
            'RENOUVELLEMENT',

            -- Deliberately overlaps period 2 by one day.
            DATE '2027-01-30',
            DATE '2027-07-30',

            DATE '2027-01-30',
            FALSE
        );

    EXCEPTION
        WHEN OTHERS THEN
            rejected := TRUE;
    END;


    IF rejected = FALSE THEN
        RAISE EXCEPTION
            'TEST FAILED: renewal with invalid start boundary was accepted';
    END IF;

    RAISE NOTICE
        'PASS: invalid renewal boundary/overlap rejected';

END;
$$;


-- =============================================================================
-- 10. NEW RENEWAL CANNOT CLAIM LEGACY STATUS
-- =============================================================================

DO $$
DECLARE
    rejected BOOLEAN := FALSE;
BEGIN

    BEGIN

        INSERT INTO real_estate.mandat_periode (
            id_mandat_periode,
            id_mandat,
            numero_periode,
            type_periode,
            date_debut,
            date_fin,
            date_renouvellement,
            est_historique_legacy
        )
        OVERRIDING SYSTEM VALUE
        VALUES (
            -800806,
            -8008,
            3,
            'RENOUVELLEMENT',
            DATE '2027-01-31',
            DATE '2027-07-31',
            DATE '2027-01-31',
            TRUE
        );

    EXCEPTION
        WHEN OTHERS THEN
            rejected := TRUE;
    END;


    IF rejected = FALSE THEN
        RAISE EXCEPTION
            'TEST FAILED: new renewal was allowed to use legacy exemption';
    END IF;

    RAISE NOTICE
        'PASS: legacy exemption cannot be used for a new renewal';

END;
$$;


-- =============================================================================
-- 11. VALID SECOND RENEWAL
-- =============================================================================

INSERT INTO real_estate.mandat_periode (
    id_mandat_periode,
    id_mandat,
    numero_periode,
    type_periode,
    date_debut,
    date_fin,
    date_renouvellement,
    commentaire,
    est_historique_legacy
)
OVERRIDING SYSTEM VALUE
VALUES (
    -800807,
    -8008,
    3,
    'RENOUVELLEMENT',
    DATE '2027-01-31',
    DATE '2027-07-31',
    DATE '2027-01-31',
    'Second renewal test period',
    FALSE
);


-- =============================================================================
-- 12. CONTRACTUAL PERIODS MUST BE IMMUTABLE
-- =============================================================================

DO $$
DECLARE
    rejected BOOLEAN := FALSE;
BEGIN

    BEGIN

        UPDATE real_estate.mandat_periode
        SET commentaire = 'Illegal historical rewrite'
        WHERE id_mandat_periode = -800804;

    EXCEPTION
        WHEN OTHERS THEN
            rejected := TRUE;
    END;


    IF rejected = FALSE THEN
        RAISE EXCEPTION
            'TEST FAILED: contractual period update was accepted';
    END IF;

    RAISE NOTICE
        'PASS: contractual period update rejected';

END;
$$;


-- =============================================================================
-- 13. ONLY ONE INITIAL PERIOD MUST BE ALLOWED
-- =============================================================================

DO $$
DECLARE
    rejected BOOLEAN := FALSE;
BEGIN

    BEGIN

        INSERT INTO real_estate.mandat_periode (
            id_mandat_periode,
            id_mandat,
            numero_periode,
            type_periode,
            date_debut,
            date_fin,
            date_renouvellement,
            est_historique_legacy
        )
        OVERRIDING SYSTEM VALUE
        VALUES (
            -800808,
            -8008,
            4,
            'INITIAL',
            DATE '2027-07-31',
            DATE '2028-01-31',
            NULL,
            FALSE
        );

    EXCEPTION
        WHEN OTHERS THEN
            rejected := TRUE;
    END;


    IF rejected = FALSE THEN
        RAISE EXCEPTION
            'TEST FAILED: second INITIAL period was accepted';
    END IF;

    RAISE NOTICE
        'PASS: second INITIAL period rejected';

END;
$$;


-- =============================================================================
-- 14. FINAL TEST STATE
-- =============================================================================

DO $$
DECLARE
    total_periods INTEGER;
    renewal_periods INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO total_periods
    FROM real_estate.mandat_periode
    WHERE id_mandat = -8008;


    SELECT COUNT(*)
    INTO renewal_periods
    FROM real_estate.mandat_periode
    WHERE id_mandat = -8008
      AND type_periode = 'RENOUVELLEMENT';


    IF total_periods <> 3 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 3 valid periods, found %',
            total_periods;
    END IF;


    IF renewal_periods <> 2 THEN
        RAISE EXCEPTION
            'TEST FAILED: expected 2 valid renewals, found %',
            renewal_periods;
    END IF;


    RAISE NOTICE
        'PASS: Mandat lifecycle contains 1 INITIAL + 2 RENEWAL periods';

END;
$$;


-- =============================================================================
-- TEST REPORT
-- =============================================================================

SELECT
    id_mandat,
    numero_periode,
    type_periode,
    date_debut,
    date_fin,
    date_renouvellement,
    est_historique_legacy
FROM real_estate.mandat_periode
WHERE id_mandat = -8008
ORDER BY numero_periode;


SELECT
    '011_mandat_lifecycle.sql' AS test_file,
    'PASS' AS result,
    'Mandat lifecycle constraints validated' AS description;


-- =============================================================================
-- NEVER KEEP TEST DATA
-- =============================================================================

ROLLBACK;