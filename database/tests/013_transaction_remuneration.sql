BEGIN;

-- =============================================================================
-- Test 013
-- Transaction and remuneration foundation
--
-- Validates migration 010:
--   - vente structure and constraints
--   - versioned honoraires parameters
--   - versioned remuneration parameters
--   - performance bands
--   - approved/default commission grids
--   - overlap protection
--   - frozen remuneration calculation fields on paiement
-- =============================================================================


-- =============================================================================
-- 1. Required tables exist
-- =============================================================================

DO $$
BEGIN
    IF to_regclass('real_estate.vente') IS NULL THEN
        RAISE EXCEPTION 'real_estate.vente is missing';
    END IF;

    IF to_regclass('real_estate.parametres_honoraires') IS NULL THEN
        RAISE EXCEPTION 'real_estate.parametres_honoraires is missing';
    END IF;

    IF to_regclass('real_estate.parametres_remuneration') IS NULL THEN
        RAISE EXCEPTION 'real_estate.parametres_remuneration is missing';
    END IF;

    IF to_regclass('real_estate.palier_performance') IS NULL THEN
        RAISE EXCEPTION 'real_estate.palier_performance is missing';
    END IF;
END;
$$;


-- =============================================================================
-- 2. Migration registry
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM migration_control.schema_version
    WHERE version = '010';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'Expected exactly one migration registry entry for 010, got %',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- 3. Legacy commission grids are preserved as historical
-- =============================================================================

DO $$
DECLARE
    v_legacy_total INTEGER;
    v_legacy_historical INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_legacy_total
    FROM real_estate.bareme_commission
    WHERE id_chasseur IS NOT NULL;

    SELECT COUNT(*)
    INTO v_legacy_historical
    FROM real_estate.bareme_commission
    WHERE id_chasseur IS NOT NULL
      AND statut_usage = 'HISTORIQUE';

    IF v_legacy_total <> v_legacy_historical THEN
        RAISE EXCEPTION
            'All hunter-specific legacy commission grids must remain HISTORIQUE';
    END IF;
END;
$$;


-- =============================================================================
-- 4. Default commission grid is supported
-- =============================================================================

DO $$
DECLARE
    v_default_approved_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_default_approved_count
    FROM real_estate.bareme_commission
    WHERE id_chasseur IS NULL
      AND actif = TRUE
      AND statut_usage = 'APPROUVE';

    IF v_default_approved_count = 0 THEN
        RAISE EXCEPTION
            'At least one active approved default commission grid must exist';
    END IF;
END;
$$;

-- =============================================================================
-- 5. Hunter-specific grid is supported alongside default grid
-- =============================================================================

DO $$
DECLARE
    v_chasseur BIGINT;
    v_id BIGINT;
BEGIN
    SELECT id_chasseur
    INTO v_chasseur
    FROM real_estate.chasseur
    ORDER BY id_chasseur
    LIMIT 1;

    IF v_chasseur IS NULL THEN
        RAISE EXCEPTION
            'No chasseur available for hunter-specific grid test';
    END IF;

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
        0,
        200000,
        0.35,
        0,
        DATE '2026-01-01',
        NULL,
        TRUE,
        v_chasseur,
        'APPROUVE'
    )
    RETURNING id_bareme INTO v_id;

    IF v_id IS NULL THEN
        RAISE EXCEPTION
            'Hunter-specific commission grid could not be inserted';
    END IF;
END;
$$;


-- =============================================================================
-- 6. Overlapping approved default commission grids are rejected
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
            100000,
            250000,
            0.40,
            0,
            DATE '2026-06-01',
            NULL,
            TRUE,
            NULL,
            'APPROUVE'
        );

        RAISE EXCEPTION
            'Expected overlapping approved default grid to be rejected';

    EXCEPTION
        WHEN raise_exception THEN
            IF SQLERRM = 'Expected overlapping approved default grid to be rejected' THEN
                RAISE;
            END IF;

        WHEN OTHERS THEN
            NULL;
    END;
END;
$$;


-- =============================================================================
-- 7. Adjacent commission ranges are accepted
--
-- Existing hunter-specific test range:
--   [0, 200000)
--
-- This hunter-specific range starts exactly at 200000 and therefore
-- must NOT overlap.
-- =============================================================================

DO $$
DECLARE
    v_chasseur BIGINT;
    v_id BIGINT;
BEGIN
    SELECT id_chasseur
    INTO v_chasseur
    FROM real_estate.chasseur
    ORDER BY id_chasseur
    LIMIT 1;

    IF v_chasseur IS NULL THEN
        RAISE EXCEPTION
            'No chasseur available for adjacent commission-grid test';
    END IF;

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
        200000,
        350000,
        0.35,
        0,
        DATE '2026-01-01',
        NULL,
        TRUE,
        v_chasseur,
        'APPROUVE'
    )
    RETURNING id_bareme INTO v_id;

    IF v_id IS NULL THEN
        RAISE EXCEPTION
            'Adjacent hunter-specific commission range was incorrectly rejected';
    END IF;
