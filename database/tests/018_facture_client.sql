-- Test 018: migration 015's immutable client invoice (no VAT/payment lifecycle).
-- Uses an existing mandate and effective configuration, creates fresh sales,
-- and rolls back every business mutation. Identity sequences may advance.
-- Ownership, receipt eligibility and immutability are application invariants;
-- the migration provides FKs, uniqueness and individual numeric checks.
\set ON_ERROR_STOP on
BEGIN;

CREATE FUNCTION pg_temp.assert_invoice(ok BOOLEAN, message TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    IF ok IS DISTINCT FROM TRUE THEN
        RAISE EXCEPTION 'FAIL: %', message;
    END IF;
    RAISE NOTICE 'PASS: %', message;
END;
$$;

SELECT pg_temp.assert_invoice(
    (SELECT COUNT(*) = 1 FROM migration_control.schema_version WHERE version = '015'),
    'migration 015 registered exactly once');
SELECT pg_temp.assert_invoice(to_regclass('real_estate.facture_client') IS NOT NULL,
    'facture_client table exists');

SELECT pg_temp.assert_invoice(
    (SELECT array_agg(column_name::TEXT ORDER BY ordinal_position) = ARRAY[
        'id_facture_client', 'id_vente', 'id_client', 'id_parametres_honoraires',
        'numero_facture', 'date_emission', 'montant_achat', 'montant_fixe_applique',
        'taux_pourcentage_applique', 'montant_honoraires_ht', 'date_creation'
    ] FROM information_schema.columns
    WHERE table_schema = 'real_estate' AND table_name = 'facture_client'),
    'exact migration 015 columns');

SELECT pg_temp.assert_invoice(
    NOT EXISTS (
        SELECT 1 FROM (VALUES
            ('pk_facture_client', 'p'),
            ('fk_facture_client_vente', 'f'),
            ('fk_facture_client_client', 'f'),
            ('fk_facture_client_parametres_honoraires', 'f'),
            ('uq_facture_client_vente', 'u'),
            ('uq_facture_client_numero', 'u'),
            ('ck_facture_client_numero', 'c'),
            ('ck_facture_client_montant_achat', 'c'),
            ('ck_facture_client_montant_fixe', 'c'),
            ('ck_facture_client_taux_honoraires', 'c'),
            ('ck_facture_client_honoraires_ht', 'c')
        ) expected(name, kind)
        LEFT JOIN pg_constraint c ON c.conname = expected.name
            AND c.contype::TEXT = expected.kind
            AND c.conrelid = 'real_estate.facture_client'::regclass
        WHERE c.oid IS NULL
    ), 'PK, FKs, unique and CHECK constraints');

SELECT pg_temp.assert_invoice(
    (SELECT COUNT(*) = 3 FROM pg_indexes
    WHERE schemaname = 'real_estate' AND tablename = 'facture_client'
    AND indexname IN ('idx_facture_client_client', 'idx_facture_client_date_emission',
        'idx_facture_client_parametres_honoraires')),
    'client, emission and configuration indexes');

-- Select only configuration/mandate references; never modify an existing sale.
CREATE TEMP TABLE invoice_fixture ON COMMIT DROP AS
SELECT m.id_mandat, m.id_client, ph.id_parametres_honoraires,
    ph.date_debut_validite AS deed_date, ph.montant_fixe, ph.taux_pourcentage
FROM real_estate.mandat m CROSS JOIN real_estate.parametres_honoraires ph
WHERE ph.actif AND ph.date_debut_validite <= CURRENT_DATE
ORDER BY m.id_mandat, ph.date_debut_validite DESC, ph.id_parametres_honoraires DESC
LIMIT 1;
SELECT pg_temp.assert_invoice((SELECT COUNT(*) = 1 FROM invoice_fixture),
    'fixture mandate and fee configuration available');

CREATE TEMP TABLE invoice_sales(id_vente BIGINT) ON COMMIT DROP;
WITH inserted AS (
    INSERT INTO real_estate.vente(id_mandat, origine_vente, date_acte_authentique, montant_achat)
    SELECT f.id_mandat, 'CLIENT_SEUL', f.deed_date, 420000.00
    FROM invoice_fixture f CROSS JOIN generate_series(1, 2)
    RETURNING id_vente
) INSERT INTO invoice_sales SELECT id_vente FROM inserted;

INSERT INTO real_estate.facture_client (
    id_vente, id_client, id_parametres_honoraires, numero_facture, date_emission,
    montant_achat, montant_fixe_applique, taux_pourcentage_applique, montant_honoraires_ht
)
SELECT s.id_vente, f.id_client, f.id_parametres_honoraires,
    'TEST-FC-018-' || s.id_vente, CURRENT_DATE, 420000.00,
    f.montant_fixe, f.taux_pourcentage, ROUND(f.montant_fixe + f.taux_pourcentage * 420000.00, 2)
FROM invoice_fixture f CROSS JOIN invoice_sales s;

SELECT pg_temp.assert_invoice(
    (SELECT COUNT(*) = 2 FROM real_estate.facture_client fc
    JOIN invoice_sales s USING(id_vente)
    JOIN real_estate.vente v USING(id_vente)
    JOIN real_estate.mandat m USING(id_mandat)
    CROSS JOIN invoice_fixture f
    WHERE fc.id_client = m.id_client
      AND fc.id_parametres_honoraires = f.id_parametres_honoraires
      AND fc.montant_achat = v.montant_achat
      AND fc.montant_fixe_applique = f.montant_fixe
      AND fc.taux_pourcentage_applique = f.taux_pourcentage
      AND fc.montant_honoraires_ht = ROUND(f.montant_fixe + f.taux_pourcentage * v.montant_achat, 2)),
    'valid invoice insertion, derived ownership and Decimal-equivalent snapshot');

-- Every failed mutation has its own subtransaction. Verify SQLSTATE and the
-- actual constraint, so a different error cannot mask a missing protection.
DO $$
DECLARE
    bad RECORD;
    actual_constraint TEXT;
    first_sale BIGINT;
    second_sale BIGINT;
BEGIN
    SELECT MIN(id_vente), MAX(id_vente) INTO first_sale, second_sale FROM invoice_sales;
    FOR bad IN SELECT * FROM (VALUES
        ('numero_facture = ''  ''', '23514', 'ck_facture_client_numero'),
        ('montant_achat = 0', '23514', 'ck_facture_client_montant_achat'),
        ('montant_fixe_applique = -1', '23514', 'ck_facture_client_montant_fixe'),
        ('taux_pourcentage_applique = -0.0001', '23514', 'ck_facture_client_taux_honoraires'),
        ('taux_pourcentage_applique = 1.0001', '23514', 'ck_facture_client_taux_honoraires'),
        ('montant_honoraires_ht = -1', '23514', 'ck_facture_client_honoraires_ht'),
        ('id_vente = (SELECT COALESCE(MAX(id_vente),0)+1 FROM real_estate.vente)', '23503', 'fk_facture_client_vente'),
        ('id_client = (SELECT COALESCE(MAX(id_client),0)+1 FROM real_estate.client)', '23503', 'fk_facture_client_client'),
        ('id_parametres_honoraires = (SELECT COALESCE(MAX(id_parametres_honoraires),0)+1 FROM real_estate.parametres_honoraires)',
            '23503', 'fk_facture_client_parametres_honoraires'),
        ('id_vente = ' || second_sale, '23505', 'uq_facture_client_vente'),
        ('numero_facture = ''TEST-FC-018-' || second_sale || '''', '23505', 'uq_facture_client_numero')
    ) cases(assignment, expected_state, expected_constraint)
    LOOP
        BEGIN
            EXECUTE 'UPDATE real_estate.facture_client SET ' || bad.assignment || ' WHERE id_vente = $1'
                USING first_sale;
            RAISE EXCEPTION 'FAIL: mutation accepted: %', bad.assignment;
        EXCEPTION WHEN integrity_constraint_violation THEN
            GET STACKED DIAGNOSTICS actual_constraint = CONSTRAINT_NAME;
            IF SQLSTATE <> bad.expected_state OR actual_constraint <> bad.expected_constraint THEN
                RAISE;
            END IF;
            RAISE NOTICE 'PASS: % enforced', actual_constraint;
        END;
    END LOOP;
END;
$$;

-- Source configuration updates cannot change already persisted amounts.
UPDATE real_estate.parametres_honoraires
SET montant_fixe = montant_fixe + 1
WHERE id_parametres_honoraires IN (SELECT id_parametres_honoraires FROM invoice_fixture);
SELECT pg_temp.assert_invoice(
    (SELECT COUNT(*) = 2 FROM real_estate.facture_client fc
    JOIN invoice_sales s USING(id_vente) CROSS JOIN invoice_fixture f
    WHERE fc.montant_fixe_applique = f.montant_fixe
      AND fc.montant_honoraires_ht = ROUND(f.montant_fixe + f.taux_pourcentage * fc.montant_achat, 2)),
    'financial snapshots remain unchanged after fee configuration update');

ROLLBACK;
