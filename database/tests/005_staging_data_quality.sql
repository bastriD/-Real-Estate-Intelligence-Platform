-- =============================================================================
-- 005_staging_data_quality.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate one STAGING batch before loading the normalized OLTP model.
--
-- Expected batch content:
--   - 5 staging.recherches
--   - 1000 staging.annonces
--   - 0 invalid staging rows
--
-- Runtime variable:
--   ingestion_batch
--
-- Example:
--   psql \
--     -v ON_ERROR_STOP=1 \
--     -v ingestion_batch='generated-20260822T000000' \
--     -f database/tests/005_staging_data_quality.sql
-- =============================================================================

\set ON_ERROR_STOP on


-- =============================================================================
-- INITIALIZE SESSION BATCH VARIABLE
-- =============================================================================

SELECT set_config(
    'real_estate.ingestion_batch',
    :'ingestion_batch',
    false
);

SELECT
    current_setting('real_estate.ingestion_batch') AS ingestion_batch;


-- =============================================================================
-- 0. BATCH EXISTS
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM staging.annonces
    WHERE ingestion_batch = v_batch;

    IF v_count = 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: batch % does not exist',
            v_batch;
    END IF;

    RAISE NOTICE
        'PASS: STAGING batch % exists',
        v_batch;
END
$$;


-- =============================================================================
-- 1. EXPECTED RECHERCHES COUNT
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM staging.recherches
    WHERE ingestion_batch = v_batch;

    IF v_count <> 5 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: expected 5 recherches for batch %, found %',
            v_batch,
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: 5 staging recherches found';
END
$$;


-- =============================================================================
-- 2. EXPECTED ANNONCES COUNT
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM staging.annonces
    WHERE ingestion_batch = v_batch;

    IF v_count <> 1000 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: expected 1000 annonces for batch %, found %',
            v_batch,
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: 1000 staging annonces found';
END
$$;


-- =============================================================================
-- 3. NO INVALID RECHERCHES
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.recherches
    WHERE ingestion_batch = v_batch
      AND quality_valid = FALSE;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % invalid recherches found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: no invalid staging recherches';
END
$$;


-- =============================================================================
-- 4. NO INVALID ANNONCES
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.annonces
    WHERE ingestion_batch = v_batch
      AND quality_valid = FALSE;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % invalid annonces found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: no invalid staging annonces';
END
$$;


-- =============================================================================
-- 5. RAW / STAGING RECHERCHES RECONCILIATION
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_raw BIGINT;
    v_staging BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_raw
    FROM raw.recherches
    WHERE ingestion_batch = v_batch;

    SELECT COUNT(*)
    INTO v_staging
    FROM staging.recherches
    WHERE ingestion_batch = v_batch;

    IF v_raw <> v_staging THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: recherches reconciliation mismatch, RAW=% STAGING=%',
            v_raw,
            v_staging;
    END IF;

    RAISE NOTICE
        'PASS: recherches RAW/STAGING reconciliation = %',
        v_raw;
END
$$;


-- =============================================================================
-- 6. RAW / STAGING ANNONCES RECONCILIATION
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_raw BIGINT;
    v_staging BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_raw
    FROM raw.annonces
    WHERE ingestion_batch = v_batch;

    SELECT COUNT(*)
    INTO v_staging
    FROM staging.annonces
    WHERE ingestion_batch = v_batch;

    IF v_raw <> v_staging THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: annonces reconciliation mismatch, RAW=% STAGING=%',
            v_raw,
            v_staging;
    END IF;

    RAISE NOTICE
        'PASS: annonces RAW/STAGING reconciliation = %',
        v_raw;
END
$$;


-- =============================================================================
-- 7. UNIQUE RECHERCHE REFERENCES
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_duplicates BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_duplicates
    FROM (
        SELECT reference
        FROM staging.recherches
        WHERE ingestion_batch = v_batch
        GROUP BY reference
        HAVING COUNT(*) > 1
    ) duplicates;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % duplicate recherche references found',
            v_duplicates;
    END IF;

    RAISE NOTICE
        'PASS: staging recherche references are unique';
END
$$;


-- =============================================================================
-- 8. UNIQUE ANNONCE REFERENCES
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_duplicates BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_duplicates
    FROM (
        SELECT reference
        FROM staging.annonces
        WHERE ingestion_batch = v_batch
        GROUP BY reference
        HAVING COUNT(*) > 1
    ) duplicates;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % duplicate annonce references found',
            v_duplicates;
    END IF;

    RAISE NOTICE
        'PASS: staging annonce references are unique';
END
$$;


-- =============================================================================
-- 9. RECHERCHE_REF CONSISTENCY
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_orphans BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_orphans
    FROM staging.annonces a
    LEFT JOIN staging.recherches r
      ON r.reference = a.recherche_ref
     AND r.ingestion_batch = a.ingestion_batch
    WHERE a.ingestion_batch = v_batch
      AND r.staging_id IS NULL;

    IF v_orphans <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % annonces reference an unknown recherche',
            v_orphans;
    END IF;

    RAISE NOTICE
        'PASS: all recherche_ref values resolve inside the batch';
END
$$;


