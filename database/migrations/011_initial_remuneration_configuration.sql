BEGIN;

-- =============================================================================
-- Migration 011
-- Initial approved remuneration configuration
--
-- Purpose:
--   Promote the validated project remuneration rules from example/test values
--   into the first operational configuration used by the backend.
--
-- Important distinction:
--
--   Migration 010 created the structures and explicitly did NOT seed the
--   proposed values as production configuration.
--
--   Migration 011 is the explicit project decision that approves the following
--   baseline configuration for operational use.
--
-- Effective date:
--   2026-01-01
--
-- Company fees:
--
--   H = F + t * P
--
--   F = 3000 EUR
--   t = 2.5%
--
-- Hunter remuneration:
--
--   - computed as a percentage of company fees H;
--   - never directly from purchase price;
--   - default grid selected by purchase-price band;
--   - final rate modulated by seniority and five-factor performance;
--   - final rate bounded between 20% and 60%.
--
-- Five mandatory performance criteria:
--
--   1. Mandat -> authentic deed delay
--   2. Exclusivity
--   3. Successful sales
--   4. Signed Mandats
--   5. Visits before purchase
--
-- Existing legacy hunter-specific commission rows remain HISTORIQUE.
-- They are NOT promoted or modified by this migration.
-- =============================================================================


-- =============================================================================
-- 1. Initial approved company-fee configuration
--
-- Formula:
--
--   H = 3000 + 0.025 * purchase_price
--
-- Example:
--
--   purchase price = 420000
--   H = 3000 + 0.025 * 420000
--   H = 13500
-- =============================================================================

INSERT INTO real_estate.parametres_honoraires (
    date_debut_validite,
    date_fin_validite,
    montant_fixe,
    taux_pourcentage,
    actif
)
VALUES (
    DATE '2026-01-01',
    NULL,
    3000.00,
    0.025000,
    TRUE
);


-- =============================================================================
-- 2. Initial approved remuneration/performance configuration
--
-- Rolling performance window:
--   12 months
--
-- Weights:
--
--   delay       25%
--   exclusivity 10%
--   sales       25%
--   mandates    15%
--   visits      25%
--
-- Total = 100%
--
-- Exclusivity score:
--
--   exclusive     = 100
--   non-exclusive = 60
--
-- Volume scoring:
--
--   successful sale = +20 points
--   signed Mandat    = +10 points
--
-- Seniority:
--
--   +2% per completed year
--   capped at +10%
--
-- Performance modulation:
--
--   pivot = 50
--   amplitude = +/-20%
--
-- Final remuneration-rate bounds:
--
--   floor   = 20%
--   ceiling = 60%
-- =============================================================================

INSERT INTO real_estate.parametres_remuneration (
    date_debut_validite,
    date_fin_validite,
    fenetre_mois,

    poids_delai,
    poids_exclusivite,
    poids_ventes,
    poids_mandats,
    poids_visites,

    note_exclusif,
    note_non_exclusif,

    points_par_vente,
    points_par_mandat,

    taux_anciennete_par_annee,
    plafond_anciennete,

    score_pivot,
    amplitude_performance,

    taux_plancher,
    taux_plafond,

    actif
)
VALUES (
    DATE '2026-01-01',
    NULL,
    12,

    0.250000,
    0.100000,
    0.250000,
    0.150000,
    0.250000,

    100.00,
    60.00,

    20.00,
    10.00,

    0.020000,
    0.100000,

    50.00,
    0.200000,

    0.200000,
    0.600000,

    TRUE
);


-- =============================================================================
-- 3. Delay-performance scoring bands
--
-- Criterion:
--   DELAI_SEMAINES
--
-- Lower delay is better.
--
-- Evaluation order:
--
--   <= 12 weeks  -> 100
--   <= 20 weeks  ->  80
--   <= 28 weeks  ->  60
--   <= 36 weeks  ->  40
--   <= 48 weeks  ->  20
--   >  48 weeks  ->   0
--
-- borne_max NULL represents the open-ended final band.
-- =============================================================================

INSERT INTO real_estate.palier_performance (
    id_parametres_remuneration,
    critere,
    ordre,
    borne_max,
    note
)
SELECT
    p.id_parametres_remuneration,
    values_to_insert.critere,
    values_to_insert.ordre,
    values_to_insert.borne_max,
    values_to_insert.note
