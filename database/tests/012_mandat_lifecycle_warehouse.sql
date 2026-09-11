BEGIN;

-- =============================================================================
-- Test 012
-- Validate warehouse.fact_mandat_periode
--
-- Objectives:
--   - Verify migration 009 is registered
--   - Verify OLTP -> Warehouse backfill completeness
--   - Verify source uniqueness
--   - Verify period uniqueness per Mandat
--   - Verify date keys resolve correctly
--   - Verify INITIAL / RENOUVELLEMENT semantics
--   - Verify duration and count constraints
--   - Verify warehouse compatibility with existing fact_mandat grain
--
-- This test is transactional and ends with ROLLBACK.
-- =============================================================================


-- =============================================================================
-- 1. Migration registration
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM migration_control.schema_version
    WHERE version = '009';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: migration 009 must be registered exactly once, found %',
            v_count;
    END IF;

    RAISE NOTICE 'PASS: migration 009 registered';
END;
$$;


-- =============================================================================
-- 2. Table exists
-- =============================================================================

DO $$
DECLARE
    v_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'warehouse'
          AND table_name = 'fact_mandat_periode'
    )
    INTO v_exists;

    IF NOT v_exists THEN
        RAISE EXCEPTION
            'FAIL: warehouse.fact_mandat_periode does not exist';
    END IF;

    RAISE NOTICE 'PASS: warehouse.fact_mandat_periode exists';
END;
$$;


-- =============================================================================
-- 3. Backfill completeness
--
-- Every OLTP Mandat period must have exactly one warehouse fact row.
-- =============================================================================

DO $$
DECLARE
    v_source_count INTEGER;
    v_warehouse_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_source_count
    FROM real_estate.mandat_periode;

    SELECT COUNT(*)
    INTO v_warehouse_count
    FROM warehouse.fact_mandat_periode;

    IF v_source_count <> v_warehouse_count THEN
        RAISE EXCEPTION
            'FAIL: OLTP periods=% warehouse periods=%',
            v_source_count,
            v_warehouse_count;
    END IF;

    RAISE NOTICE
        'PASS: warehouse period count matches OLTP source count (%)',
        v_source_count;
END;
$$;


-- =============================================================================
-- 4. No missing source periods
-- =============================================================================

DO $$
DECLARE
    v_missing INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_missing
    FROM real_estate.mandat_periode mp
    LEFT JOIN warehouse.fact_mandat_periode fmp
      ON fmp.id_mandat_periode_source = mp.id_mandat_periode
    WHERE fmp.id_mandat_periode_source IS NULL;

    IF v_missing <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % OLTP Mandat periods are missing from warehouse',
            v_missing;
    END IF;

    RAISE NOTICE 'PASS: no missing Mandat periods in warehouse';
END;
$$;


-- =============================================================================
-- 5. Existing fact_mandat grain remains unchanged
--
-- One fact_mandat row per source Mandat.
-- =============================================================================

DO $$
DECLARE
    v_duplicates INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_duplicates
    FROM (
        SELECT id_mandat_source
        FROM warehouse.fact_mandat
        GROUP BY id_mandat_source
        HAVING COUNT(*) > 1
    ) d;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'FAIL: fact_mandat contains duplicate source Mandats';
    END IF;

    RAISE NOTICE
        'PASS: fact_mandat grain remains one row per source Mandat';
END;
$$;


-- =============================================================================
-- 6. Unique source period
-- =============================================================================

DO $$
DECLARE
    v_duplicates INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_duplicates
    FROM (
        SELECT id_mandat_periode_source
        FROM warehouse.fact_mandat_periode
        GROUP BY id_mandat_periode_source
        HAVING COUNT(*) > 1
    ) d;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'FAIL: duplicate id_mandat_periode_source found';
    END IF;

    RAISE NOTICE 'PASS: source period identifiers are unique';
END;
$$;


-- =============================================================================
-- 7. Unique period number per Mandat
-- =============================================================================