END;
$$;


-- =============================================================================
-- 8. Company-fee parameter versions
-- =============================================================================

DO $$
DECLARE
    v_id BIGINT;
BEGIN
    INSERT INTO real_estate.parametres_honoraires (
        date_debut_validite,
        date_fin_validite,
        montant_fixe,
        taux_pourcentage,
        actif
    )
    VALUES (
        DATE '2026-01-01',
        DATE '2026-12-31',
        3000.00,
        0.025,
        TRUE
    )
    RETURNING id_parametres_honoraires INTO v_id;

    IF v_id IS NULL THEN
        RAISE EXCEPTION
            'Company-fee parameters could not be inserted';
    END IF;
END;
$$;


-- =============================================================================
-- 9. Overlapping company-fee parameters are rejected
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
            DATE '2027-01-01',
            2500.00,
            0.030,
            TRUE
        );

        RAISE EXCEPTION
            'Expected overlapping company-fee parameter period to be rejected';

    EXCEPTION
        WHEN raise_exception THEN
            IF SQLERRM = 'Expected overlapping company-fee parameter period to be rejected' THEN
                RAISE;
            END IF;

        WHEN OTHERS THEN
            NULL;
    END;
END;
$$;


-- =============================================================================
-- 10. Remuneration parameters
-- =============================================================================

DO $$
DECLARE
    v_id BIGINT;
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
        DATE '2026-01-01',
        NULL,
        12,

        0.25,
        0.10,
        0.25,
        0.15,
        0.25,

        100,
        60,

        20,
        10,

        0.02,
        0.10,

        50,
        0.20,

        0.20,
        0.60,

        TRUE
    )
    RETURNING id_parametres_remuneration INTO v_id;

    IF v_id IS NULL THEN
        RAISE EXCEPTION
            'Remuneration parameters could not be inserted';
    END IF;
END;
$$;


-- =============================================================================
-- 11. Weight total must equal 1.0
-- =============================================================================

DO $$
BEGIN
    BEGIN
        INSERT INTO real_estate.parametres_remuneration (
            date_debut_validite,
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
            DATE '2030-01-01',
            12,

            0.25,
            0.10,
            0.25,
            0.15,
            0.20,

            100,
            60,

            20,
            10,

            0.02,
            0.10,

            50,
            0.20,

            0.20,
            0.60,

            FALSE
        );

        RAISE EXCEPTION
            'Expected invalid remuneration weight total to be rejected';

    EXCEPTION
        WHEN check_violation THEN
            NULL;

        WHEN raise_exception THEN
            IF SQLERRM = 'Expected invalid remuneration weight total to be rejected' THEN
                RAISE;
            END IF;
    END;
END;
$$;


-- =============================================================================
-- 12. Performance bands can be attached to a parameter version
-- =============================================================================

DO $$
DECLARE
    v_param BIGINT;
    v_count INTEGER;
BEGIN
    SELECT id_parametres_remuneration
    INTO v_param
    FROM real_estate.parametres_remuneration
    WHERE actif = TRUE
    ORDER BY id_parametres_remuneration
    LIMIT 1;

    INSERT INTO real_estate.palier_performance (
        id_parametres_remuneration,
        critere,
        ordre,
        borne_max,
        note
    )
    VALUES
        (v_param, 'DELAI_SEMAINES', 1, 12, 100),
        (v_param, 'DELAI_SEMAINES', 2, 20, 80),
        (v_param, 'DELAI_SEMAINES', 3, NULL, 0),

        (v_param, 'VISITES', 1, 3, 100),
        (v_param, 'VISITES', 2, 6, 80),
        (v_param, 'VISITES', 3, NULL, 0);

    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.palier_performance
    WHERE id_parametres_remuneration = v_param;

    IF v_count <> 6 THEN
        RAISE EXCEPTION
            'Expected 6 performance bands, got %',
            v_count;
    END IF;
END;
$$;


-- =============================================================================
-- 13. Completed sale can be represented
-- =============================================================================

DO $$
DECLARE
    v_mandat BIGINT;
    v_periode BIGINT;
    v_chasseur BIGINT;
    v_id BIGINT;
