-- =============================================================================
-- 013_demande_client_ownership.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Introduce explicit business ownership for search requests (demandes).
--
-- Business lifecycle:
--   1. A client/prospect submits a search request.
--   2. The demande exists before any mandate is signed.
--   3. A hunter may be assigned and work on the demande.
--   4. Criteria may be revised by the client, hunter or system.
--   5. A mandate may be signed later.
--
-- Important distinction:
--
--   demande.id_client
--       -> stable business owner of the demande
--
--   demande_version.auteur_client_id
--       -> author of one particular criteria version
--
-- These concepts MUST NOT be conflated.
--
-- Historical treatment:
--   LEGACY:
--       Owner is deterministically recovered from the existing mandate.
--
--   GENERATED:
--       Existing synthetic matching/ML demandes remain ownerless.
--       No artificial client ownership is invented.
--
-- Business rules:
--   - LEGACY/API/MANUEL demandes require a client owner.
--   - GENERATED demandes may have no client owner.
--   - When a demande references a mandate, both must belong to the same client.
--
-- Runtime inventory before this migration:
--   LEGACY    : 17 total, 17 with mandate
--   GENERATED : 90 total, 0 with mandate
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
            'Migration 013 aborted: real_estate.demande does not exist';
    END IF;

    IF to_regclass('real_estate.client') IS NULL THEN
        RAISE EXCEPTION
            'Migration 013 aborted: real_estate.client does not exist';
    END IF;

    IF to_regclass('real_estate.mandat') IS NULL THEN
        RAISE EXCEPTION
            'Migration 013 aborted: real_estate.mandat does not exist';
    END IF;

    IF to_regclass('migration_control.schema_version') IS NULL THEN
        RAISE EXCEPTION
            'Migration 013 aborted: migration_control.schema_version does not exist';
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
        WHERE version = '013'
    ) THEN
        RAISE EXCEPTION
            'Migration 013 has already been applied';
    END IF;
END
$$;


-- =============================================================================
-- 3. ADD EXPLICIT CLIENT OWNERSHIP
--
-- Nullable at the physical level because GENERATED synthetic demandes are
-- intentionally allowed to exist without a real business client.
-- =============================================================================

ALTER TABLE real_estate.demande
    ADD COLUMN id_client BIGINT;


ALTER TABLE real_estate.demande
    ADD CONSTRAINT fk_demande_client
    FOREIGN KEY (id_client)
    REFERENCES real_estate.client(id_client)
    ON DELETE RESTRICT;


CREATE INDEX idx_demande_client
    ON real_estate.demande(id_client);


-- =============================================================================
-- 4. BACKFILL LEGACY OWNERSHIP
--
-- Migration 005 guarantees that LEGACY demandes remain linked to mandates.
-- Therefore mandate.id_client is authoritative for their historical owner.
--
-- GENERATED demandes are intentionally NOT modified.
-- =============================================================================

UPDATE real_estate.demande d
SET id_client = m.id_client
FROM real_estate.mandat m
WHERE d.id_mandat = m.id_mandat
  AND d.origine = 'LEGACY';


-- =============================================================================
-- 5. BUSINESS OWNERSHIP RULE
--
-- Real business demandes require a client owner.
--
-- GENERATED rows are synthetic search/matching data and may remain ownerless.
-- =============================================================================

ALTER TABLE real_estate.demande
    ADD CONSTRAINT ck_demande_client_owner
    CHECK (
        origine = 'GENERATED'
        OR id_client IS NOT NULL
    );


-- =============================================================================
-- 6. DATABASE-LEVEL MANDATE / CLIENT CONSISTENCY
--
-- PostgreSQL CHECK constraints cannot safely enforce cross-table equality.
-- A constraint trigger is therefore used.
--
-- If a demande references a mandate:
--
--     demande.id_client = mandat.id_client
--
-- GENERATED ownerless demandes may exist only while they have no mandate.
-- =============================================================================

