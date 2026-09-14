-- =====================================================================
-- File: database/tests/007_warehouse_data_quality.sql
-- Project: Chasse Immobiliere
-- Purpose:
--   Validate OLTP -> Warehouse reconciliation and analytical integrity.
--
-- This test must fail the Airflow task when a critical warehouse
-- invariant is violated.
-- =====================================================================

\set ON_ERROR_STOP on

\echo '============================================================'
\echo 'WAREHOUSE DATA QUALITY'
\echo '============================================================'


-- =====================================================================
-- 1. DIMENSION DATE
-- =====================================================================

DO $$
DECLARE
    v_count bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM warehouse.dim_date;

    IF v_count <> 5844 THEN
        RAISE EXCEPTION
            'FAIL: dim_date expected 5844 rows, found %',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: dim_date contains % rows',
        v_count;
END
$$;


-- =====================================================================
-- 2. CLIENT RECONCILIATION
--
-- +1 = controlled UNKNOWN warehouse member.
-- =====================================================================

DO $$
DECLARE
    v_oltp bigint;
    v_dw bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_oltp
    FROM real_estate.client;

    SELECT COUNT(*)
    INTO v_dw
    FROM warehouse.dim_client;

    IF v_dw <> v_oltp + 1 THEN
        RAISE EXCEPTION
            'FAIL: client reconciliation OLTP=% DW=% expected DW=%',
            v_oltp,
            v_dw,
            v_oltp + 1;
    END IF;

    RAISE NOTICE
        'PASS: client reconciliation OLTP=% DW=%',
        v_oltp,
        v_dw;
END
$$;


-- =====================================================================
-- 3. CHASSEUR RECONCILIATION
-- =====================================================================

DO $$
DECLARE
    v_oltp bigint;
    v_dw bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_oltp
    FROM real_estate.chasseur;

    SELECT COUNT(*)
    INTO v_dw
    FROM warehouse.dim_chasseur;

    IF v_dw <> v_oltp + 1 THEN
        RAISE EXCEPTION
            'FAIL: chasseur reconciliation OLTP=% DW=% expected DW=%',
            v_oltp,
            v_dw,
            v_oltp + 1;
    END IF;

    RAISE NOTICE
        'PASS: chasseur reconciliation OLTP=% DW=%',
        v_oltp,
        v_dw;
END
$$;


-- =====================================================================
-- 4. SECTEUR RECONCILIATION
-- =====================================================================

DO $$
DECLARE
    v_oltp bigint;
    v_dw bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_oltp
    FROM real_estate.secteur;

    SELECT COUNT(*)
    INTO v_dw
    FROM warehouse.dim_secteur;

    IF v_dw <> v_oltp + 1 THEN
        RAISE EXCEPTION
            'FAIL: secteur reconciliation OLTP=% DW=% expected DW=%',
            v_oltp,
            v_dw,
            v_oltp + 1;
    END IF;

    RAISE NOTICE
        'PASS: secteur reconciliation OLTP=% DW=%',
        v_oltp,
        v_dw;
END
$$;


-- =====================================================================
-- 5. DEMANDE VERSION RECONCILIATION
-- =====================================================================

DO $$
DECLARE
    v_oltp bigint;
    v_dw bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_oltp
    FROM real_estate.demande_version;

    SELECT COUNT(*)
    INTO v_dw
    FROM warehouse.dim_demande_version;

    IF v_dw <> v_oltp + 1 THEN
        RAISE EXCEPTION
            'FAIL: demande_version reconciliation OLTP=% DW=% expected DW=%',
            v_oltp,
            v_dw,
            v_oltp + 1;
    END IF;

    RAISE NOTICE
        'PASS: demande_version reconciliation OLTP=% DW=%',
        v_oltp,
        v_dw;
END
$$;


-- =====================================================================
-- 6. MANDAT FACT RECONCILIATION
-- =====================================================================

DO $$
DECLARE
    v_oltp bigint;
    v_dw bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_oltp
    FROM real_estate.mandat;

    SELECT COUNT(*)
    INTO v_dw
    FROM warehouse.fact_mandat;

    IF v_dw <> v_oltp THEN
        RAISE EXCEPTION
            'FAIL: mandat reconciliation OLTP=% DW=%',
            v_oltp,
            v_dw;
    END IF;

    RAISE NOTICE
        'PASS: mandat reconciliation OLTP=% DW=%',
        v_oltp,
        v_dw;
END
$$;


-- =====================================================================
-- 7. MANDAT-SECTEUR BRIDGE RECONCILIATION
-- =====================================================================

DO $$
DECLARE
    v_oltp bigint;
    v_dw bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_oltp
    FROM real_estate.mandat_secteur;

    SELECT COUNT(*)
    INTO v_dw
    FROM warehouse.bridge_mandat_secteur;

    IF v_dw <> v_oltp THEN
        RAISE EXCEPTION
            'FAIL: mandat_secteur reconciliation OLTP=% DW=%',
            v_oltp,
            v_dw;
    END IF;

    RAISE NOTICE
        'PASS: mandat_secteur reconciliation OLTP=% DW=%',
        v_oltp,
        v_dw;