DO $$
DECLARE
    v_duplicates INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_duplicates
    FROM (
        SELECT
            mandat_fact_key,
            numero_periode
        FROM warehouse.fact_mandat_periode
        GROUP BY
            mandat_fact_key,
            numero_periode
        HAVING COUNT(*) > 1
    ) d;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'FAIL: duplicate period number found for a Mandat';
    END IF;

    RAISE NOTICE
        'PASS: period numbers are unique within each Mandat';
END;
$$;


-- =============================================================================
-- 8. Mandat foreign-key mapping
-- =============================================================================

DO $$
DECLARE
    v_invalid INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM warehouse.fact_mandat_periode fmp
    LEFT JOIN warehouse.fact_mandat fm
      ON fm.mandat_fact_key = fmp.mandat_fact_key
    WHERE fm.mandat_fact_key IS NULL;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % period rows have no warehouse Mandat parent',
            v_invalid;
    END IF;

    RAISE NOTICE 'PASS: every period maps to a warehouse Mandat';
END;
$$;


-- =============================================================================
-- 9. Source Mandat mapping is correct
-- =============================================================================

DO $$
DECLARE
    v_mismatch INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_mismatch
    FROM warehouse.fact_mandat_periode fmp
    JOIN real_estate.mandat_periode mp
      ON mp.id_mandat_periode = fmp.id_mandat_periode_source
    JOIN warehouse.fact_mandat fm
      ON fm.mandat_fact_key = fmp.mandat_fact_key
    WHERE fm.id_mandat_source <> mp.id_mandat;

    IF v_mismatch <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % warehouse periods map to wrong Mandat',
            v_mismatch;
    END IF;

    RAISE NOTICE 'PASS: source Mandat mapping is correct';
END;
$$;


-- =============================================================================
-- 10. Date keys match OLTP source dates
-- =============================================================================

DO $$
DECLARE
    v_mismatch INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_mismatch
    FROM warehouse.fact_mandat_periode fmp
    JOIN real_estate.mandat_periode mp
      ON mp.id_mandat_periode = fmp.id_mandat_periode_source
    WHERE fmp.date_debut_key
              <> TO_CHAR(mp.date_debut, 'YYYYMMDD')::INTEGER
       OR fmp.date_fin_key
              <> TO_CHAR(mp.date_fin, 'YYYYMMDD')::INTEGER
       OR fmp.date_renouvellement_key
              IS DISTINCT FROM
              CASE
                  WHEN mp.date_renouvellement IS NULL
                      THEN NULL
                  ELSE TO_CHAR(
                      mp.date_renouvellement,
                      'YYYYMMDD'
                  )::INTEGER
              END;

    IF v_mismatch <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % warehouse period date mappings differ from OLTP',
            v_mismatch;
    END IF;

    RAISE NOTICE 'PASS: warehouse date keys match OLTP dates';
END;
$$;


-- =============================================================================
-- 11. All date keys resolve through dim_date
-- =============================================================================

DO $$
DECLARE
    v_invalid INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM warehouse.fact_mandat_periode fmp
    LEFT JOIN warehouse.dim_date dd_start
      ON dd_start.date_key = fmp.date_debut_key
    LEFT JOIN warehouse.dim_date dd_end
      ON dd_end.date_key = fmp.date_fin_key
    LEFT JOIN warehouse.dim_date dd_renew
      ON dd_renew.date_key = fmp.date_renouvellement_key
    WHERE dd_start.date_key IS NULL
       OR dd_end.date_key IS NULL
       OR (
           fmp.date_renouvellement_key IS NOT NULL
           AND dd_renew.date_key IS NULL
       );

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % warehouse period rows contain unresolved date keys',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: all Mandat period date keys resolve through dim_date';
END;
$$;


-- =============================================================================
-- 12. Duration matches OLTP period
-- =============================================================================

DO $$
DECLARE
    v_mismatch INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_mismatch
    FROM warehouse.fact_mandat_periode fmp
    JOIN real_estate.mandat_periode mp
      ON mp.id_mandat_periode = fmp.id_mandat_periode_source
    WHERE fmp.duree_jours <> (mp.date_fin - mp.date_debut);

    IF v_mismatch <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % warehouse periods have incorrect duration',
            v_mismatch;
    END IF;

    RAISE NOTICE 'PASS: period duration matches OLTP';
END;
$$;


