-- Read-only sector reconciliation. An optional batch limits DAG checks;
-- a standalone CI invocation checks all sector-bearing generated rows.
\set ON_ERROR_STOP on
\if :{?ingestion_batch}
\else
\set ingestion_batch ''
\endif
SELECT set_config('real_estate.sector_check_batch', :'ingestion_batch', false);

SELECT secteur_code FROM raw.annonces LIMIT 0;
SELECT secteur_code FROM raw.recherches LIMIT 0;
SELECT secteur_code FROM staging.annonces LIMIT 0;
SELECT secteur_code FROM staging.recherches LIMIT 0;

DO $$
DECLARE
    batch TEXT := current_setting('real_estate.sector_check_batch');
BEGIN
    IF NOT EXISTS (SELECT 1 FROM migration_control.schema_version WHERE version = '018') THEN
        RAISE EXCEPTION 'Sector reconciliation requires migration 018';
    END IF;

    IF EXISTS (
        SELECT 1 FROM staging.recherches sr
        LEFT JOIN real_estate.demande_version dv ON dv.source_recherche_ref = sr.reference
             AND dv.ingestion_batch = sr.ingestion_batch
        WHERE sr.quality_valid AND sr.secteur_code IS NOT NULL
          AND (batch = '' OR sr.ingestion_batch = batch)
          AND (dv.id_demande_version IS NULL OR (
              SELECT COUNT(*) FROM real_estate.demande_version_secteur link
              WHERE link.id_demande_version = dv.id_demande_version
          ) <> 1)
    ) THEN
        RAISE EXCEPTION 'Generated sector-bearing searches must have exactly one loaded sector';
    END IF;

    IF EXISTS (
        SELECT 1 FROM staging.annonces sa
        LEFT JOIN staging.recherches sr ON sr.reference = sa.recherche_ref
             AND sr.ingestion_batch = sa.ingestion_batch AND sr.quality_valid
        LEFT JOIN real_estate.demande_version dv ON dv.source_recherche_ref = sr.reference
             AND dv.ingestion_batch = sr.ingestion_batch
        LEFT JOIN real_estate.demande_version_secteur link ON link.id_demande_version = dv.id_demande_version
        LEFT JOIN real_estate.source source ON source.nom = 'GENERATEUR_ANNONCES' AND source.type_source = 'AUTRE'
        LEFT JOIN real_estate.bien b ON b.id_source = source.id_source AND b.reference_externe = sa.reference
        LEFT JOIN real_estate.secteur sector ON sector.id_secteur = b.id_secteur
        WHERE sa.quality_valid AND sa.secteur_code IS NOT NULL
          AND (batch = '' OR sa.ingestion_batch = batch)
          AND (sa.secteur_code IS DISTINCT FROM sr.secteur_code
               OR b.id_secteur IS NULL OR b.id_secteur IS DISTINCT FROM link.id_secteur
               OR LOWER(TRIM(b.ville)) IS DISTINCT FROM LOWER(TRIM(sector.ville))
               OR b.code_postal IS DISTINCT FROM sector.code_postal)
    ) THEN
        RAISE EXCEPTION 'Generated property/search sector reconciliation failed';
    END IF;
END;
$$;

SELECT COUNT(*) AS sector_bearing_annonces_checked
FROM staging.annonces
WHERE quality_valid AND secteur_code IS NOT NULL
  AND (current_setting('real_estate.sector_check_batch') = ''
       OR ingestion_batch = current_setting('real_estate.sector_check_batch'));
