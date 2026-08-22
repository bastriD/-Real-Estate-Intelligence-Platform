-- =============================================================================
-- 002_migrate_legacy_data.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Migrate valid data from the immutable legacy schema:
--
--       "Fil_Rouge_Depart"
--
--   into the normalized V2 OLTP schema:
--
--       real_estate
--
-- Principles:
--   - NEVER modify or delete legacy source data.
--   - Preserve traceability between legacy IDs and target records.
--   - Reject structurally invalid source rows rather than weakening V2.
--   - Never invent uncertain structured search criteria.
--   - Preserve legacy free-text search descriptions.
--   - Convert legacy commission percentages to target ratios.
--
-- Known legacy anomaly:
--   mandate 13 references utilisateur 3 as client,
--   but utilisateur 3 has role = 'chasseur'.
--   That mandate must be rejected from the clean target model.
--
-- Expected result from supplied StarterPack:
--   clients              : 18
--   chasseurs            : 6
--   secteurs             : 10
--   legacy mandats       : 18
--   migrated mandats     : 17
--   rejected mandats     : 1
--   demandes             : 17
--   demande_version      : 17
--   bareme_commission    : 6
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;

-- =============================================================================
-- 1. PRECONDITIONS
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.schemata
        WHERE schema_name = 'Fil_Rouge_Depart'
    ) THEN
        RAISE EXCEPTION
            'Migration 002 aborted: legacy schema Fil_Rouge_Depart is missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.schemata
        WHERE schema_name = 'real_estate'
    ) THEN
        RAISE EXCEPTION
            'Migration 002 aborted: target schema real_estate is missing';
    END IF;
END
$$;


-- =============================================================================
-- 2. MIGRATION CONTROL
--
-- Kept outside real_estate so the business schema remains exactly
-- the 14-table MPD baseline.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS migration_control;

CREATE TABLE IF NOT EXISTS migration_control.schema_version (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS migration_control.legacy_rejection (
    id_rejection BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    migration_version VARCHAR(20) NOT NULL,
    source_schema VARCHAR(120) NOT NULL,
    source_table VARCHAR(120) NOT NULL,
    source_id BIGINT NOT NULL,

    rejection_code VARCHAR(80) NOT NULL,
    rejection_reason TEXT NOT NULL,

    source_payload JSONB,

    rejected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_legacy_rejection
        UNIQUE (
            migration_version,
            source_schema,
            source_table,
            source_id,
            rejection_code
        )
);


-- Register migration 001 retrospectively if its schema is present.
INSERT INTO migration_control.schema_version (
    version,
    description
)
SELECT
    '001',
    'Initial real_estate PostgreSQL schema'
WHERE to_regclass('real_estate.client') IS NOT NULL
ON CONFLICT (version) DO NOTHING;


-- Prevent accidental second execution.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM migration_control.schema_version
        WHERE version = '002'
    ) THEN
        RAISE EXCEPTION
            'Migration 002 has already been applied';
    END IF;
END
$$;


-- =============================================================================
-- 3. TEMPORARY LEGACY-ID MAPPING TABLES
--
-- These exist only for the duration of the migration transaction.
-- =============================================================================

CREATE TEMP TABLE migration_client_map (
    legacy_id BIGINT PRIMARY KEY,
    target_id BIGINT NOT NULL UNIQUE
) ON COMMIT DROP;

CREATE TEMP TABLE migration_chasseur_map (
    legacy_id BIGINT PRIMARY KEY,
    target_id BIGINT NOT NULL UNIQUE
) ON COMMIT DROP;

CREATE TEMP TABLE migration_secteur_map (
    legacy_id BIGINT PRIMARY KEY,
    target_id BIGINT NOT NULL UNIQUE
) ON COMMIT DROP;

CREATE TEMP TABLE migration_mandat_map (
    legacy_id BIGINT PRIMARY KEY,
    target_id BIGINT NOT NULL UNIQUE
) ON COMMIT DROP;

CREATE TEMP TABLE migration_demande_map (
    legacy_mandat_id BIGINT PRIMARY KEY,
    target_id BIGINT NOT NULL UNIQUE
) ON COMMIT DROP;


-- =============================================================================
-- 4. CLIENTS
-- =============================================================================

