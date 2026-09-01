-- =============================================================================
-- 005_demande_pre_mandat.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Align the OLTP demand lifecycle with the official business process.
--
-- Official process:
--   1. A prospect submits a search request.
--   2. The request is recorded.
--   3. A hunter is assigned / accepts the request.
--   4. Initial matching can already be performed.
--   5. Criteria are refined.
--   6. The mandate is signed afterwards.
--
-- Therefore:
--   real_estate.demande MUST be allowed to exist before a mandat.
--
-- This migration:
--   - makes demande.id_mandat nullable;
--   - adds provenance information for LEGACY / GENERATED / API / MANUAL data;
--   - adds generator lineage fields to demande_version;
--   - keeps all existing legacy relationships unchanged;
--   - prepares STAGING recherches -> OLTP demande/demande_version.
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;

-- =============================================================================
-- 1. PRECONDITIONS
-- =============================================================================

DO $$
BEGIN
    IF to_regclass('real_estate.demande') IS NULL THEN
        RAISE EXCEPTION
            'Migration 005 aborted: real_estate.demande does not exist';
    END IF;

    IF to_regclass('real_estate.demande_version') IS NULL THEN
        RAISE EXCEPTION
            'Migration 005 aborted: real_estate.demande_version does not exist';
    END IF;

    IF to_regclass('migration_control.schema_version') IS NULL THEN
        RAISE EXCEPTION
            'Migration 005 aborted: migration_control.schema_version does not exist';
    END IF;
END
$$;


-- =============================================================================
-- 2. PREVENT ACCIDENTAL SECOND EXECUTION
-- =============================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM migration_control.schema_version
        WHERE version = '005'
    ) THEN
        RAISE EXCEPTION
            'Migration 005 has already been applied';
    END IF;
END
$$;


-- =============================================================================
-- 3. DEMANDE MAY EXIST BEFORE MANDAT
--
-- Existing legacy rows keep their current id_mandat.
-- Only the NOT NULL constraint is relaxed.
-- =============================================================================

ALTER TABLE real_estate.demande
    ALTER COLUMN id_mandat DROP NOT NULL;


-- =============================================================================
-- 4. DEMANDE PROVENANCE
--
-- This distinguishes:
--   LEGACY     -> migrated historical system
--   GENERATED  -> synthetic matching / ML dataset
--   API        -> future application/API-created demand
--   MANUEL     -> controlled manual creation
-- =============================================================================

ALTER TABLE real_estate.demande
    ADD COLUMN origine VARCHAR(20) NOT NULL DEFAULT 'API';

ALTER TABLE real_estate.demande
    ADD CONSTRAINT ck_demande_origine
    CHECK (
        origine IN (
            'LEGACY',
            'GENERATED',
            'API',
            'MANUEL'
        )
    );


-- Existing migrated demandes are known legacy data.
UPDATE real_estate.demande
SET origine = 'LEGACY'
WHERE reference_demande LIKE 'LEGACY-DEMANDE-%';


-- =============================================================================
-- 5. GENERATED SEARCH LINEAGE
--
-- source_recherche_ref preserves the generator's stable search reference:
--
--      staging.recherches.reference
--
-- ingestion_batch records the batch through which that search entered
-- the platform.
--
-- source_recherche_ref is globally unique for generated searches because
-- the generator creates stable REC-XXXXXXXX references.
-- =============================================================================

ALTER TABLE real_estate.demande_version
    ADD COLUMN source_recherche_ref VARCHAR(80);

ALTER TABLE real_estate.demande_version
    ADD COLUMN ingestion_batch TEXT;


CREATE UNIQUE INDEX uq_demande_version_source_recherche_ref
    ON real_estate.demande_version(source_recherche_ref)
    WHERE source_recherche_ref IS NOT NULL;


CREATE INDEX idx_demande_version_ingestion_batch
    ON real_estate.demande_version(ingestion_batch)
    WHERE ingestion_batch IS NOT NULL;


-- =============================================================================
-- 6. BUSINESS CONSISTENCY
--
-- A legacy demand must continue to have a mandate.
--
-- GENERATED/API/MANUEL demandes may exist before mandate signature.
-- =============================================================================

ALTER TABLE real_estate.demande
    ADD CONSTRAINT ck_demande_legacy_mandat
    CHECK (
        origine <> 'LEGACY'
        OR id_mandat IS NOT NULL
    );


-- =============================================================================
-- 7. VALIDATION
-- =============================================================================

DO $$
DECLARE
    legacy_demande_count INTEGER;
    legacy_without_mandat INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO legacy_demande_count
    FROM real_estate.demande
    WHERE origine = 'LEGACY';

    SELECT COUNT(*)
    INTO legacy_without_mandat
    FROM real_estate.demande
    WHERE origine = 'LEGACY'
      AND id_mandat IS NULL;

    IF legacy_demande_count <> 17 THEN
        RAISE EXCEPTION
            'Migration 005 validation failed: expected 17 legacy demandes, found %',
            legacy_demande_count;
    END IF;

    IF legacy_without_mandat <> 0 THEN
        RAISE EXCEPTION
            'Migration 005 validation failed: % legacy demandes have no mandate',
            legacy_without_mandat;
    END IF;

    RAISE NOTICE
        'PASS: 17 migrated legacy demandes remain linked to mandates';

    RAISE NOTICE
        'PASS: new demandes may now exist before mandate signature';
END
$$;


-- =============================================================================
-- 8. REGISTER MIGRATION
-- =============================================================================

INSERT INTO migration_control.schema_version (
    version,
    description
)
VALUES (
    '005',
    'Allow pre-mandate demandes and add generated-search lineage'
);


COMMIT;


-- =============================================================================
-- POST-MIGRATION REPORT
-- =============================================================================

SELECT
    version,
    description,
    applied_at
FROM migration_control.schema_version
ORDER BY version;


SELECT
    origine,
    COUNT(*) AS demandes,
    COUNT(id_mandat) AS avec_mandat,
    COUNT(*) - COUNT(id_mandat) AS sans_mandat
FROM real_estate.demande
GROUP BY origine
ORDER BY origine;