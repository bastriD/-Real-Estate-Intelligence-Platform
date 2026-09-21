-- =============================================================================
-- Migration 017
-- Deterministic enrichment of legacy search criteria and versioned geography.
--
-- SOURCE:
-- Fil_Rouge_Depart legacy search descriptions migrated conservatively by 002.
--
-- PURPOSE:
-- - preserve description_recherche_legacy;
-- - enrich only original LEGACY demande_version version 1 rows;
-- - structure deterministic hard search criteria;
-- - preserve flexible preferences in criteres_souhaites JSONB;
-- - model precise search geography as DemandeVersion N:N Secteur;
-- - preserve uncertainty, except the documented project Tn type convention.
--
-- Later business-created versions are NOT modified.
-- Migrations 001-016 remain immutable.
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;

DO $$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM migration_control.schema_version
        WHERE version = '016'
    ) <> 1 THEN
        RAISE EXCEPTION 'Migration 017 requires migration 016';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM migration_control.schema_version
        WHERE version = '017'
    ) THEN
        RAISE EXCEPTION 'Migration 017 has already been applied';
    END IF;
END;
$$;


-- =============================================================================
-- Versioned search geography
-- =============================================================================

CREATE TABLE real_estate.demande_version_secteur (
    id_demande_version BIGINT NOT NULL,
    id_secteur BIGINT NOT NULL,

    CONSTRAINT pk_demande_version_secteur
        PRIMARY KEY (id_demande_version, id_secteur),

    CONSTRAINT fk_demande_version_secteur_version
        FOREIGN KEY (id_demande_version)
        REFERENCES real_estate.demande_version(id_demande_version)
        ON DELETE CASCADE,

    CONSTRAINT fk_demande_version_secteur_secteur
        FOREIGN KEY (id_secteur)
        REFERENCES real_estate.secteur(id_secteur)
        ON DELETE RESTRICT
);

CREATE INDEX idx_demande_version_secteur_secteur
    ON real_estate.demande_version_secteur(id_secteur);

-- Precise matching requires explicit property geography. Never infer a quarter
-- from a postcode: several canonical sectors share the same postcode.
ALTER TABLE real_estate.bien ADD COLUMN id_secteur BIGINT;
ALTER TABLE real_estate.bien ADD CONSTRAINT fk_bien_secteur
    FOREIGN KEY (id_secteur) REFERENCES real_estate.secteur(id_secteur) ON DELETE RESTRICT;
CREATE INDEX idx_bien_secteur ON real_estate.bien(id_secteur) WHERE id_secteur IS NOT NULL;

-- Existing ingestion updates location without knowing the new sector field.
-- A corrected address must invalidate, not silently retain, a reviewed mapping.
CREATE FUNCTION real_estate.invalidate_bien_secteur_on_location_change()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.id_secteur IS NOT NULL AND (
        ROW(NEW.ville, NEW.adresse, NEW.code_postal, NEW.latitude, NEW.longitude)
        IS DISTINCT FROM ROW(OLD.ville, OLD.adresse, OLD.code_postal, OLD.latitude, OLD.longitude)
    ) THEN
        NEW.id_secteur := NULL;
        INSERT INTO real_estate.audit_log(table_name, operation, record_id, utilisateur,
            ancienne_valeur, nouvelle_valeur, contexte)
        VALUES ('bien', 'UPDATE', OLD.id_bien::TEXT, CURRENT_USER,
            jsonb_build_object('id_secteur', OLD.id_secteur), jsonb_build_object('id_secteur', NULL),
            jsonb_build_object('source', 'database_trigger', 'action', 'invalidate_bien_secteur'));
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER trg_invalidate_bien_secteur
BEFORE UPDATE OF ville, adresse, code_postal, latitude, longitude ON real_estate.bien
FOR EACH ROW EXECUTE FUNCTION real_estate.invalidate_bien_secteur_on_location_change();

COMMENT ON TABLE real_estate.demande_version_secteur IS
    'Versioned acceptable search sectors for a demande_version. Multiple rows represent alternative acceptable sectors.';

COMMENT ON COLUMN real_estate.demande_version_secteur.id_demande_version IS
    'Search criteria version owning this geographic criterion.';

