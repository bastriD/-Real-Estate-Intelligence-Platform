-- =============================================================================
-- 006_oltp_data_quality.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate the final OLTP load for one ingestion batch.
--
-- Runtime variable:
--   ingestion_batch
--
-- Assumptions:
--   - generated source name = GENERATEUR_ANNONCES
--   - staging batch contains the references expected in OLTP
--   - real_estate.bien uniqueness is enforced by:
--       (id_source, reference_externe)
--
-- Example:
--   psql \
--     -v ON_ERROR_STOP=1 \
--     -v ingestion_batch='generated-20260822T000000' \
--     -f database/tests/006_oltp_data_quality.sql
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
-- 0. SOURCE EXISTS
-- =============================================================================

DO $$
DECLARE
    v_source_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_source_count
    FROM real_estate.source
    WHERE nom = 'GENERATEUR_ANNONCES'
      AND type_source = 'AUTRE';

    IF v_source_count = 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: generated source does not exist';
    END IF;

    IF v_source_count > 1 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: multiple generated sources found: %',
            v_source_count;
    END IF;

    RAISE NOTICE
        'PASS: generated source exists exactly once';
END
$$;


-- =============================================================================
-- 1. SOURCE IS ACTIVE
-- =============================================================================

DO $$
DECLARE
    v_inactive BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_inactive
    FROM real_estate.source
    WHERE nom = 'GENERATEUR_ANNONCES'
      AND type_source = 'AUTRE'
      AND actif = FALSE;

    IF v_inactive <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: generated source is inactive';
    END IF;

    RAISE NOTICE
        'PASS: generated source is active';
END
$$;


-- =============================================================================
-- 2. EXPECTED BIEN COUNT FOR CURRENT BATCH
--
-- Count only properties whose references are present in the current
-- validated staging batch.
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_expected BIGINT;
    v_loaded BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_expected
    FROM staging.annonces
    WHERE ingestion_batch = v_batch
      AND quality_valid = TRUE;

    SELECT COUNT(*)
    INTO v_loaded
    FROM staging.annonces s
    JOIN real_estate.source src
      ON src.nom = 'GENERATEUR_ANNONCES'
     AND src.type_source = 'AUTRE'
    JOIN real_estate.bien b
      ON b.reference_externe = s.reference
     AND b.id_source = src.id_source
    WHERE s.ingestion_batch = v_batch
      AND s.quality_valid = TRUE;

    IF v_expected <> v_loaded THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: expected % biens for batch %, found %',
            v_expected,
            v_batch,
            v_loaded;
    END IF;

    RAISE NOTICE
        'PASS: % biens loaded for current batch',
        v_loaded;
END
$$;


-- =============================================================================
-- 3. NO MISSING STAGING REFERENCES
-- =============================================================================

DO $$
DECLARE
    v_batch TEXT := current_setting('real_estate.ingestion_batch');
    v_missing BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_missing
    FROM staging.annonces s
    JOIN real_estate.source src
      ON src.nom = 'GENERATEUR_ANNONCES'
     AND src.type_source = 'AUTRE'
    LEFT JOIN real_estate.bien b
      ON b.reference_externe = s.reference
     AND b.id_source = src.id_source
    WHERE s.ingestion_batch = v_batch
      AND s.quality_valid = TRUE
      AND b.id_bien IS NULL;

    IF v_missing <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % staging annonces are missing from real_estate.bien',
            v_missing;
    END IF;

    RAISE NOTICE
        'PASS: all staging references exist in OLTP';
END
$$;


-- =============================================================================
-- 4. NO DUPLICATE SOURCE / REFERENCE PAIRS
-- =============================================================================

DO $$
DECLARE
    v_duplicates BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_duplicates
    FROM (
        SELECT
            id_source,
            reference_externe
        FROM real_estate.bien
        GROUP BY
            id_source,
            reference_externe
        HAVING COUNT(*) > 1
    ) duplicate_rows;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % duplicate (id_source, reference_externe) pairs found',
            v_duplicates;
    END IF;

    RAISE NOTICE
        'PASS: no duplicate source/reference pairs';
END
$$;


-- =============================================================================
-- 5. SOURCE FOREIGN KEY CONSISTENCY
-- =============================================================================

DO $$
DECLARE
    v_orphans BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_orphans
    FROM real_estate.bien b
    LEFT JOIN real_estate.source s
      ON s.id_source = b.id_source
    WHERE s.id_source IS NULL;

    IF v_orphans <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % biens have invalid source foreign keys',
            v_orphans;
    END IF;

    RAISE NOTICE
        'PASS: bien -> source foreign keys are valid';
END
$$;


-- =============================================================================
-- 6. MANDATORY BIEN FIELDS
-- =============================================================================

DO $$
DECLARE
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bien
    WHERE reference_externe IS NULL
       OR BTRIM(reference_externe) = ''
       OR type_bien IS NULL
       OR BTRIM(type_bien) = ''
       OR id_source IS NULL;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % biens have missing mandatory fields',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: mandatory bien fields are populated';
END
$$;


-- =============================================================================
-- 7. PRICE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bien
    WHERE prix IS NOT NULL
      AND prix < 0;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % biens have negative price',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: bien prices are valid';
END
$$;


-- =============================================================================
-- 8. SURFACE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bien
    WHERE surface IS NOT NULL
      AND surface < 0;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % biens have negative surface',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: bien surfaces are valid';
END
$$;


-- =============================================================================
-- 9. ROOM COUNTS
-- =============================================================================