FROM real_estate.parametres_remuneration p
CROSS JOIN (
    VALUES
        ('DELAI_SEMAINES', 1, 12,   100.00),
        ('DELAI_SEMAINES', 2, 20,    80.00),
        ('DELAI_SEMAINES', 3, 28,    60.00),
        ('DELAI_SEMAINES', 4, 36,    40.00),
        ('DELAI_SEMAINES', 5, 48,    20.00),
        ('DELAI_SEMAINES', 6, NULL,   0.00)
) AS values_to_insert(
    critere,
    ordre,
    borne_max,
    note
)
WHERE p.date_debut_validite = DATE '2026-01-01'
  AND p.date_fin_validite IS NULL
  AND p.actif = TRUE;


-- =============================================================================
-- 4. Visit-performance scoring bands
--
-- Criterion:
--   VISITES
--
-- Fewer visits before purchase is better.
--
-- Evaluation order:
--
--   <= 3 visits   -> 100
--   <= 6 visits   ->  80
--   <= 9 visits   ->  60
--   <= 12 visits  ->  40
--   <= 15 visits  ->  20
--   >  15 visits  ->   0
-- =============================================================================

INSERT INTO real_estate.palier_performance (
    id_parametres_remuneration,
    critere,
    ordre,
    borne_max,
    note
)
SELECT
    p.id_parametres_remuneration,
    values_to_insert.critere,
    values_to_insert.ordre,
    values_to_insert.borne_max,
    values_to_insert.note
FROM real_estate.parametres_remuneration p
CROSS JOIN (
    VALUES
        ('VISITES', 1, 3,    100.00),
        ('VISITES', 2, 6,     80.00),
        ('VISITES', 3, 9,     60.00),
        ('VISITES', 4, 12,    40.00),
        ('VISITES', 5, 15,    20.00),
        ('VISITES', 6, NULL,   0.00)
) AS values_to_insert(
    critere,
    ordre,
    borne_max,
    note
)
WHERE p.date_debut_validite = DATE '2026-01-01'
  AND p.date_fin_validite IS NULL
  AND p.actif = TRUE;


-- =============================================================================
-- 5. Initial approved DEFAULT remuneration grid
--
-- Scope:
--   id_chasseur IS NULL
--
-- This is the default operational grid.
--
-- Price-range convention:
--
--   lower bound inclusive
--   upper bound exclusive
--
--   [0, 200000)       -> 30%
--   [200000, 350000)  -> 35%
--   [350000, 500000)  -> 40%
--   [500000, 750000)  -> 45%
--   [750000, infinity)-> 50%
--
-- These percentages apply to company fees, not purchase price.
--
-- Existing hunter-specific HISTORIQUE rows remain untouched.
-- =============================================================================

INSERT INTO real_estate.bareme_commission (
    montant_min,
    montant_max,
    taux_commission,
    montant_fixe,
    date_debut_validite,
    date_fin_validite,
    actif,
    id_chasseur,
    statut_usage
)
VALUES
    (
        0.00,
        200000.00,
        0.3000,
        0.00,
        DATE '2026-01-01',
        NULL,
        TRUE,
        NULL,
        'APPROUVE'
    ),
    (
        200000.00,
        350000.00,
        0.3500,
        0.00,
        DATE '2026-01-01',
        NULL,
        TRUE,
        NULL,
        'APPROUVE'
    ),
    (
        350000.00,
        500000.00,
        0.4000,
        0.00,
        DATE '2026-01-01',
        NULL,
        TRUE,
        NULL,
        'APPROUVE'
    ),
    (
        500000.00,
        750000.00,
        0.4500,
        0.00,
        DATE '2026-01-01',
        NULL,
        TRUE,
        NULL,
        'APPROUVE'
    ),
    (
        750000.00,
        NULL,
        0.5000,
        0.00,
        DATE '2026-01-01',
        NULL,
        TRUE,
        NULL,
        'APPROUVE'
    );


-- =============================================================================
-- 6. Safety validations
--
-- These checks deliberately fail the migration if the configuration inserted
-- above does not match the expected baseline.
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.parametres_honoraires
    WHERE date_debut_validite = DATE '2026-01-01'
      AND date_fin_validite IS NULL
      AND montant_fixe = 3000.00
      AND taux_pourcentage = 0.025000
      AND actif = TRUE;

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'Expected exactly one active initial company-fee configuration, found %',
            v_count;
    END IF;