COMMENT ON COLUMN real_estate.demande_version_secteur.id_secteur IS
    'Canonical acceptable sector referenced by the search version.';


-- =============================================================================
-- Defensive validation of the legacy source population
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.demande d
    JOIN real_estate.demande_version dv
      ON dv.id_demande = d.id_demande
    WHERE d.origine = 'LEGACY'
      AND dv.numero_version = 1
      AND dv.description_recherche_legacy IS NOT NULL
      AND LENGTH(TRIM(dv.description_recherche_legacy)) > 0;

    IF v_count <> 17 THEN
        RAISE EXCEPTION
            'Migration 017 expected 17 original LEGACY version-1 searches, found %',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- Structured deterministic criteria (retrieval versus ranking is application policy)
--
-- T2/T3/T4/T5 are interpreted as Appartement + number of rooms.
-- This is a project vocabulary convention; Tn alone is not proof of dwelling type.
-- Explicit Maison / Villa / Loft / Appartement values are preserved using the
-- canonical property-type vocabulary already used by real_estate.bien.
--
-- Only criteria explicitly present in the original description are populated.
-- =============================================================================

-- Check exact source identity/content, not merely a population count.
CREATE TEMP TABLE enrichment_017_source(reference_demande TEXT PRIMARY KEY, description TEXT) ON COMMIT DROP;
INSERT INTO enrichment_017_source VALUES
    ('LEGACY-DEMANDE-1', 'T3 Ecusson, budget 320000, 65m2 min, balcon, calme, DPE C max'),
    ('LEGACY-DEMANDE-2', 'T4 Croix-Rousse, budget 450000, 85m2, terrasse ou jardin'),
    ('LEGACY-DEMANDE-3', 'T2 Beaux-Arts, budget 280000, 45m2 min, lumineux, proche tram'),
    ('LEGACY-DEMANDE-4', 'Maison Ile de Nantes, budget 390000, 3 chambres, petit exterieur'),
    ('LEGACY-DEMANDE-5', 'T4 Port Marianne, budget 550000, 90m2, parking, ascenseur, vue'),
    ('LEGACY-DEMANDE-6', 'Maison Castelnau, budget 240000, 80m2, jardin, travaux OK'),
    ('LEGACY-DEMANDE-7', 'Loft Confluence, budget 610000, 100m2, standing, terrasse'),
    ('LEGACY-DEMANDE-8', 'T3 Ecusson ou Beaux-Arts, budget 300000, charme ancien, poutres'),
    ('LEGACY-DEMANDE-9', 'T3 Sete centre, budget 260000, vue mer si possible, 60m2'),
    ('LEGACY-DEMANDE-10', 'Villa Lattes, budget 420000, 4 pieces, piscine ou jardin sud'),
    ('LEGACY-DEMANDE-11', 'T3 Port Marianne, budget 350000, neuf ou recent, balcon, parking'),
    ('LEGACY-DEMANDE-12', 'Appartement Nantes, budget 480000, 4 pieces, dernier etage'),
    ('LEGACY-DEMANDE-14', 'T5 Confluence, budget 700000, 120m2, prestations haut de gamme'),
    ('LEGACY-DEMANDE-15', 'T3 Ecusson, budget 310000, ancien renove, cave appreciee'),
    ('LEGACY-DEMANDE-16', 'Maison Sete, budget 290000, 3 pieces, garage'),
    ('LEGACY-DEMANDE-17', 'T2 Beaux-Arts, budget 260000, 45m2, balcon, DPE D max'),
    ('LEGACY-DEMANDE-18', 'Maison Castelnau, budget 330000, 90m2, 3 chambres, jardin');

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM enrichment_017_source e
        LEFT JOIN real_estate.demande d ON d.reference_demande = e.reference_demande AND d.origine = 'LEGACY'
        LEFT JOIN real_estate.demande_version dv ON dv.id_demande = d.id_demande AND dv.numero_version = 1
        WHERE dv.id_demande_version IS NULL OR dv.description_recherche_legacy IS DISTINCT FROM e.description
    ) THEN
        RAISE EXCEPTION 'Migration 017 source descriptions differ from the reviewed legacy baseline';
    END IF;
    -- A changed V1 must be reviewed, never silently overwritten by a data backfill.
    IF EXISTS (
        SELECT 1 FROM real_estate.demande_version dv JOIN real_estate.demande d USING(id_demande)
        JOIN enrichment_017_source e USING(reference_demande)
        WHERE dv.numero_version = 1 AND (
            dv.type_bien IS NOT NULL OR dv.surface_min IS NOT NULL OR dv.nb_pieces_min IS NOT NULL
            OR dv.nb_chambres_min IS NOT NULL OR dv.dpe_max IS NOT NULL
            OR dv.criteres_souhaites IS DISTINCT FROM '[]'::jsonb
        )
    ) THEN
        RAISE EXCEPTION 'Migration 017 refuses to overwrite already structured legacy V1 criteria';
    END IF;