DO $$
DECLARE
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bien
    WHERE nb_pieces IS NOT NULL
      AND nb_pieces < 0;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % biens have invalid nb_pieces',
            v_invalid;
    END IF;

    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bien
    WHERE nb_chambres IS NOT NULL
      AND nb_chambres < 0;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % biens have invalid nb_chambres',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: room counts are valid';
END
$$;


-- =============================================================================
-- 10. DPE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bien
    WHERE dpe IS NOT NULL
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
            'OLTP DQ FAILED: % invalid DPE values found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: DPE values are valid';
END
$$;


-- =============================================================================
-- 11. LATITUDE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bien
    WHERE latitude IS NOT NULL
      AND latitude NOT BETWEEN -90 AND 90;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % invalid latitudes found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: latitude values are valid';
END
$$;


-- =============================================================================
-- 12. LONGITUDE DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bien
    WHERE longitude IS NOT NULL
      AND longitude NOT BETWEEN -180 AND 180;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % invalid longitudes found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: longitude values are valid';
END
$$;


-- =============================================================================
-- 13. STATUT DOMAIN
-- =============================================================================

DO $$
DECLARE
    v_invalid BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bien
    WHERE statut NOT IN (
        'ACTIF',
        'EXPIRE',
        'VENDU',
        'INDISPONIBLE'
    );

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'OLTP DQ FAILED: % invalid bien statuses found',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: bien statuses are valid';
END
$$;


-- =============================================================================
-- 14. CURRENT BATCH RECONCILIATION DETAILS
-- =============================================================================

SELECT
    current_setting(
        'real_estate.ingestion_batch'
    ) AS ingestion_batch,

    (
        SELECT COUNT(*)
        FROM staging.annonces
        WHERE ingestion_batch =
            current_setting('real_estate.ingestion_batch')
          AND quality_valid = TRUE
    ) AS staging_valid_annonces,

    (
        SELECT COUNT(*)
        FROM staging.annonces s
        JOIN real_estate.source src
          ON src.nom = 'GENERATEUR_ANNONCES'
         AND src.type_source = 'AUTRE'
        JOIN real_estate.bien b
          ON b.reference_externe = s.reference
         AND b.id_source = src.id_source
        WHERE s.ingestion_batch =
            current_setting('real_estate.ingestion_batch')
          AND s.quality_valid = TRUE
    ) AS oltp_matched_biens;


-- =============================================================================
-- 15. SOURCE SUMMARY
-- =============================================================================

SELECT
    s.id_source,
    s.nom,
    s.type_source,
    s.actif,
    s.niveau_confiance,
    COUNT(b.id_bien) AS total_biens
FROM real_estate.source s
LEFT JOIN real_estate.bien b
  ON b.id_source = s.id_source
WHERE s.nom = 'GENERATEUR_ANNONCES'
  AND s.type_source = 'AUTRE'
GROUP BY
    s.id_source,
    s.nom,
    s.type_source,
    s.actif,
    s.niveau_confiance
ORDER BY s.id_source;


-- =============================================================================
-- 16. BIEN STATUS DISTRIBUTION
-- =============================================================================

SELECT
    b.statut,
    COUNT(*) AS biens
FROM real_estate.bien b
JOIN real_estate.source s
  ON s.id_source = b.id_source
WHERE s.nom = 'GENERATEUR_ANNONCES'
  AND s.type_source = 'AUTRE'
GROUP BY b.statut
ORDER BY biens DESC, b.statut;


-- =============================================================================
-- 17. PROPERTY TYPE DISTRIBUTION
-- =============================================================================

SELECT
    b.type_bien,
    COUNT(*) AS biens
FROM real_estate.bien b
JOIN real_estate.source s
  ON s.id_source = b.id_source
WHERE s.nom = 'GENERATEUR_ANNONCES'
  AND s.type_source = 'AUTRE'
GROUP BY b.type_bien
ORDER BY biens DESC, b.type_bien;


-- =============================================================================
-- 18. CITY DISTRIBUTION
-- =============================================================================

SELECT
    b.ville,
    COUNT(*) AS biens
FROM real_estate.bien b
JOIN real_estate.source s
  ON s.id_source = b.id_source
WHERE s.nom = 'GENERATEUR_ANNONCES'
  AND s.type_source = 'AUTRE'
GROUP BY b.ville
ORDER BY biens DESC, b.ville;


-- =============================================================================
-- 19. NUMERIC SUMMARY
-- =============================================================================

SELECT
    COUNT(*) AS total_biens,

    MIN(prix) AS min_price,
    MAX(prix) AS max_price,
    ROUND(AVG(prix), 2) AS avg_price,

    MIN(surface) AS min_surface,
    MAX(surface) AS max_surface,
    ROUND(AVG(surface), 2) AS avg_surface,

    COUNT(*) FILTER (
        WHERE dpe IS NULL
    ) AS missing_dpe,

    COUNT(*) FILTER (
        WHERE nb_chambres IS NULL
    ) AS missing_nb_chambres,

    COUNT(*) FILTER (
        WHERE latitude IS NULL
    ) AS missing_latitude,

    COUNT(*) FILTER (
        WHERE longitude IS NULL
    ) AS missing_longitude

FROM real_estate.bien b
JOIN real_estate.source s
  ON s.id_source = b.id_source
WHERE s.nom = 'GENERATEUR_ANNONCES'
  AND s.type_source = 'AUTRE';


-- =============================================================================
-- FINAL RESULT
-- =============================================================================

SELECT
    'PASS' AS status,

    current_setting(
        'real_estate.ingestion_batch'
    ) AS ingestion_batch,

    'OLTP data quality validated successfully' AS result;