END;
$$;


DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.parametres_remuneration
    WHERE date_debut_validite = DATE '2026-01-01'
      AND date_fin_validite IS NULL
      AND fenetre_mois = 12
      AND poids_delai = 0.250000
      AND poids_exclusivite = 0.100000
      AND poids_ventes = 0.250000
      AND poids_mandats = 0.150000
      AND poids_visites = 0.250000
      AND actif = TRUE;

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'Expected exactly one active initial remuneration configuration, found %',
            v_count;
    END IF;
END;
$$;


DO $$
DECLARE
    v_param_id BIGINT;
    v_count INTEGER;
BEGIN
    SELECT id_parametres_remuneration
    INTO v_param_id
    FROM real_estate.parametres_remuneration
    WHERE date_debut_validite = DATE '2026-01-01'
      AND date_fin_validite IS NULL
      AND actif = TRUE;

    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.palier_performance
    WHERE id_parametres_remuneration = v_param_id;

    IF v_count <> 12 THEN
        RAISE EXCEPTION
            'Expected 12 performance bands for initial configuration, found %',
            v_count;
    END IF;
END;
$$;


DO $$
DECLARE
    v_delay_count INTEGER;
    v_visit_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_delay_count
    FROM real_estate.palier_performance pp
    JOIN real_estate.parametres_remuneration pr
      ON pr.id_parametres_remuneration =
         pp.id_parametres_remuneration
    WHERE pr.date_debut_validite = DATE '2026-01-01'
      AND pr.date_fin_validite IS NULL
      AND pr.actif = TRUE
      AND pp.critere = 'DELAI_SEMAINES';

    SELECT COUNT(*)
    INTO v_visit_count
    FROM real_estate.palier_performance pp
    JOIN real_estate.parametres_remuneration pr
      ON pr.id_parametres_remuneration =
         pp.id_parametres_remuneration
    WHERE pr.date_debut_validite = DATE '2026-01-01'
      AND pr.date_fin_validite IS NULL
      AND pr.actif = TRUE
      AND pp.critere = 'VISITES';

    IF v_delay_count <> 6 THEN
        RAISE EXCEPTION
            'Expected 6 DELAI_SEMAINES bands, found %',
            v_delay_count;
    END IF;

    IF v_visit_count <> 6 THEN
        RAISE EXCEPTION
            'Expected 6 VISITES bands, found %',
            v_visit_count;
    END IF;
END;
$$;


DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.bareme_commission
    WHERE id_chasseur IS NULL
      AND statut_usage = 'APPROUVE'
      AND date_debut_validite = DATE '2026-01-01'
      AND date_fin_validite IS NULL
      AND actif = TRUE;

    IF v_count <> 5 THEN
        RAISE EXCEPTION
            'Expected 5 approved default remuneration-grid bands, found %',
            v_count;
    END IF;
END;
$$;


DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.bareme_commission
    WHERE id_chasseur IS NOT NULL
      AND statut_usage <> 'HISTORIQUE';

    IF v_count <> 0 THEN
        RAISE EXCEPTION
            'Legacy hunter-specific rows must remain HISTORIQUE; found % operational rows',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- 7. Configuration documentation
-- =============================================================================

COMMENT ON TABLE real_estate.parametres_honoraires IS
    'Versioned company-fee configuration. Initial operational baseline approved from 2026-01-01: 3000 EUR + 2.5 percent of purchase price.';

COMMENT ON TABLE real_estate.parametres_remuneration IS
    'Versioned remuneration configuration controlling five-factor performance, seniority modulation, and final remuneration-rate bounds.';

COMMENT ON TABLE real_estate.palier_performance IS
    'Versioned performance thresholds for DELAI_SEMAINES and VISITES. Initial baseline approved from 2026-01-01.';

COMMENT ON TABLE real_estate.bareme_commission IS
    'Commission grids. HISTORIQUE rows preserve legacy values; APPROUVE rows are operational. Initial default approved grid applies percentages to company fees.';


-- =============================================================================
-- 8. Migration registry
-- =============================================================================

INSERT INTO migration_control.schema_version (
    version,
    description
)
VALUES (
    '011',
    'Seed initial approved remuneration business configuration'
);


COMMIT;