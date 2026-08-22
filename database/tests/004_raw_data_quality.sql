-- =============================================================================
-- 004_raw_data_quality.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate one RAW ingestion batch before transformation to STAGING.
--
-- Expected batch content:
--   - 5 recherches
--   - 1000 annonces
--
-- Runtime variable:
--   ingestion_batch
--
-- Example:
--   psql \
--     -v ON_ERROR_STOP=1 \
--     -v ingestion_batch='generated-20260822T000000' \
--     -f database/tests/004_raw_data_quality.sql
-- =============================================================================

\set ON_ERROR_STOP on


-- =============================================================================
-- INITIALIZE SESSION BATCH VARIABLE
--
-- psql variables cannot safely be referenced directly from inside a
-- PL/pgSQL DO $$ ... $$ body.
--
-- Store the supplied psql variable as a session setting first.
-- Every DO block can then retrieve it using current_setting().
-- =============================================================================

SELECT set_config(
    'real_estate.ingestion_batch',
    :'ingestion_batch',
    false
);

SELECT
    current_setting('real_estate.ingestion_batch') AS ingestion_batch;


-- =============================================================================
-- 0. BATCH EXISTENCE
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM raw.annonces
    WHERE ingestion_batch = v_batch;

    IF v_count = 0 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: batch % does not exist in raw.annonces',
            v_batch;
    END IF;

    RAISE NOTICE
        'PASS: RAW batch % exists',
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
    FROM raw.recherches
    WHERE ingestion_batch = v_batch;

    IF v_count <> 5 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: expected 5 recherches for batch %, found %',
            v_batch,
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: 5 recherches found for batch %',
        v_batch;
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
    FROM raw.annonces
    WHERE ingestion_batch = v_batch;

    IF v_count <> 1000 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: expected 1000 annonces for batch %, found %',
            v_batch,
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: 1000 annonces found for batch %',
        v_batch;
END
$$;


-- =============================================================================
-- 3. DUPLICATE RECHERCHE REFERENCES
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
        FROM raw.recherches
        WHERE ingestion_batch = v_batch
        GROUP BY reference
        HAVING COUNT(*) > 1
    ) duplicates;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: % duplicate recherche references found',
            v_duplicates;
    END IF;

    RAISE NOTICE
        'PASS: no duplicate recherche references';
END
$$;


-- =============================================================================
-- 4. DUPLICATE ANNONCE REFERENCES
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
        FROM raw.annonces
        WHERE ingestion_batch = v_batch
        GROUP BY reference
        HAVING COUNT(*) > 1
    ) duplicates;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: % duplicate annonce references found',
            v_duplicates;
    END IF;

    RAISE NOTICE
        'PASS: no duplicate annonce references';
END
$$;


-- =============================================================================
-- 5. MANDATORY RECHERCHE FIELDS
--
-- Generator matching rules rely on:
--   reference
--   ville
--   type_bien
--   budget_max
--   surface_min
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM raw.recherches
    WHERE ingestion_batch = v_batch
      AND (
            reference IS NULL
            OR BTRIM(reference) = ''
            OR ville IS NULL
            OR BTRIM(ville) = ''
            OR type_bien IS NULL
            OR BTRIM(type_bien) = ''
            OR budget_max IS NULL
            OR BTRIM(budget_max) = ''
            OR surface_min IS NULL
            OR BTRIM(surface_min) = ''
          );

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: % recherches have missing mandatory fields',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: mandatory recherche fields are populated';
END
$$;


-- =============================================================================
-- 6. MANDATORY ANNONCE MATCHING FIELDS
--
-- Guaranteed matching attributes:
--   reference
--   recherche_ref
--   ville
--   type_bien
--   prix
--   surface OR surface_m2
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM raw.annonces
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
            OR BTRIM(prix) = ''
            OR (
                (
                    surface IS NULL
                    OR BTRIM(surface) = ''
                )
                AND
                (
                    surface_m2 IS NULL
                    OR BTRIM(surface_m2) = ''
                )
            )
          );

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: % annonces have missing mandatory matching fields',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: mandatory annonce matching fields are populated';
END
$$;