END;
$$;

UPDATE real_estate.demande_version dv
SET
    type_bien = CASE d.reference_demande
        WHEN 'LEGACY-DEMANDE-1'  THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-2'  THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-3'  THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-4'  THEN 'Maison'
        WHEN 'LEGACY-DEMANDE-5'  THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-6'  THEN 'Maison'
        WHEN 'LEGACY-DEMANDE-7'  THEN 'Loft'
        WHEN 'LEGACY-DEMANDE-8'  THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-9'  THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-10' THEN 'Villa'
        WHEN 'LEGACY-DEMANDE-11' THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-12' THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-14' THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-15' THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-16' THEN 'Maison'
        WHEN 'LEGACY-DEMANDE-17' THEN 'Appartement'
        WHEN 'LEGACY-DEMANDE-18' THEN 'Maison'
        ELSE dv.type_bien
    END,

    surface_min = CASE d.reference_demande
        WHEN 'LEGACY-DEMANDE-1'  THEN 65
        WHEN 'LEGACY-DEMANDE-2'  THEN 85
        WHEN 'LEGACY-DEMANDE-3'  THEN 45
        WHEN 'LEGACY-DEMANDE-5'  THEN 90
        WHEN 'LEGACY-DEMANDE-6'  THEN 80
        WHEN 'LEGACY-DEMANDE-7'  THEN 100
        WHEN 'LEGACY-DEMANDE-9'  THEN 60
        WHEN 'LEGACY-DEMANDE-12' THEN NULL
        WHEN 'LEGACY-DEMANDE-14' THEN 120
        WHEN 'LEGACY-DEMANDE-17' THEN 45
        WHEN 'LEGACY-DEMANDE-18' THEN 90
        ELSE dv.surface_min
    END,

    nb_pieces_min = CASE d.reference_demande
        WHEN 'LEGACY-DEMANDE-1'  THEN 3
        WHEN 'LEGACY-DEMANDE-2'  THEN 4
        WHEN 'LEGACY-DEMANDE-3'  THEN 2
        WHEN 'LEGACY-DEMANDE-5'  THEN 4
        WHEN 'LEGACY-DEMANDE-8'  THEN 3
        WHEN 'LEGACY-DEMANDE-9'  THEN 3
        WHEN 'LEGACY-DEMANDE-10' THEN 4
        WHEN 'LEGACY-DEMANDE-11' THEN 3
        WHEN 'LEGACY-DEMANDE-12' THEN 4
        WHEN 'LEGACY-DEMANDE-14' THEN 5
        WHEN 'LEGACY-DEMANDE-15' THEN 3
        WHEN 'LEGACY-DEMANDE-16' THEN 3
        WHEN 'LEGACY-DEMANDE-17' THEN 2
        ELSE dv.nb_pieces_min
    END,

    nb_chambres_min = CASE d.reference_demande
        WHEN 'LEGACY-DEMANDE-4'  THEN 3
        WHEN 'LEGACY-DEMANDE-18' THEN 3
        ELSE dv.nb_chambres_min
    END,

    dpe_max = CASE d.reference_demande
        WHEN 'LEGACY-DEMANDE-1'  THEN 'C'
        WHEN 'LEGACY-DEMANDE-17' THEN 'D'
        ELSE dv.dpe_max
    END

FROM real_estate.demande d
WHERE d.id_demande = dv.id_demande
  AND d.origine = 'LEGACY'
  AND dv.numero_version = 1;