-- =============================================================================
-- 13. INITIAL semantic
-- =============================================================================

DO $$
DECLARE
    v_invalid INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM warehouse.fact_mandat_periode
    WHERE type_periode = 'INITIAL'
      AND date_renouvellement_key IS NOT NULL;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'FAIL: INITIAL periods must not have renewal date';
    END IF;

    RAISE NOTICE 'PASS: INITIAL period semantics valid';
END;
$$;


-- =============================================================================
-- 14. RENOUVELLEMENT semantic
-- =============================================================================

DO $$
DECLARE
    v_invalid INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM warehouse.fact_mandat_periode
    WHERE type_periode = 'RENOUVELLEMENT'
      AND date_renouvellement_key IS NULL;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'FAIL: RENOUVELLEMENT periods require renewal date';
    END IF;

    RAISE NOTICE 'PASS: RENOUVELLEMENT period semantics valid';
END;
$$;


-- =============================================================================
-- 15. periode_count invariant
-- =============================================================================

DO $$
DECLARE
    v_invalid INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM warehouse.fact_mandat_periode
    WHERE periode_count <> 1;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'FAIL: periode_count must always equal 1';
    END IF;

    RAISE NOTICE 'PASS: periode_count invariant valid';
END;
$$;


-- =============================================================================
-- 16. Constraint test: invalid period number
-- =============================================================================

DO $$
DECLARE
    v_mandat_fact_key BIGINT;
    v_source_id BIGINT;
BEGIN
    SELECT mandat_fact_key
    INTO v_mandat_fact_key
    FROM warehouse.fact_mandat
    ORDER BY mandat_fact_key
    LIMIT 1;

    SELECT COALESCE(MAX(id_mandat_periode_source), 0) + 1000000
    INTO v_source_id
    FROM warehouse.fact_mandat_periode;

    BEGIN
        INSERT INTO warehouse.fact_mandat_periode (
            id_mandat_periode_source,
            mandat_fact_key,
            numero_periode,
            type_periode,
            date_debut_key,
            date_fin_key,
            date_renouvellement_key,
            est_historique_legacy,
            duree_jours,
            periode_count,
            created_at_source
        )
        VALUES (
            v_source_id,
            v_mandat_fact_key,
            0,
            'INITIAL',
            20260101,
            20260701,
            NULL,
            FALSE,
            181,
            1,
            CURRENT_TIMESTAMP
        );

        RAISE EXCEPTION
            'FAIL: numero_periode=0 was accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: numero_periode constraint rejects zero';
    END;
END;
$$;


-- =============================================================================
-- 17. Constraint test: invalid period type
-- =============================================================================

DO $$
DECLARE
    v_mandat_fact_key BIGINT;
    v_source_id BIGINT;
BEGIN
    SELECT mandat_fact_key
    INTO v_mandat_fact_key
    FROM warehouse.fact_mandat
    ORDER BY mandat_fact_key
    LIMIT 1;

    SELECT COALESCE(MAX(id_mandat_periode_source), 0) + 2000000
    INTO v_source_id
    FROM warehouse.fact_mandat_periode;

    BEGIN
        INSERT INTO warehouse.fact_mandat_periode (
            id_mandat_periode_source,
            mandat_fact_key,
            numero_periode,
            type_periode,
            date_debut_key,
            date_fin_key,
            date_renouvellement_key,
            est_historique_legacy,
            duree_jours,
            periode_count,
            created_at_source
        )
        VALUES (
            v_source_id,
            v_mandat_fact_key,
            99,
            'INVALID',
            20260101,
            20260701,
            NULL,
            FALSE,
            181,
            1,
            CURRENT_TIMESTAMP
        );

        RAISE EXCEPTION
            'FAIL: invalid period type was accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: period type constraint rejects invalid value';
    END;
END;
$$;


-- =============================================================================
-- 18. Constraint test: INITIAL with renewal date
-- =============================================================================

DO $$
DECLARE
    v_mandat_fact_key BIGINT;
    v_source_id BIGINT;
