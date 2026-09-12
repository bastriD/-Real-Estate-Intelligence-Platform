BEGIN;

-- =============================================================================
-- Test 014
-- Initial remuneration configuration
--
-- Validates migration 011:
--
--   - approved company-fee parameters;
--   - approved remuneration/performance parameters;
--   - 6 delay scoring bands;
--   - 6 visit scoring bands;
--   - 5 default approved commission bands;
--   - legacy hunter-specific rows remain HISTORIQUE;
--   - overlap protections remain active.
--
-- This test is read-only apart from temporary statements executed inside the
-- surrounding transaction. Everything is rolled back at the end.
-- =============================================================================


-- =============================================================================
-- 1. Migration registry
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM migration_control.schema_version
    WHERE version = '011';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'Migration 011 must be registered exactly once, found %',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- 2. Company-fee configuration
--
-- Expected operational baseline:
--
--   H = 3000 + 2.5% * purchase_price
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
            'Expected one approved company-fee configuration, found %',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- 3. Remuneration/performance configuration
-- =============================================================================

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

      AND note_exclusif = 100.00
      AND note_non_exclusif = 60.00

      AND points_par_vente = 20.00
      AND points_par_mandat = 10.00

      AND taux_anciennete_par_annee = 0.020000
      AND plafond_anciennete = 0.100000

      AND score_pivot = 50.00
      AND amplitude_performance = 0.200000

      AND taux_plancher = 0.200000
      AND taux_plafond = 0.600000

      AND actif = TRUE;

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'Expected one approved remuneration configuration, found %',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- 4. Delay-performance bands
-- =============================================================================

DO $$
DECLARE
    v_param_id BIGINT;
    v_count INTEGER;
BEGIN
    SELECT id_parametres_remuneration
    INTO STRICT v_param_id
    FROM real_estate.parametres_remuneration
    WHERE date_debut_validite = DATE '2026-01-01'
      AND date_fin_validite IS NULL
      AND actif = TRUE;

    SELECT COUNT(*)
    INTO v_count
    FROM (
        VALUES
            (1, 12,   100.00::numeric),
            (2, 20,    80.00::numeric),
            (3, 28,    60.00::numeric),
            (4, 36,    40.00::numeric),
            (5, 48,    20.00::numeric),
            (6, NULL,   0.00::numeric)
    ) expected(
        ordre,
        borne_max,
        note
    )
    JOIN real_estate.palier_performance actual
      ON actual.id_parametres_remuneration = v_param_id
     AND actual.critere = 'DELAI_SEMAINES'
     AND actual.ordre = expected.ordre
     AND actual.borne_max IS NOT DISTINCT FROM expected.borne_max
     AND actual.note = expected.note;

    IF v_count <> 6 THEN
        RAISE EXCEPTION
            'Delay-performance configuration mismatch: expected 6 matching bands, found %',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- 5. Visit-performance bands
-- =============================================================================

DO $$
DECLARE
    v_param_id BIGINT;
    v_count INTEGER;
BEGIN
    SELECT id_parametres_remuneration
    INTO STRICT v_param_id
    FROM real_estate.parametres_remuneration
    WHERE date_debut_validite = DATE '2026-01-01'
      AND date_fin_validite IS NULL
      AND actif = TRUE;

    SELECT COUNT(*)
    INTO v_count
    FROM (
        VALUES
            (1, 3,    100.00::numeric),
            (2, 6,     80.00::numeric),
            (3, 9,     60.00::numeric),
            (4, 12,    40.00::numeric),
            (5, 15,    20.00::numeric),
            (6, NULL,   0.00::numeric)
    ) expected(
        ordre,
        borne_max,
        note
    )
    JOIN real_estate.palier_performance actual
      ON actual.id_parametres_remuneration = v_param_id
     AND actual.critere = 'VISITES'
     AND actual.ordre = expected.ordre
     AND actual.borne_max IS NOT DISTINCT FROM expected.borne_max
     AND actual.note = expected.note;

    IF v_count <> 6 THEN
        RAISE EXCEPTION
            'Visit-performance configuration mismatch: expected 6 matching bands, found %',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- 6. Approved default commission grid
--
-- Price bands:
--
--   [0,      200000) -> 30%
--   [200000, 350000) -> 35%
--   [350000, 500000) -> 40%
--   [500000, 750000) -> 45%
--   [750000, infinity)->50%
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM (
        VALUES
            (
                0.00::numeric,
                200000.00::numeric,
                0.3000::numeric
            ),
            (
                200000.00::numeric,
                350000.00::numeric,
                0.3500::numeric
            ),
            (
                350000.00::numeric,
                500000.00::numeric,
                0.4000::numeric
            ),
            (
                500000.00::numeric,
                750000.00::numeric,
                0.4500::numeric
            ),
            (
                750000.00::numeric,
                NULL::numeric,
                0.5000::numeric
            )
    ) expected(
        montant_min,
        montant_max,
        taux_commission
    )
    JOIN real_estate.bareme_commission actual
      ON actual.id_chasseur IS NULL
     AND actual.statut_usage = 'APPROUVE'
     AND actual.actif = TRUE
     AND actual.date_debut_validite = DATE '2026-01-01'
     AND actual.date_fin_validite IS NULL
     AND actual.montant_min = expected.montant_min
     AND actual.montant_max IS NOT DISTINCT FROM expected.montant_max
     AND actual.taux_commission = expected.taux_commission;

    IF v_count <> 5 THEN
        RAISE EXCEPTION
            'Approved default commission grid mismatch: expected 5 matching bands, found %',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- 7. Legacy rows remain historical