-- =============================================================================
-- Flexible preferences
--
-- JSON arrays preserve the source meaning.
-- Alternatives expressed with "ou" remain a single alternative expression
-- rather than being transformed into two mandatory boolean requirements.
-- =============================================================================

UPDATE real_estate.demande_version dv
SET criteres_souhaites = CASE d.reference_demande

    WHEN 'LEGACY-DEMANDE-1'
        THEN '["balcon", "calme"]'::jsonb

    WHEN 'LEGACY-DEMANDE-2'
        THEN '["terrasse ou jardin"]'::jsonb

    WHEN 'LEGACY-DEMANDE-3'
        THEN '["lumineux", "proche tram"]'::jsonb

    WHEN 'LEGACY-DEMANDE-4'
        THEN '["petit exterieur"]'::jsonb

    WHEN 'LEGACY-DEMANDE-5'
        THEN '["parking", "ascenseur", "vue"]'::jsonb

    WHEN 'LEGACY-DEMANDE-6'
        THEN '["jardin", "travaux OK"]'::jsonb

    WHEN 'LEGACY-DEMANDE-7'
        THEN '["standing", "terrasse"]'::jsonb

    WHEN 'LEGACY-DEMANDE-8'
        THEN '["charme ancien", "poutres"]'::jsonb

    WHEN 'LEGACY-DEMANDE-9'
        THEN '["vue mer si possible"]'::jsonb

    WHEN 'LEGACY-DEMANDE-10'
        THEN '["piscine ou jardin sud"]'::jsonb

    WHEN 'LEGACY-DEMANDE-11'
        THEN '["neuf ou recent", "balcon", "parking"]'::jsonb

    WHEN 'LEGACY-DEMANDE-12'
        THEN '["dernier etage"]'::jsonb

    WHEN 'LEGACY-DEMANDE-14'
        THEN '["prestations haut de gamme"]'::jsonb

    WHEN 'LEGACY-DEMANDE-15'
        THEN '["ancien renove", "cave appreciee"]'::jsonb

    WHEN 'LEGACY-DEMANDE-16'
        THEN '["garage"]'::jsonb

    WHEN 'LEGACY-DEMANDE-17'
        THEN '["balcon"]'::jsonb

    WHEN 'LEGACY-DEMANDE-18'
        THEN '["jardin"]'::jsonb

    ELSE dv.criteres_souhaites
END

FROM real_estate.demande d
WHERE d.id_demande = dv.id_demande
  AND d.origine = 'LEGACY'
  AND dv.numero_version = 1;


-- =============================================================================
-- Precise sector mapping
--
-- Only explicitly named geographic sectors are mapped.
--
-- Not inferred:
-- - Appartement Nantes -> NOT automatically Ile de Nantes
-- - Maison Sete       -> NOT automatically Sete Centre
-- - Villa Lattes      -> no more precise sector stated
-- - Maison Castelnau  -> no more precise sector stated
--
-- "Ecusson ou Beaux-Arts" intentionally produces two rows.
-- =============================================================================

INSERT INTO real_estate.demande_version_secteur (
    id_demande_version,
    id_secteur
)
SELECT
    dv.id_demande_version,
    s.id_secteur
FROM real_estate.demande d
JOIN real_estate.demande_version dv
  ON dv.id_demande = d.id_demande
JOIN real_estate.secteur s
  ON (
        (d.reference_demande IN (
            'LEGACY-DEMANDE-1',
            'LEGACY-DEMANDE-15'
        )
         AND s.ville = 'Montpellier'
         AND s.quartier = 'Écusson')

     OR (d.reference_demande = 'LEGACY-DEMANDE-2'
         AND s.ville = 'Lyon'
         AND s.quartier = 'Croix-Rousse')

     OR (d.reference_demande IN (
            'LEGACY-DEMANDE-3',
            'LEGACY-DEMANDE-17'
        )
         AND s.ville = 'Montpellier'
         AND s.quartier = 'Beaux-Arts')

     OR (d.reference_demande = 'LEGACY-DEMANDE-4'
         AND s.ville = 'Nantes'
         AND s.quartier = 'Île de Nantes')

     OR (d.reference_demande IN (
            'LEGACY-DEMANDE-5',
            'LEGACY-DEMANDE-11'
        )
         AND s.ville = 'Montpellier'
         AND s.quartier = 'Port Marianne')

     OR (d.reference_demande IN (
            'LEGACY-DEMANDE-7',
            'LEGACY-DEMANDE-14'
        )
         AND s.ville = 'Lyon'
         AND s.quartier = 'Confluence')

     OR (d.reference_demande = 'LEGACY-DEMANDE-8'
         AND s.ville = 'Montpellier'
         AND s.quartier IN ('Écusson', 'Beaux-Arts'))

     OR (d.reference_demande = 'LEGACY-DEMANDE-9'
         AND s.ville = 'Sète'
         AND s.quartier = 'Centre')
     )