END
$$;


-- =====================================================================
-- 8. PRESENTATION FACT RECONCILIATION
-- =====================================================================

DO $$
DECLARE
    v_oltp bigint;
    v_dw bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_oltp
    FROM real_estate.presentation;

    SELECT COUNT(*)
    INTO v_dw
    FROM warehouse.fact_presentation;

    IF v_dw <> v_oltp THEN
        RAISE EXCEPTION
            'FAIL: presentation reconciliation OLTP=% DW=%',
            v_oltp,
            v_dw;
    END IF;

    RAISE NOTICE
        'PASS: presentation reconciliation OLTP=% DW=%',
        v_oltp,
        v_dw;
END
$$;


-- =====================================================================
-- 9. PAYMENT FACT RECONCILIATION
-- =====================================================================

DO $$
DECLARE
    v_oltp bigint;
    v_dw bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_oltp
    FROM real_estate.paiement;

    SELECT COUNT(*)
    INTO v_dw
    FROM warehouse.fact_paiement;

    IF v_dw <> v_oltp THEN
        RAISE EXCEPTION
            'FAIL: paiement reconciliation OLTP=% DW=%',
            v_oltp,
            v_dw;
    END IF;

    RAISE NOTICE
        'PASS: paiement reconciliation OLTP=% DW=%',
        v_oltp,
        v_dw;
END
$$;

-- =====================================================================
-- 9.1 PAYMENT FACT FINANCIAL RECONCILIATION
--
-- Validate that financial measures and lifecycle status loaded into the
-- warehouse remain identical to their OLTP source values.
-- =====================================================================

DO $$
DECLARE
    v_mismatches bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_mismatches
    FROM real_estate.paiement p
    JOIN warehouse.fact_paiement fp
      ON fp.id_paiement_source = p.id_paiement
    WHERE
        fp.montant_achat IS DISTINCT FROM p.montant_achat
        OR fp.montant_honoraires IS DISTINCT FROM p.montant_honoraires
        OR fp.montant_chasseur IS DISTINCT FROM p.montant_chasseur
        OR fp.statut IS DISTINCT FROM p.statut;

    IF v_mismatches <> 0 THEN
        RAISE EXCEPTION
            'FAIL: paiement financial reconciliation mismatches=%',
            v_mismatches;
    END IF;

    RAISE NOTICE
        'PASS: paiement financial reconciliation mismatches=%',
        v_mismatches;
END
$$;


-- =====================================================================
-- 9.2 PAYMENT FACT BUSINESS AMOUNT CONSISTENCY
--
-- Hunter remuneration cannot exceed company fees.
-- =====================================================================

DO $$
DECLARE
    v_invalid bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM warehouse.fact_paiement
    WHERE montant_chasseur IS NOT NULL
      AND montant_honoraires IS NOT NULL
      AND montant_chasseur > montant_honoraires;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'FAIL: paiement hunter remuneration exceeds company fees rows=%',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: paiement hunter remuneration does not exceed company fees';
END
$$;


-- =====================================================================
-- 9.3 PAID PAYMENT DATE COMPLETENESS
--
-- A payment in PAYE status must have both company-fee reception and
-- hunter-payment dates materialized in the warehouse.
-- =====================================================================

DO $$
DECLARE
    v_invalid bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM warehouse.fact_paiement
    WHERE statut = 'PAYE'
      AND (
          date_reception_honoraires_key IS NULL
          OR date_paiement_chasseur_key IS NULL
      );

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'FAIL: PAYE paiement missing lifecycle date rows=%',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: PAYE paiements contain reception and hunter payment dates';
END
$$;


-- =====================================================================
-- 9.4 PAYMENT FACT DATE RECONCILIATION
--
-- Validate warehouse date keys against OLTP business dates.
-- YYYYMMDD integer keys are compared directly with OLTP dates.
-- =====================================================================

DO $$
DECLARE
    v_mismatches bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_mismatches
    FROM real_estate.paiement p
    JOIN warehouse.fact_paiement fp
      ON fp.id_paiement_source = p.id_paiement
    WHERE
        fp.date_acte_authentique_key IS DISTINCT FROM
            CASE
                WHEN p.date_acte_authentique IS NULL THEN NULL
                ELSE TO_CHAR(
                    p.date_acte_authentique,
                    'YYYYMMDD'
                )::integer
            END

        OR fp.date_reception_honoraires_key IS DISTINCT FROM
            CASE
                WHEN p.date_reception_honoraires IS NULL THEN NULL
                ELSE TO_CHAR(
                    p.date_reception_honoraires,
                    'YYYYMMDD'
                )::integer
            END

        OR fp.date_paiement_chasseur_key IS DISTINCT FROM
            CASE
                WHEN p.date_paiement_chasseur IS NULL THEN NULL
                ELSE TO_CHAR(
                    p.date_paiement_chasseur,
                    'YYYYMMDD'
                )::integer
            END;

    IF v_mismatches <> 0 THEN
        RAISE EXCEPTION
            'FAIL: paiement date reconciliation mismatches=%',
            v_mismatches;
    END IF;

    RAISE NOTICE
        'PASS: paiement date reconciliation mismatches=%',
        v_mismatches;