-- =============================================================================

DO $$
DECLARE
    v_legacy_total INTEGER;
    v_invalid INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_legacy_total
    FROM real_estate.bareme_commission
    WHERE id_chasseur IS NOT NULL;

    SELECT COUNT(*)
    INTO v_invalid
    FROM real_estate.bareme_commission
    WHERE id_chasseur IS NOT NULL
      AND statut_usage <> 'HISTORIQUE';

    IF v_legacy_total <> 6 THEN
        RAISE EXCEPTION
            'Expected 6 legacy hunter-specific commission rows, found %',
            v_legacy_total;
    END IF;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'Hunter-specific legacy rows must remain HISTORIQUE, found % invalid rows',
            v_invalid;
    END IF;
END;
$$;


-- =============================================================================
-- 8. Company-fee overlap protection
-- =============================================================================

DO $$
BEGIN
    BEGIN
        INSERT INTO real_estate.parametres_honoraires (
            date_debut_validite,
            date_fin_validite,
            montant_fixe,
            taux_pourcentage,
            actif
        )
        VALUES (
            DATE '2026-06-01',
            NULL,
            1000.00,
            0.010000,
            TRUE
        );

        RAISE EXCEPTION
            'Expected overlapping company-fee configuration to be rejected';

    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM =
                'Expected overlapping company-fee configuration to be rejected'
            THEN
                RAISE;
            END IF;
    END;
END;
$$;


-- =============================================================================
-- 9. Remuneration-parameter overlap protection
-- =============================================================================

DO $$
BEGIN
    BEGIN
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
            DATE '2026-06-01',
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

        RAISE EXCEPTION
            'Expected overlapping remuneration configuration to be rejected';

    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM =
                'Expected overlapping remuneration configuration to be rejected'
            THEN
                RAISE;
            END IF;
    END;
END;
$$;


-- =============================================================================
-- 10. Approved-grid overlap protection
-- =============================================================================

DO $$
BEGIN
    BEGIN
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
        VALUES (
            100000.00,
            250000.00,
            0.3300,
            0.00,
            DATE '2026-01-01',
            NULL,
            TRUE,
            NULL,
            'APPROUVE'
        );

        RAISE EXCEPTION
            'Expected overlapping approved commission band to be rejected';

    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM =
                'Expected overlapping approved commission band to be rejected'
            THEN
                RAISE;
            END IF;
    END;
END;
$$;


-- =============================================================================
-- 11. Worked baseline configuration check
--
-- Purchase price:
--   420000
--
-- Company fees:
--   3000 + (420000 * 0.025) = 13500
--
-- Applicable default base rate:
--   [350000, 500000) = 40%
-- =============================================================================

DO $$
DECLARE
    v_fees NUMERIC(14, 2);
    v_rate NUMERIC(7, 4);
BEGIN
    SELECT
        ROUND(
            ph.montant_fixe
            + (420000.00 * ph.taux_pourcentage),
            2
        )
    INTO STRICT v_fees
    FROM real_estate.parametres_honoraires ph
    WHERE ph.date_debut_validite <= DATE '2026-09-12'
      AND (
            ph.date_fin_validite IS NULL
            OR ph.date_fin_validite >= DATE '2026-09-12'
          )
      AND ph.actif = TRUE;

    IF v_fees <> 13500.00 THEN
        RAISE EXCEPTION
            'Expected company fees 13500.00 for 420000 purchase, got %',
            v_fees;
    END IF;

    SELECT b.taux_commission
    INTO STRICT v_rate
    FROM real_estate.bareme_commission b
    WHERE b.id_chasseur IS NULL
      AND b.statut_usage = 'APPROUVE'
      AND b.actif = TRUE

      AND b.date_debut_validite <= DATE '2026-09-12'
      AND (
            b.date_fin_validite IS NULL
            OR b.date_fin_validite >= DATE '2026-09-12'
          )

      AND 420000.00 >= b.montant_min
      AND (
            b.montant_max IS NULL
            OR 420000.00 < b.montant_max
          );

    IF v_rate <> 0.4000 THEN
        RAISE EXCEPTION
            'Expected default base rate 0.4000 for 420000 purchase, got %',
            v_rate;
    END IF;
END;
$$;


-- =============================================================================
-- Test completed successfully.
-- No test data is persisted.
-- =============================================================================

ROLLBACK;