WHERE d.origine = 'LEGACY'
  AND dv.numero_version = 1
ON CONFLICT DO NOTHING;

-- Validate every intended mapping, not only the two-sector alternative.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM (VALUES (1,1), (2,1), (3,1), (4,1), (5,1), (7,1),
            (8,2), (9,1), (11,1), (14,1), (15,1), (17,1)) expected(legacy_id, sector_count)
        LEFT JOIN real_estate.demande d ON d.reference_demande = 'LEGACY-DEMANDE-' || expected.legacy_id
        LEFT JOIN real_estate.demande_version dv ON dv.id_demande = d.id_demande AND dv.numero_version = 1
        LEFT JOIN real_estate.demande_version_secteur ds ON ds.id_demande_version = dv.id_demande_version
        GROUP BY expected.legacy_id, expected.sector_count
        HAVING COUNT(ds.id_secteur) <> expected.sector_count
    ) THEN
        RAISE EXCEPTION 'Migration 017 could not resolve every precise legacy sector unambiguously';
    END IF;
END;
$$;


-- =============================================================================
-- Defensive post-enrichment validation
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN

    -- All 17 original legacy descriptions must still exist.

    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.demande d
    JOIN real_estate.demande_version dv
      ON dv.id_demande = d.id_demande
    WHERE d.origine = 'LEGACY'
      AND dv.numero_version = 1
      AND dv.description_recherche_legacy IS NOT NULL
      AND LENGTH(TRIM(dv.description_recherche_legacy)) > 0;

    IF v_count <> 17 THEN
        RAISE EXCEPTION
            'Migration 017 corrupted legacy descriptions: expected 17, found %',
            v_count;
    END IF;


    -- Every original legacy V1 search must now have a property type.

    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.demande d
    JOIN real_estate.demande_version dv
      ON dv.id_demande = d.id_demande
    WHERE d.origine = 'LEGACY'
      AND dv.numero_version = 1
      AND dv.type_bien IS NULL;

    IF v_count <> 0 THEN
        RAISE EXCEPTION
            'Migration 017 left % LEGACY V1 searches without type_bien',
            v_count;
    END IF;


    -- Ecusson ou Beaux-Arts must preserve two acceptable sectors.

    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.demande d
    JOIN real_estate.demande_version dv
      ON dv.id_demande = d.id_demande
    JOIN real_estate.demande_version_secteur dvs
      ON dvs.id_demande_version = dv.id_demande_version
    WHERE d.reference_demande = 'LEGACY-DEMANDE-8'
      AND dv.numero_version = 1;

    IF v_count <> 2 THEN
        RAISE EXCEPTION
            'Migration 017 expected 2 sectors for LEGACY-DEMANDE-8, found %',
            v_count;
    END IF;


    -- Later runtime/business versions must not receive migration sector rows.

    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.demande d
    JOIN real_estate.demande_version dv
      ON dv.id_demande = d.id_demande
    JOIN real_estate.demande_version_secteur dvs
      ON dvs.id_demande_version = dv.id_demande_version
    WHERE d.origine = 'LEGACY'
      AND dv.numero_version <> 1;

    IF v_count <> 0 THEN
        RAISE EXCEPTION
            'Migration 017 incorrectly enriched % later demande versions',
            v_count;
    END IF;

END;
$$;


-- =============================================================================
-- Migration registry
-- =============================================================================

INSERT INTO migration_control.schema_version (
    version,
    description
)
VALUES (
    '017',
    'Enrich legacy search criteria and add versioned demande sector geography'
);

COMMIT;