BEGIN
    SELECT
        m.id_mandat,
        mp.id_mandat_periode,
        m.id_chasseur
    INTO
        v_mandat,
        v_periode,
        v_chasseur
    FROM real_estate.mandat m
    JOIN real_estate.mandat_periode mp
      ON mp.id_mandat = m.id_mandat
    ORDER BY
        m.id_mandat,
        mp.numero_periode DESC
    LIMIT 1;

    IF v_mandat IS NULL THEN
        RAISE EXCEPTION
            'No Mandat available for sale test';
    END IF;

    INSERT INTO real_estate.vente (
        id_mandat,
        id_mandat_periode,
        id_chasseur_beneficiaire,
        origine_vente,
        date_acte_authentique,
        montant_achat
    )
    VALUES (
        v_mandat,
        v_periode,
        v_chasseur,
        'CHASSEUR',
        CURRENT_DATE,
        420000.00
    )
    RETURNING id_vente INTO v_id;

    IF v_id IS NULL THEN
        RAISE EXCEPTION
            'Completed sale could not be inserted';
    END IF;
END;
$$;


-- =============================================================================
-- 14. Invalid sale origin is rejected
-- =============================================================================

DO $$
DECLARE
    v_mandat BIGINT;
BEGIN
    SELECT id_mandat
    INTO v_mandat
    FROM real_estate.mandat
    ORDER BY id_mandat
    LIMIT 1;

    BEGIN
        INSERT INTO real_estate.vente (
            id_mandat,
            origine_vente,
            date_acte_authentique,
            montant_achat
        )
        VALUES (
            v_mandat,
            'INCONNUE',
            CURRENT_DATE,
            100000.00
        );

        RAISE EXCEPTION
            'Expected invalid sale origin to be rejected';

    EXCEPTION
        WHEN check_violation THEN
            NULL;

        WHEN raise_exception THEN
            IF SQLERRM = 'Expected invalid sale origin to be rejected' THEN
                RAISE;
            END IF;
    END;
END;
$$;


-- =============================================================================
-- 15. Paiement contains frozen calculation columns
-- =============================================================================

DO $$
DECLARE
    v_missing INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_missing
    FROM (
        VALUES
            ('id_vente'),
            ('id_chasseur_beneficiaire'),
            ('id_parametres_honoraires'),
            ('id_parametres_remuneration'),
            ('date_calcul'),
            ('droit_remuneration'),
            ('motif_refus'),
            ('semaines_mandat_acte'),
            ('nb_visites_calcul'),
            ('annees_anciennete_calcul'),
            ('nb_ventes_fenetre'),
            ('nb_mandats_fenetre'),
            ('note_delai'),
            ('note_exclusivite'),
            ('note_ventes'),
            ('note_mandats'),
            ('note_visites'),
            ('score_performance'),
            ('taux_base'),
            ('majoration_anciennete'),
            ('modulation_performance'),
            ('taux_final')
    ) AS required(column_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM information_schema.columns c
        WHERE c.table_schema = 'real_estate'
          AND c.table_name = 'paiement'
          AND c.column_name = required.column_name
    );

    IF v_missing <> 0 THEN
        RAISE EXCEPTION
            'Missing % frozen remuneration columns on paiement',
            v_missing;
    END IF;
END;
$$;


-- =============================================================================
-- 16. Refused remuneration requires a reason
-- =============================================================================

DO $$
DECLARE
    v_mandat BIGINT;
BEGIN
    SELECT id_mandat
    INTO v_mandat
    FROM real_estate.mandat
    ORDER BY id_mandat
    LIMIT 1;

    BEGIN
        INSERT INTO real_estate.paiement (
            id_mandat,
            statut,
            droit_remuneration,
            motif_refus
        )
        VALUES (
            v_mandat,
            'ATTENDU',
            FALSE,
            NULL
        );

        RAISE EXCEPTION
            'Expected denied remuneration without reason to be rejected';

    EXCEPTION
        WHEN check_violation THEN
            NULL;

        WHEN raise_exception THEN
            IF SQLERRM = 'Expected denied remuneration without reason to be rejected' THEN
                RAISE;
            END IF;
    END;
END;
$$;


-- =============================================================================
-- 17. Open remuneration right cannot have a refusal reason
-- =============================================================================

DO $$
DECLARE
    v_mandat BIGINT;
BEGIN
    SELECT id_mandat
    INTO v_mandat
    FROM real_estate.mandat
    ORDER BY id_mandat
    LIMIT 1;

    BEGIN
        INSERT INTO real_estate.paiement (
            id_mandat,
            statut,
            droit_remuneration,
            motif_refus
        )
        VALUES (
            v_mandat,
            'ATTENDU',
            TRUE,
            'MANDAT_EXPIRE'
        );

        RAISE EXCEPTION
            'Expected open remuneration with refusal reason to be rejected';

    EXCEPTION
        WHEN check_violation THEN
            NULL;

        WHEN raise_exception THEN
            IF SQLERRM = 'Expected open remuneration with refusal reason to be rejected' THEN
                RAISE;
            END IF;
    END;
END;
$$;


-- =============================================================================
-- Test isolation
-- =============================================================================

ROLLBACK;