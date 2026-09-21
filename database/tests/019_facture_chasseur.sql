-- Test 019: run via database:test-facture-chasseur after migration 016.
-- No existing business rows are changed. Test rows roll back; sequences may advance.
-- Cross-table ownership/amount checks and payment transitions belong to the API.
\set ON_ERROR_STOP on
BEGIN;

CREATE FUNCTION pg_temp.assert_hunter_invoice(ok BOOLEAN, message TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    IF ok IS DISTINCT FROM TRUE THEN RAISE EXCEPTION 'FAIL: %', message; END IF;
    RAISE NOTICE 'PASS: %', message;
END;
$$;

SELECT pg_temp.assert_hunter_invoice(
    (SELECT COUNT(*) = 1 FROM migration_control.schema_version WHERE version = '016'),
    'migration 016 registered exactly once');
SELECT pg_temp.assert_hunter_invoice(to_regclass('real_estate.facture_chasseur') IS NOT NULL,
    'hunter invoice table exists');
SELECT pg_temp.assert_hunter_invoice(
    (SELECT array_agg(column_name::TEXT ORDER BY ordinal_position) = ARRAY[
        'id_facture_chasseur', 'id_paiement', 'id_chasseur', 'numero_version', 'numero_facture',
        'date_facture', 'montant', 'date_soumission', 'statut', 'date_verification',
        'id_verificateur', 'motif_rejet'
    ] FROM information_schema.columns
    WHERE table_schema = 'real_estate' AND table_name = 'facture_chasseur'),
    'exact migration 016 columns');
SELECT pg_temp.assert_hunter_invoice(
    NOT EXISTS (
        SELECT 1 FROM (VALUES
            ('pk_facture_chasseur', 'p'), ('fk_facture_chasseur_paiement', 'f'),
            ('fk_facture_chasseur_chasseur', 'f'), ('fk_facture_chasseur_verificateur', 'f'),
            ('uq_facture_chasseur_paiement_version', 'u'), ('ck_facture_chasseur_version', 'c'),
            ('ck_facture_chasseur_numero', 'c'), ('ck_facture_chasseur_montant', 'c'),
            ('ck_facture_chasseur_statut', 'c'), ('ck_facture_chasseur_verification', 'c'),
            ('ck_facture_chasseur_dates', 'c')
        ) expected(name, kind)
        LEFT JOIN pg_constraint c ON c.conname = expected.name AND c.contype::TEXT = expected.kind
            AND c.conrelid = 'real_estate.facture_chasseur'::regclass
        WHERE c.oid IS NULL
    ), 'PK, FK, version uniqueness and CHECK constraints');
SELECT pg_temp.assert_hunter_invoice(
    (SELECT COUNT(*) = 3 FROM pg_indexes WHERE schemaname = 'real_estate'
    AND tablename = 'facture_chasseur' AND indexname IN (
        'uq_facture_chasseur_active', 'idx_facture_chasseur_chasseur', 'idx_facture_chasseur_statut')),
    'active invoice, hunter and status indexes');

-- Reuse reference identities only. Require an existing ADMIN; never provision credentials.
CREATE TEMP TABLE hunter_invoice_fixture ON COMMIT DROP AS
SELECT m.id_mandat, m.id_chasseur, u.id_utilisateur
FROM real_estate.mandat m CROSS JOIN real_estate.utilisateur u
WHERE m.id_chasseur IS NOT NULL AND u.role = 'ADMIN'
ORDER BY m.id_mandat, u.id_utilisateur LIMIT 1;
SELECT pg_temp.assert_hunter_invoice((SELECT COUNT(*) = 1 FROM hunter_invoice_fixture),
    'fixture requires an existing hunter mandate and ADMIN identity');
CREATE TEMP TABLE hunter_invoice_payment(id_paiement BIGINT) ON COMMIT DROP;
WITH sale AS (
    INSERT INTO real_estate.vente(id_mandat, origine_vente, date_acte_authentique, montant_achat)
    SELECT id_mandat, 'CLIENT_SEUL', CURRENT_DATE, 300000.00 FROM hunter_invoice_fixture
    RETURNING id_vente
), payment AS (
    INSERT INTO real_estate.paiement(id_vente, id_mandat, id_chasseur_beneficiaire,
        droit_remuneration, date_acte_authentique, date_reception_honoraires,
        montant_achat, montant_honoraires, montant_chasseur, statut)
    SELECT s.id_vente, f.id_mandat, f.id_chasseur, TRUE, CURRENT_DATE, CURRENT_DATE,
        300000.00, 10500.00, 3939.60, 'RECU' FROM sale s CROSS JOIN hunter_invoice_fixture f
    RETURNING id_paiement
) INSERT INTO hunter_invoice_payment SELECT id_paiement FROM payment;
INSERT INTO real_estate.facture_chasseur(id_paiement, id_chasseur, numero_version,
    numero_facture, date_facture, montant)
SELECT p.id_paiement, f.id_chasseur, 1, 'TEST-HUNTER-019', CURRENT_DATE, 3939.60
FROM hunter_invoice_payment p CROSS JOIN hunter_invoice_fixture f;

DO $$
DECLARE
    bad RECORD;
    actual_constraint TEXT;
    payment_id BIGINT;
BEGIN
    SELECT id_paiement INTO STRICT payment_id FROM hunter_invoice_payment;
    FOR bad IN SELECT * FROM (VALUES
        ('numero_version = 0', '23514', 'ck_facture_chasseur_version'),
        ('numero_facture = '' ''', '23514', 'ck_facture_chasseur_numero'),
        ('montant = 0', '23514', 'ck_facture_chasseur_montant'),
        ('statut = ''CONFORME''', '23514', 'ck_facture_chasseur_verification'),
        ('motif_rejet = ''unexpected''', '23514', 'ck_facture_chasseur_verification'),
        ('id_paiement = (SELECT COALESCE(MAX(id_paiement),0)+1 FROM real_estate.paiement)',
            '23503', 'fk_facture_chasseur_paiement'),
        ('id_chasseur = (SELECT COALESCE(MAX(id_chasseur),0)+1 FROM real_estate.chasseur)',
            '23503', 'fk_facture_chasseur_chasseur'),
        ('statut = ''CONFORME'', date_verification = CURRENT_TIMESTAMP, id_verificateur = '
            || '(SELECT COALESCE(MAX(id_utilisateur),0)+1 FROM real_estate.utilisateur)',
            '23503', 'fk_facture_chasseur_verificateur'),
        ('statut = ''CONFORME'', date_verification = CURRENT_TIMESTAMP - INTERVAL ''1 day'', '
            || 'id_verificateur = (SELECT id_utilisateur FROM hunter_invoice_fixture)',
            '23514', 'ck_facture_chasseur_dates')
    ) cases(assignment, expected_state, expected_constraint)
    LOOP
        BEGIN
            EXECUTE 'UPDATE real_estate.facture_chasseur SET ' || bad.assignment || ' WHERE id_paiement = $1'
                USING payment_id;
            RAISE EXCEPTION 'FAIL: mutation accepted: %', bad.assignment;
        EXCEPTION WHEN integrity_constraint_violation THEN
            GET STACKED DIAGNOSTICS actual_constraint = CONSTRAINT_NAME;
            IF SQLSTATE <> bad.expected_state OR actual_constraint <> bad.expected_constraint THEN RAISE; END IF;
            RAISE NOTICE 'PASS: % enforced', actual_constraint;
        END;
    END LOOP;
    BEGIN
        INSERT INTO real_estate.facture_chasseur(id_paiement, id_chasseur, numero_version,
            numero_facture, date_facture, montant)
        SELECT id_paiement, id_chasseur, 2, numero_facture, date_facture, montant
        FROM real_estate.facture_chasseur WHERE id_paiement = payment_id;
        RAISE EXCEPTION 'FAIL: second active invoice accepted';
    EXCEPTION WHEN unique_violation THEN
        GET STACKED DIAGNOSTICS actual_constraint = CONSTRAINT_NAME;
        IF actual_constraint <> 'uq_facture_chasseur_active' THEN RAISE; END IF;
    END;
END;
$$;

UPDATE real_estate.facture_chasseur SET statut = 'REJETEE', motif_rejet = 'Correction requested',
    id_verificateur = (SELECT id_utilisateur FROM hunter_invoice_fixture), date_verification = CURRENT_TIMESTAMP
WHERE id_paiement IN (SELECT id_paiement FROM hunter_invoice_payment);
INSERT INTO real_estate.facture_chasseur(id_paiement, id_chasseur, numero_version,
    numero_facture, date_facture, montant)
SELECT id_paiement, id_chasseur, 2, numero_facture, date_facture, montant
FROM real_estate.facture_chasseur WHERE id_paiement IN (SELECT id_paiement FROM hunter_invoice_payment);
UPDATE real_estate.facture_chasseur SET statut = 'CONFORME',
    id_verificateur = (SELECT id_utilisateur FROM hunter_invoice_fixture), date_verification = CURRENT_TIMESTAMP
WHERE id_paiement IN (SELECT id_paiement FROM hunter_invoice_payment) AND numero_version = 2;
SELECT pg_temp.assert_hunter_invoice(
    (SELECT array_agg(statut ORDER BY numero_version) = ARRAY['REJETEE', 'CONFORME']::VARCHAR[]
    FROM real_estate.facture_chasseur WHERE id_paiement IN (SELECT id_paiement FROM hunter_invoice_payment)),
    'rejected version retained alongside conforming correction');
SELECT pg_temp.assert_hunter_invoice(
    (SELECT statut = 'RECU' AND montant_chasseur = 3939.60 FROM real_estate.paiement
    WHERE id_paiement IN (SELECT id_paiement FROM hunter_invoice_payment)),
    'invoice SQL storage does not recalculate remuneration or replace application transitions');

DO $$
DECLARE
    actual_constraint TEXT;
BEGIN
    BEGIN
        -- A rejected row avoids the active index: this exercises version uniqueness itself.
        INSERT INTO real_estate.facture_chasseur(id_paiement, id_chasseur, numero_version,
            numero_facture, date_facture, montant, statut, date_verification, id_verificateur, motif_rejet)
        SELECT id_paiement, id_chasseur, 1, numero_facture, date_facture, montant,
            statut, date_verification, id_verificateur, motif_rejet
        FROM real_estate.facture_chasseur
        WHERE id_paiement IN (SELECT id_paiement FROM hunter_invoice_payment) AND numero_version = 1;
        RAISE EXCEPTION 'FAIL: duplicate rejected version accepted';
    EXCEPTION WHEN unique_violation THEN
        GET STACKED DIAGNOSTICS actual_constraint = CONSTRAINT_NAME;
        IF actual_constraint <> 'uq_facture_chasseur_paiement_version' THEN RAISE; END IF;
    END;
    BEGIN
        INSERT INTO real_estate.facture_chasseur(id_paiement, id_chasseur, numero_version,
            numero_facture, date_facture, montant)
        SELECT id_paiement, id_chasseur, 3, numero_facture, date_facture, montant
        FROM real_estate.facture_chasseur
        WHERE id_paiement IN (SELECT id_paiement FROM hunter_invoice_payment) AND numero_version = 2;
        RAISE EXCEPTION 'FAIL: submission after conforming invoice accepted';
    EXCEPTION WHEN unique_violation THEN
        GET STACKED DIAGNOSTICS actual_constraint = CONSTRAINT_NAME;
        IF actual_constraint <> 'uq_facture_chasseur_active' THEN RAISE; END IF;
    END;
END;
$$;
ROLLBACK;