-- =============================================================================
-- 7. RECHERCHE_REF REFERENTIAL CONSISTENCY
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_orphans BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_orphans
    FROM raw.annonces a
    LEFT JOIN raw.recherches r
      ON r.reference = a.recherche_ref
     AND r.ingestion_batch = a.ingestion_batch
    WHERE a.ingestion_batch = v_batch
      AND r.raw_id IS NULL;

    IF v_orphans <> 0 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: % annonces reference an unknown recherche',
            v_orphans;
    END IF;

    RAISE NOTICE
        'PASS: every annonce recherche_ref resolves in the same batch';
END
$$;


-- =============================================================================
-- 8. BASIC PRICE PARSEABILITY
--
-- RAW values may contain:
--   320000
--   320000 €
--   320 000 €
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM raw.annonces
    WHERE ingestion_batch = v_batch
      AND prix IS NOT NULL
      AND BTRIM(prix) <> ''
      AND REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        BTRIM(prix),
                        '€',
                        ''
                    ),
                    ' ',
                    ''
                ),
                ',',
                '.'
            ),
            CHR(160),
            ''
          ) !~ '^[0-9]+([.][0-9]+)?$';

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: % annonce prices are not parseable',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: all non-null annonce prices are parseable';
END
$$;


-- =============================================================================
-- 9. BASIC SURFACE PARSEABILITY
--
-- surface is preferred.
-- surface_m2 acts as fallback.
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM raw.annonces
    WHERE ingestion_batch = v_batch
      AND COALESCE(
            NULLIF(BTRIM(surface), ''),
            NULLIF(BTRIM(surface_m2), '')
          ) IS NOT NULL
      AND REPLACE(
            REPLACE(
                REPLACE(
                    COALESCE(
                        NULLIF(BTRIM(surface), ''),
                        NULLIF(BTRIM(surface_m2), '')
                    ),
                    'm²',
                    ''
                ),
                ' ',
                ''
            ),
            ',',
            '.'
          ) !~ '^[0-9]+([.][0-9]+)?$';

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'RAW DQ FAILED: % annonce surfaces are not parseable',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: all annonce surfaces are parseable';
END
$$;


-- =============================================================================
-- 10. QUALITY METRICS
--
-- Informational metrics.
-- Optional source attributes may legitimately be absent.
-- =============================================================================

SELECT
    COUNT(*) AS total_annonces,

    COUNT(*) FILTER (
        WHERE code_postal IS NULL
           OR BTRIM(code_postal) = ''
    ) AS missing_code_postal,

    COUNT(*) FILTER (
        WHERE date_publication IS NULL
           OR BTRIM(date_publication) = ''
    ) AS missing_date_publication,

    COUNT(*) FILTER (
        WHERE dpe IS NULL
           OR BTRIM(dpe) = ''
    ) AS missing_dpe,

    COUNT(*) FILTER (
        WHERE nb_pieces IS NULL
           OR BTRIM(nb_pieces) = ''
    ) AS missing_nb_pieces,

    COUNT(*) FILTER (
        WHERE nb_chambres IS NULL
           OR BTRIM(nb_chambres) = ''
    ) AS missing_nb_chambres,

    COUNT(*) FILTER (
        WHERE contact_email IS NULL
           OR BTRIM(contact_email) = ''
    ) AS missing_contact_email,

    COUNT(*) FILTER (
        WHERE latitude IS NULL
           OR BTRIM(latitude) = ''
    ) AS missing_latitude,

    COUNT(*) FILTER (
        WHERE longitude IS NULL
           OR BTRIM(longitude) = ''
    ) AS missing_longitude

FROM raw.annonces
WHERE ingestion_batch =
    current_setting('real_estate.ingestion_batch');


-- =============================================================================
-- 11. DISTRIBUTION BY PROPERTY TYPE
-- =============================================================================

SELECT
    type_bien,
    COUNT(*) AS annonces
FROM raw.annonces
WHERE ingestion_batch =
    current_setting('real_estate.ingestion_batch')
GROUP BY type_bien
ORDER BY annonces DESC, type_bien;


-- =============================================================================
-- 12. DISTRIBUTION BY CITY
-- =============================================================================

SELECT
    ville,
    COUNT(*) AS annonces
FROM raw.annonces
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
    'RAW data quality validated successfully' AS result;