INSERT INTO real_estate.client (
    nom,
    prenom,
    email,
    telephone,
    ville,
    date_creation,
    statut,
    consentement_contact
)
SELECT
    u.nom,
    u.prenom,
    u.email,
    u.telephone,
    u.ville,
    u.date_creation::timestamptz,
    'ACTIF',
    FALSE
FROM "Fil_Rouge_Depart".utilisateurs u
WHERE u.role = 'client'
ORDER BY u.id;


INSERT INTO migration_client_map (
    legacy_id,
    target_id
)
SELECT
    legacy.id,
    target.id_client
FROM "Fil_Rouge_Depart".utilisateurs legacy
JOIN real_estate.client target
  ON target.email = legacy.email
WHERE legacy.role = 'client';


-- =============================================================================
-- 5. CHASSEURS
--
-- Legacy date_creation is an account creation date, not proven to be
-- employment-entry date. We therefore do NOT reinterpret it as date_entree.
-- =============================================================================

INSERT INTO real_estate.chasseur (
    nom,
    prenom,
    email,
    telephone,
    date_entree,
    statut
)
SELECT
    u.nom,
    u.prenom,
    u.email,
    u.telephone,
    NULL,
    'ACTIF'
FROM "Fil_Rouge_Depart".utilisateurs u
WHERE u.role = 'chasseur'
ORDER BY u.id;


INSERT INTO migration_chasseur_map (
    legacy_id,
    target_id
)
SELECT
    legacy.id,
    target.id_chasseur
FROM "Fil_Rouge_Depart".utilisateurs legacy
JOIN real_estate.chasseur target
  ON target.email = legacy.email
WHERE legacy.role = 'chasseur';


-- =============================================================================
-- 6. SECTEURS
-- =============================================================================

INSERT INTO real_estate.secteur (
    pays,
    ville,
    quartier,
    code_postal,
    actif
)
SELECT
    'France',
    s.ville,
    s.quartier,
    s.code_postal,
    TRUE
FROM "Fil_Rouge_Depart".secteurs s
ORDER BY s.id;


INSERT INTO migration_secteur_map (
    legacy_id,
    target_id
)
SELECT
    legacy.id,
    target.id_secteur
FROM "Fil_Rouge_Depart".secteurs legacy
JOIN real_estate.secteur target
  ON target.pays = 'France'
 AND target.ville = legacy.ville
 AND target.code_postal = legacy.code_postal
 AND target.quartier IS NOT DISTINCT FROM legacy.quartier;


-- =============================================================================
-- 7. IDENTIFY AND RECORD INVALID LEGACY MANDATES
-- =============================================================================

INSERT INTO migration_control.legacy_rejection (
    migration_version,
    source_schema,
    source_table,
    source_id,
    rejection_code,
    rejection_reason,
    source_payload
)
SELECT
    '002',
    'Fil_Rouge_Depart',
    'mandats',
    m.id,
    'INVALID_CLIENT_ROLE',
    format(
        'mandats.client_id=%s references utilisateur role=%s instead of client',
        m.client_id,
        u.role
    ),
    jsonb_build_object(
        'mandat_id', m.id,
        'client_id', m.client_id,
        'actual_role', u.role::text,
        'chasseur_id', m.chasseur_id,
        'secteur_id', m.secteur_id,
        'exclusif', m.exclusif,
        'date_debut', m.date_debut,
        'statut', m.statut::text,
        'description_recherche', m.description_recherche
    )
FROM "Fil_Rouge_Depart".mandats m
JOIN "Fil_Rouge_Depart".utilisateurs u
  ON u.id = m.client_id
WHERE u.role <> 'client'
ON CONFLICT DO NOTHING;


-- Also reject any mandate whose chasseur_id does not identify a chasseur.
INSERT INTO migration_control.legacy_rejection (
    migration_version,
    source_schema,
    source_table,
    source_id,
    rejection_code,
    rejection_reason,
    source_payload
)
SELECT
    '002',
    'Fil_Rouge_Depart',
    'mandats',
    m.id,
    'INVALID_CHASSEUR_ROLE',
    format(
        'mandats.chasseur_id=%s references utilisateur role=%s instead of chasseur',
        m.chasseur_id,
        u.role
    ),
    jsonb_build_object(
        'mandat_id', m.id,
        'client_id', m.client_id,
        'chasseur_id', m.chasseur_id,
        'actual_role', u.role::text,
        'secteur_id', m.secteur_id,
        'exclusif', m.exclusif,
        'date_debut', m.date_debut,
        'statut', m.statut::text,
        'description_recherche', m.description_recherche
    )