END
$$;
-- =====================================================================
-- 10. CURRENT PROPERTY DIMENSION RECONCILIATION
--
-- Every OLTP property must have exactly one current warehouse member.
-- UNKNOWN row is excluded.
-- =====================================================================

DO $$
DECLARE
    v_oltp bigint;
    v_dw bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_oltp
    FROM real_estate.bien;

    SELECT COUNT(*)
    INTO v_dw
    FROM warehouse.dim_bien
    WHERE is_current = TRUE
      AND bien_key <> 0;

    IF v_dw <> v_oltp THEN
        RAISE EXCEPTION
            'FAIL: current bien reconciliation OLTP=% DW=%',
            v_oltp,
            v_dw;
    END IF;

    RAISE NOTICE
        'PASS: current bien reconciliation OLTP=% DW=%',
        v_oltp,
        v_dw;
END
$$;


-- =====================================================================
-- 11. DUPLICATE CURRENT PROPERTY MEMBERS
-- =====================================================================

DO $$
DECLARE
    v_duplicates bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_duplicates
    FROM (
        SELECT
            id_source_source,
            reference_externe
        FROM warehouse.dim_bien
        WHERE is_current = TRUE
          AND bien_key <> 0
        GROUP BY
            id_source_source,
            reference_externe
        HAVING COUNT(*) > 1
    ) d;

    IF v_duplicates <> 0 THEN
        RAISE EXCEPTION
            'FAIL: duplicate current dim_bien business keys=%',
            v_duplicates;
    END IF;

    RAISE NOTICE
        'PASS: no duplicate current dim_bien business keys';
END
$$;


-- =====================================================================
-- 12. FACT ANNONCE BASIC QUALITY
-- =====================================================================

DO $$
DECLARE
    v_invalid bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM warehouse.fact_annonce
    WHERE prix < 0
       OR surface <= 0
       OR prix_m2 < 0;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'FAIL: invalid fact_annonce numerical rows=%',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: fact_annonce numerical measures are valid';
END
$$;


-- =====================================================================
-- 13. FACT MANDAT BASIC QUALITY
-- =====================================================================

DO $$
DECLARE
    v_invalid bigint;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid
    FROM warehouse.fact_mandat
    WHERE duree_jours < 0
       OR mandat_count <> 1;

    IF v_invalid <> 0 THEN
        RAISE EXCEPTION
            'FAIL: invalid fact_mandat rows=%',
            v_invalid;
    END IF;

    RAISE NOTICE
        'PASS: fact_mandat measures are valid';
END
$$;


-- =====================================================================
-- 14. WAREHOUSE SUMMARY
-- =====================================================================

\echo ''
\echo 'WAREHOUSE OBJECT COUNTS'
\echo '------------------------------------------------------------'

SELECT
    object_name,
    rows
FROM (
    SELECT 'dim_source' AS object_name, COUNT(*) AS rows
    FROM warehouse.dim_source

    UNION ALL

    SELECT 'dim_localisation', COUNT(*)
    FROM warehouse.dim_localisation

    UNION ALL

    SELECT 'dim_bien', COUNT(*)
    FROM warehouse.dim_bien

    UNION ALL

    SELECT 'dim_client', COUNT(*)
    FROM warehouse.dim_client

    UNION ALL

    SELECT 'dim_chasseur', COUNT(*)
    FROM warehouse.dim_chasseur

    UNION ALL

    SELECT 'dim_secteur', COUNT(*)
    FROM warehouse.dim_secteur

    UNION ALL

    SELECT 'dim_demande_version', COUNT(*)
    FROM warehouse.dim_demande_version

    UNION ALL

    SELECT 'fact_annonce', COUNT(*)
    FROM warehouse.fact_annonce

    UNION ALL

    SELECT 'fact_mandat', COUNT(*)
    FROM warehouse.fact_mandat

    UNION ALL

    SELECT 'bridge_mandat_secteur', COUNT(*)
    FROM warehouse.bridge_mandat_secteur

    UNION ALL

    SELECT 'fact_presentation', COUNT(*)
    FROM warehouse.fact_presentation

    UNION ALL

    SELECT 'fact_paiement', COUNT(*)
    FROM warehouse.fact_paiement
) q
ORDER BY object_name;


\echo ''
\echo '============================================================'
\echo 'PASS: WAREHOUSE data quality validated successfully'
\echo '============================================================'