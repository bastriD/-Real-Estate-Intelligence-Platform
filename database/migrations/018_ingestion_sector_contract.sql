-- Sector evidence through generated ingestion and its analytical projection.
-- Requires existing raw/staging schemas, warehouse 003, and migration 017.
-- No historical sector is inferred or backfilled from city/postcode alone.
\set ON_ERROR_STOP on
BEGIN;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM migration_control.schema_version WHERE version = '017') THEN
        RAISE EXCEPTION 'Migration 018 requires migration 017';
    END IF;
    IF EXISTS (SELECT 1 FROM migration_control.schema_version WHERE version = '018') THEN
        RAISE EXCEPTION 'Migration 018 already applied';
    END IF;
END;
$$;

ALTER TABLE raw.annonces ADD COLUMN secteur_code TEXT;
ALTER TABLE raw.recherches ADD COLUMN secteur_code TEXT;
ALTER TABLE staging.annonces ADD COLUMN secteur_code TEXT;
ALTER TABLE staging.recherches ADD COLUMN secteur_code TEXT;

COMMENT ON COLUMN raw.annonces.secteur_code IS
    'Explicit source sector identity (geo-v1); absent legacy evidence stays NULL.';
COMMENT ON COLUMN staging.annonces.secteur_code IS
    'Source sector identity resolved against active canonical geography by the OLTP loader.';

ALTER TABLE warehouse.dim_bien ADD COLUMN secteur_key BIGINT NOT NULL DEFAULT 0
    REFERENCES warehouse.dim_secteur(secteur_key);
CREATE TABLE warehouse.bridge_demande_version_secteur (
    demande_version_key BIGINT NOT NULL REFERENCES warehouse.dim_demande_version(demande_version_key),
    secteur_key BIGINT NOT NULL REFERENCES warehouse.dim_secteur(secteur_key),
    PRIMARY KEY (demande_version_key, secteur_key)
);
COMMENT ON TABLE warehouse.bridge_demande_version_secteur IS
    'Acceptable alternative sectors for each search version; independent of mandate coverage.';
COMMENT ON COLUMN warehouse.dim_bien.secteur_key IS
    'Current reviewed/source-resolved property geography; 0 means unmapped, not a matching wildcard.';

INSERT INTO migration_control.schema_version(version, description)
VALUES ('018', 'Carry explicit sector evidence through ingestion and warehouse');
COMMIT;