BEGIN
    SELECT mandat_fact_key
    INTO v_mandat_fact_key
    FROM warehouse.fact_mandat
    ORDER BY mandat_fact_key
    LIMIT 1;

    SELECT COALESCE(MAX(id_mandat_periode_source), 0) + 3000000
    INTO v_source_id
    FROM warehouse.fact_mandat_periode;

    BEGIN
        INSERT INTO warehouse.fact_mandat_periode (
            id_mandat_periode_source,
            mandat_fact_key,
            numero_periode,
            type_periode,
            date_debut_key,
            date_fin_key,
            date_renouvellement_key,
            est_historique_legacy,
            duree_jours,
            periode_count,
            created_at_source
        )
        VALUES (
            v_source_id,
            v_mandat_fact_key,
            99,
            'INITIAL',
            20260101,
            20260701,
            20260101,
            FALSE,
            181,
            1,
            CURRENT_TIMESTAMP
        );

        RAISE EXCEPTION
            'FAIL: INITIAL period with renewal date was accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: INITIAL renewal-date constraint enforced';
    END;
END;
$$;


-- =============================================================================
-- 19. Constraint test: RENOUVELLEMENT without renewal date
-- =============================================================================

DO $$
DECLARE
    v_mandat_fact_key BIGINT;
    v_source_id BIGINT;
BEGIN
    SELECT mandat_fact_key
    INTO v_mandat_fact_key
    FROM warehouse.fact_mandat
    ORDER BY mandat_fact_key
    LIMIT 1;

    SELECT COALESCE(MAX(id_mandat_periode_source), 0) + 4000000
    INTO v_source_id
    FROM warehouse.fact_mandat_periode;

    BEGIN
        INSERT INTO warehouse.fact_mandat_periode (
            id_mandat_periode_source,
            mandat_fact_key,
            numero_periode,
            type_periode,
            date_debut_key,
            date_fin_key,
            date_renouvellement_key,
            est_historique_legacy,
            duree_jours,
            periode_count,
            created_at_source
        )
        VALUES (
            v_source_id,
            v_mandat_fact_key,
            99,
            'RENOUVELLEMENT',
            20260101,
            20260701,
            NULL,
            FALSE,
            181,
            1,
            CURRENT_TIMESTAMP
        );

        RAISE EXCEPTION
            'FAIL: RENOUVELLEMENT without renewal date was accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: RENOUVELLEMENT renewal-date constraint enforced';
    END;
END;
$$;


-- =============================================================================
-- 20. Constraint test: periode_count
-- =============================================================================

DO $$
DECLARE
    v_mandat_fact_key BIGINT;
    v_source_id BIGINT;
BEGIN
    SELECT mandat_fact_key
    INTO v_mandat_fact_key
    FROM warehouse.fact_mandat
    ORDER BY mandat_fact_key
    LIMIT 1;

    SELECT COALESCE(MAX(id_mandat_periode_source), 0) + 5000000
    INTO v_source_id
    FROM warehouse.fact_mandat_periode;

    BEGIN
        INSERT INTO warehouse.fact_mandat_periode (
            id_mandat_periode_source,
            mandat_fact_key,
            numero_periode,
            type_periode,
            date_debut_key,
            date_fin_key,
            date_renouvellement_key,
            est_historique_legacy,
            duree_jours,
            periode_count,
            created_at_source
        )
        VALUES (
            v_source_id,
            v_mandat_fact_key,
            99,
            'INITIAL',
            20260101,
            20260701,
            NULL,
            FALSE,
            181,
            2,
            CURRENT_TIMESTAMP
        );

        RAISE EXCEPTION
            'FAIL: periode_count <> 1 was accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: periode_count constraint enforced';
    END;
END;
$$;


-- =============================================================================
-- 21. Final diagnostic summary
-- =============================================================================

SELECT
    COUNT(*) AS warehouse_periods,
    COUNT(*) FILTER (
        WHERE type_periode = 'INITIAL'
    ) AS initial_periods,
    COUNT(*) FILTER (
        WHERE type_periode = 'RENOUVELLEMENT'
    ) AS renewal_periods,
    COUNT(*) FILTER (
        WHERE est_historique_legacy
    ) AS legacy_periods,
    COUNT(DISTINCT mandat_fact_key) AS represented_mandats
FROM warehouse.fact_mandat_periode;


ROLLBACK;