-- =============================================================================
-- 10. MANDATORY RECHERCHE FIELDS
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.recherches
    WHERE ingestion_batch = v_batch
      AND (
            reference IS NULL
            OR BTRIM(reference) = ''
            OR ville IS NULL
            OR BTRIM(ville) = ''
            OR type_bien IS NULL
            OR BTRIM(type_bien) = ''
            OR budget_max IS NULL
            OR surface_min IS NULL
          );

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % recherches have missing mandatory fields',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: mandatory staging recherche fields are populated';
END
$$;


-- =============================================================================
-- 11. MANDATORY ANNONCE FIELDS
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.annonces
    WHERE ingestion_batch = v_batch
      AND (
            reference IS NULL
            OR BTRIM(reference) = ''
            OR recherche_ref IS NULL
            OR BTRIM(recherche_ref) = ''
            OR ville IS NULL
            OR BTRIM(ville) = ''
            OR type_bien IS NULL
            OR BTRIM(type_bien) = ''
            OR prix IS NULL
            OR surface IS NULL
          );

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % annonces have missing mandatory fields',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: mandatory staging annonce fields are populated';
END
$$;


-- =============================================================================
-- 12. PRICE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.annonces
    WHERE ingestion_batch = v_batch
      AND prix <= 0;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % annonces have price <= 0',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: all staging prices are positive';
END
$$;


-- =============================================================================
-- 13. SURFACE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.annonces
    WHERE ingestion_batch = v_batch
      AND surface <= 0;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % annonces have surface <= 0',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: all staging surfaces are positive';
END
$$;


-- =============================================================================
-- 14. LATITUDE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.annonces
    WHERE ingestion_batch = v_batch
      AND latitude IS NOT NULL
      AND latitude NOT BETWEEN -90 AND 90;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % invalid latitudes found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: latitude values are valid';
END
$$;


-- =============================================================================
-- 15. LONGITUDE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.annonces
    WHERE ingestion_batch = v_batch
      AND longitude IS NOT NULL
      AND longitude NOT BETWEEN -180 AND 180;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % invalid longitudes found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: longitude values are valid';
END
$$;


-- =============================================================================
-- 16. DPE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.annonces
    WHERE ingestion_batch = v_batch
      AND dpe IS NOT NULL
      AND dpe NOT IN (
          'A',
          'B',
          'C',
          'D',
          'E',
          'F',
          'G'
      );

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % invalid DPE values found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: DPE values are valid';
END
$$;


-- =============================================================================
-- 17. PUBLICATION DATE SANITY
--
-- Generated publication dates should not be absurdly old.
-- Future dates are allowed because the current generator may produce them.
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM staging.annonces
    WHERE ingestion_batch = v_batch
      AND date_publication IS NOT NULL
      AND date_publication < TIMESTAMPTZ '2000-01-01 00:00:00+00';

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'STAGING DQ FAILED: % implausible publication dates found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: publication dates are plausible';
END
$$;


-- =============================================================================
-- 18. STAGING QUALITY METRICS
-- =============================================================================

SELECT
    COUNT(*) AS total_annonces,

    COUNT(*) FILTER (
        WHERE dpe IS NULL
    ) AS missing_dpe,

    COUNT(*) FILTER (
        WHERE nb_pieces IS NULL
    ) AS missing_nb_pieces,

    COUNT(*) FILTER (
        WHERE nb_chambres IS NULL
    ) AS missing_nb_chambres,

    COUNT(*) FILTER (
        WHERE contact_email IS NULL
    ) AS missing_contact_email,

    COUNT(*) FILTER (
        WHERE latitude IS NULL
    ) AS missing_latitude,

    COUNT(*) FILTER (
        WHERE longitude IS NULL
    ) AS missing_longitude,

    ROUND(AVG(prix), 2) AS average_price,

    ROUND(AVG(surface), 2) AS average_surface

FROM staging.annonces
WHERE ingestion_batch =
    current_setting('real_estate.ingestion_batch');


-- =============================================================================
-- 19. PRICE RANGE
-- =============================================================================

SELECT
    MIN(prix) AS min_price,
    MAX(prix) AS max_price,
    ROUND(AVG(prix), 2) AS avg_price
FROM staging.annonces
WHERE ingestion_batch =
    current_setting('real_estate.ingestion_batch');


-- =============================================================================
-- 20. SURFACE RANGE
-- =============================================================================

SELECT
    MIN(surface) AS min_surface,
    MAX(surface) AS max_surface,
    ROUND(AVG(surface), 2) AS avg_surface
FROM staging.annonces
WHERE ingestion_batch =
    current_setting('real_estate.ingestion_batch');


-- =============================================================================
-- 21. PROPERTY TYPE DISTRIBUTION
-- =============================================================================

SELECT
    type_bien,
    COUNT(*) AS annonces
FROM staging.annonces
WHERE ingestion_batch =
    current_setting('real_estate.ingestion_batch')
GROUP BY type_bien
ORDER BY annonces DESC, type_bien;


-- =============================================================================
-- 22. CITY DISTRIBUTION
-- =============================================================================

SELECT
    ville,
    COUNT(*) AS annonces
FROM staging.annonces
WHERE ingestion_batch =
    current_setting('real_estate.ingestion_batch')
GROUP BY ville
ORDER BY annonces DESC, ville;


-- =============================================================================
-- FINAL RESULT
-- =============================================================================

SELECT
    'PASS' AS status,
    current_setting(
        'real_estate.ingestion_batch'
    ) AS ingestion_batch,
    'STAGING data quality validated successfully' AS result;