CREATE OR REPLACE FUNCTION real_estate.validate_demande_mandat_client()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    mandat_client_id BIGINT;
BEGIN
    IF NEW.id_mandat IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT m.id_client
    INTO mandat_client_id
    FROM real_estate.mandat m
    WHERE m.id_mandat = NEW.id_mandat;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Mandat % does not exist',
            NEW.id_mandat;
    END IF;

    IF NEW.id_client IS NULL THEN
        RAISE EXCEPTION
            'Demande linked to mandat % must have a client owner',
            NEW.id_mandat;
    END IF;

    IF NEW.id_client <> mandat_client_id THEN
        RAISE EXCEPTION
            'Demande client % does not match mandat % client %',
            NEW.id_client,
            NEW.id_mandat,
            mandat_client_id;
    END IF;

    RETURN NEW;
END
$$;


CREATE CONSTRAINT TRIGGER trg_demande_mandat_client
AFTER INSERT OR UPDATE OF id_client, id_mandat
ON real_estate.demande
DEFERRABLE INITIALLY IMMEDIATE
FOR EACH ROW
EXECUTE FUNCTION real_estate.validate_demande_mandat_client();


-- =============================================================================
-- 7. VALIDATION
-- =============================================================================

DO $$
DECLARE
    legacy_count INTEGER;
    legacy_without_client INTEGER;
    legacy_mismatch INTEGER;

    generated_count INTEGER;
    generated_without_client INTEGER;

    invalid_business_owner INTEGER;
    mandate_client_mismatch INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO legacy_count
    FROM real_estate.demande
    WHERE origine = 'LEGACY';


    SELECT COUNT(*)
    INTO legacy_without_client
    FROM real_estate.demande
    WHERE origine = 'LEGACY'
      AND id_client IS NULL;


    SELECT COUNT(*)
    INTO legacy_mismatch
    FROM real_estate.demande d
    JOIN real_estate.mandat m
      ON m.id_mandat = d.id_mandat
    WHERE d.origine = 'LEGACY'
      AND d.id_client IS DISTINCT FROM m.id_client;


    SELECT COUNT(*)
    INTO generated_count
    FROM real_estate.demande
    WHERE origine = 'GENERATED';


    SELECT COUNT(*)
    INTO generated_without_client
    FROM real_estate.demande
    WHERE origine = 'GENERATED'
      AND id_client IS NULL;


    SELECT COUNT(*)
    INTO invalid_business_owner
    FROM real_estate.demande
    WHERE origine <> 'GENERATED'
      AND id_client IS NULL;


    SELECT COUNT(*)
    INTO mandate_client_mismatch
    FROM real_estate.demande d
    JOIN real_estate.mandat m
      ON m.id_mandat = d.id_mandat
    WHERE d.id_client IS NULL
       OR d.id_client <> m.id_client;


    IF legacy_count <> 17 THEN
        RAISE EXCEPTION
            'Migration 013 validation failed: expected 17 legacy demandes, found %',
            legacy_count;
    END IF;


    IF legacy_without_client <> 0 THEN
        RAISE EXCEPTION
            'Migration 013 validation failed: % legacy demandes have no client owner',
            legacy_without_client;
    END IF;


    IF legacy_mismatch <> 0 THEN
        RAISE EXCEPTION
            'Migration 013 validation failed: % legacy demandes disagree with mandate ownership',
            legacy_mismatch;
    END IF;


    IF invalid_business_owner <> 0 THEN
        RAISE EXCEPTION
            'Migration 013 validation failed: % business demandes have no client owner',
            invalid_business_owner;
    END IF;


    IF mandate_client_mismatch <> 0 THEN
        RAISE EXCEPTION
            'Migration 013 validation failed: % mandate-linked demandes have inconsistent ownership',
            mandate_client_mismatch;
    END IF;


    RAISE NOTICE
        'PASS: % legacy demandes have deterministic client ownership',
        legacy_count;

    RAISE NOTICE
        'PASS: % generated demandes preserved; % remain intentionally ownerless',
        generated_count,
        generated_without_client;

    RAISE NOTICE
        'PASS: all mandate-linked demandes match mandate client ownership';

    RAISE NOTICE
        'PASS: business demandes require explicit client ownership';
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
    '013',
    'Add explicit demande client ownership and mandate-client consistency'
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
WHERE version = '013';


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