FROM "Fil_Rouge_Depart".mandats m
JOIN "Fil_Rouge_Depart".utilisateurs u
  ON u.id = m.chasseur_id
WHERE u.role <> 'chasseur'
ON CONFLICT DO NOTHING;


-- =============================================================================
-- 8. MANDATS
--
-- Explicit migration assumptions:
--
-- date_signature:
--   legacy does not provide it.
--   date_debut is used as the best available contractual date.
--
-- mode_signature:
--   unknown in legacy -> INCONNU.
--
-- date_fin:
--   derived as date_debut + 6 months.
--
-- reference_mandat:
--   deterministic technical/business migration reference.
-- =============================================================================

INSERT INTO real_estate.mandat (
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
SELECT
    'LEGACY-MANDAT-' || m.id,

    CASE
        WHEN m.exclusif THEN 'EXCLUSIF'
        ELSE 'NON_EXCLUSIF'
    END,

    m.date_debut,

    'INCONNU',

    m.date_debut,

    (m.date_debut + INTERVAL '6 months')::date,

    CASE m.statut::text
        WHEN 'actif'     THEN 'ACTIF'
        WHEN 'suspendu'  THEN 'SUSPENDU'
        WHEN 'termine'   THEN 'TERMINE'
        WHEN 'expire'    THEN 'EXPIRE'
        ELSE 'ANNULE'
    END,

    NULL,

    client_map.target_id,
    chasseur_map.target_id

FROM "Fil_Rouge_Depart".mandats m

JOIN migration_client_map client_map
  ON client_map.legacy_id = m.client_id

JOIN migration_chasseur_map chasseur_map
  ON chasseur_map.legacy_id = m.chasseur_id

WHERE NOT EXISTS (
    SELECT 1
    FROM migration_control.legacy_rejection rejection
    WHERE rejection.migration_version = '002'
      AND rejection.source_schema = 'Fil_Rouge_Depart'
      AND rejection.source_table = 'mandats'
      AND rejection.source_id = m.id
)

ORDER BY m.id;


INSERT INTO migration_mandat_map (
    legacy_id,
    target_id
)
SELECT
    legacy.id,
    target.id_mandat
FROM "Fil_Rouge_Depart".mandats legacy
JOIN real_estate.mandat target
  ON target.reference_mandat = 'LEGACY-MANDAT-' || legacy.id;


-- =============================================================================
-- 9. MANDAT <-> SECTEUR
-- =============================================================================

INSERT INTO real_estate.mandat_secteur (
    id_mandat,
    id_secteur
)
SELECT
    mandat_map.target_id,
    secteur_map.target_id
FROM "Fil_Rouge_Depart".mandats legacy

JOIN migration_mandat_map mandat_map
  ON mandat_map.legacy_id = legacy.id

JOIN migration_secteur_map secteur_map
  ON secteur_map.legacy_id = legacy.secteur_id

WHERE legacy.secteur_id IS NOT NULL;


-- =============================================================================
-- 10. DEMANDES
-- =============================================================================

INSERT INTO real_estate.demande (
    reference_demande,
    date_creation,
    statut,
    id_mandat
)
SELECT
    'LEGACY-DEMANDE-' || legacy.id,

    legacy.date_debut::timestamptz,

    CASE legacy.statut::text
        WHEN 'actif'    THEN 'ACTIVE'
        WHEN 'suspendu' THEN 'SUSPENDUE'
        WHEN 'termine'  THEN 'CLOTUREE'
        WHEN 'expire'   THEN 'CLOTUREE'
        ELSE 'ANNULEE'
    END,

    mandat_map.target_id

FROM "Fil_Rouge_Depart".mandats legacy

JOIN migration_mandat_map mandat_map
  ON mandat_map.legacy_id = legacy.id

ORDER BY legacy.id;


INSERT INTO migration_demande_map (
    legacy_mandat_id,
    target_id
)
SELECT
    legacy.id,
    target.id_demande
FROM "Fil_Rouge_Depart".mandats legacy
JOIN real_estate.demande target
  ON target.reference_demande = 'LEGACY-DEMANDE-' || legacy.id;


-- =============================================================================
-- 11. INITIAL DEMANDE_VERSION
--
-- Only values directly supported by legacy structured data are migrated.
--
-- We DO migrate:
--   - sector city
--   - sector postal code
--   - client budget_max
--   - original free-text description
--
-- We DO NOT guess:
--   - type_bien
--   - surface_min
--   - pieces
--   - bedrooms
--   - DPE
--   - JSON preferences
--
-- Those may be extracted later by deterministic parsing / Python / AI,
-- while the original source text remains preserved.
-- =============================================================================

INSERT INTO real_estate.demande_version (
    numero_version,
    date_version,
    motif_modification,

    ville,
    code_postal,
    type_bien,

    budget_min,
    budget_max,
    surface_min,

    nb_pieces_min,
    nb_chambres_min,

    dpe_max,
    criteres_souhaites,

    description_recherche_legacy,

    active,

    id_demande,

    auteur_client_id,
    auteur_chasseur_id,
    auteur_systeme
)
SELECT
    1,

    CURRENT_TIMESTAMP,

    'Migration depuis le SI hérité',

    legacy_sector.ville,
    legacy_sector.code_postal,
    NULL,

    NULL,
    legacy_client.budget_max,
    NULL,

    NULL,
    NULL,

    NULL,
    '[]'::jsonb,

    legacy_mandat.description_recherche,

    TRUE,

    demande_map.target_id,

    NULL,
    NULL,
    TRUE

FROM "Fil_Rouge_Depart".mandats legacy_mandat

JOIN migration_demande_map demande_map
  ON demande_map.legacy_mandat_id = legacy_mandat.id

JOIN "Fil_Rouge_Depart".utilisateurs legacy_client
  ON legacy_client.id = legacy_mandat.client_id

LEFT JOIN "Fil_Rouge_Depart".secteurs legacy_sector
  ON legacy_sector.id = legacy_mandat.secteur_id

ORDER BY legacy_mandat.id;


-- =============================================================================
-- 12. INITIAL COMMISSION SCALE
--
-- Legacy taux_commission is stored as percentage:
--
--      2.50 = 2.50 %
--
-- Target stores a ratio:
--
--      0.0250 = 2.50 %
--
-- Therefore:
--
--      target = legacy / 100
--
-- Legacy has no commission-history start date.
-- date_creation is used as the earliest available source date and this
-- limitation must remain documented.
-- =============================================================================

INSERT INTO real_estate.bareme_commission (
    montant_min,
    montant_max,
    taux_commission,
    montant_fixe,
    date_debut_validite,
    date_fin_validite,
    actif,
    id_chasseur
)
SELECT
    0,
    NULL,
    (legacy.taux_commission / 100.0)::numeric(7,4),
    0,
    legacy.date_creation,
    NULL,
    TRUE,
    chasseur_map.target_id

FROM "Fil_Rouge_Depart".utilisateurs legacy

JOIN migration_chasseur_map chasseur_map
  ON chasseur_map.legacy_id = legacy.id

WHERE legacy.role = 'chasseur'
  AND legacy.taux_commission IS NOT NULL

ORDER BY legacy.id;


-- =============================================================================
-- 13. INTERNAL MIGRATION VALIDATION
-- =============================================================================

DO $$
DECLARE
    client_count INTEGER;
    chasseur_count INTEGER;
    secteur_count INTEGER;
    legacy_mandat_count INTEGER;
    migrated_mandat_count INTEGER;
    rejected_mandat_count INTEGER;
    demande_count INTEGER;
    version_count INTEGER;
    bareme_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO client_count
    FROM real_estate.client;

    IF client_count <> 18 THEN
        RAISE EXCEPTION
            'Migration validation failed: expected 18 clients, found %',
            client_count;
    END IF;


    SELECT COUNT(*)
    INTO chasseur_count
    FROM real_estate.chasseur;

    IF chasseur_count <> 6 THEN
        RAISE EXCEPTION
            'Migration validation failed: expected 6 chasseurs, found %',
            chasseur_count;
    END IF;


    SELECT COUNT(*)
    INTO secteur_count
    FROM real_estate.secteur;

    IF secteur_count <> 10 THEN
        RAISE EXCEPTION
            'Migration validation failed: expected 10 secteurs, found %',
            secteur_count;
    END IF;


    SELECT COUNT(*)
    INTO legacy_mandat_count
    FROM "Fil_Rouge_Depart".mandats;

    IF legacy_mandat_count <> 18 THEN
        RAISE EXCEPTION
            'Migration validation failed: expected 18 legacy mandates, found %',
            legacy_mandat_count;
    END IF;


    SELECT COUNT(*)
    INTO migrated_mandat_count
    FROM real_estate.mandat
    WHERE reference_mandat LIKE 'LEGACY-MANDAT-%';

    IF migrated_mandat_count <> 17 THEN
        RAISE EXCEPTION
            'Migration validation failed: expected 17 migrated mandates, found %',
            migrated_mandat_count;
    END IF;


    SELECT COUNT(DISTINCT source_id)
    INTO rejected_mandat_count
    FROM migration_control.legacy_rejection
    WHERE migration_version = '002'
      AND source_schema = 'Fil_Rouge_Depart'
      AND source_table = 'mandats';

    IF rejected_mandat_count <> 1 THEN
        RAISE EXCEPTION
            'Migration validation failed: expected 1 rejected mandate, found %',
            rejected_mandat_count;
    END IF;


    SELECT COUNT(*)
    INTO demande_count
    FROM real_estate.demande
    WHERE reference_demande LIKE 'LEGACY-DEMANDE-%';

    IF demande_count <> 17 THEN
        RAISE EXCEPTION
            'Migration validation failed: expected 17 demandes, found %',
            demande_count;
    END IF;


    SELECT COUNT(*)
    INTO version_count
    FROM real_estate.demande_version
    WHERE motif_modification = 'Migration depuis le SI hérité';

    IF version_count <> 17 THEN
        RAISE EXCEPTION
            'Migration validation failed: expected 17 demande versions, found %',
            version_count;
    END IF;


    SELECT COUNT(*)
    INTO bareme_count
    FROM real_estate.bareme_commission;

    IF bareme_count <> 6 THEN
        RAISE EXCEPTION
            'Migration validation failed: expected 6 commission scales, found %',
            bareme_count;
    END IF;


    RAISE NOTICE 'PASS: 18 clients migrated';
    RAISE NOTICE 'PASS: 6 chasseurs migrated';
    RAISE NOTICE 'PASS: 10 secteurs migrated';
    RAISE NOTICE 'PASS: 17 valid mandates migrated';
    RAISE NOTICE 'PASS: 1 invalid mandate rejected';
    RAISE NOTICE 'PASS: 17 demandes created';
    RAISE NOTICE 'PASS: 17 initial demande versions created';
    RAISE NOTICE 'PASS: 6 initial commission scales created';
END
$$;


-- =============================================================================
-- 14. REGISTER MIGRATION
-- =============================================================================

INSERT INTO migration_control.schema_version (
    version,
    description
)
VALUES (
    '002',
    'Migrate StarterPack legacy data into normalized real_estate V2 model'
);


COMMIT;


-- =============================================================================
-- 15. POST-MIGRATION REPORT
-- =============================================================================

SELECT
    version,
    description,
    applied_at
FROM migration_control.schema_version
ORDER BY version;


SELECT
    migration_version,
    source_table,
    source_id,
    rejection_code,
    rejection_reason
FROM migration_control.legacy_rejection
WHERE migration_version = '002'
ORDER BY source_table, source_id;


SELECT
    'client' AS entity,
    COUNT(*) AS migrated_rows
FROM real_estate.client

UNION ALL

SELECT
    'chasseur',
    COUNT(*)
FROM real_estate.chasseur

UNION ALL

SELECT
    'secteur',
    COUNT(*)
FROM real_estate.secteur

UNION ALL

SELECT
    'mandat',
    COUNT(*)
FROM real_estate.mandat

UNION ALL

SELECT
    'demande',
    COUNT(*)
FROM real_estate.demande

UNION ALL

SELECT
    'demande_version',
    COUNT(*)
FROM real_estate.demande_version

UNION ALL

SELECT
    'bareme_commission',
    COUNT(*)
FROM real_estate.bareme_commission

ORDER BY entity;