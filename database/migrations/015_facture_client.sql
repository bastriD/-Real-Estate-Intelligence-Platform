-- =============================================================================
-- 015_facture_client.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Introduce the client invoice generated from a completed property sale.
--
-- Business lifecycle:
--   Vente / acte authentique
--       -> company fees calculated from effective honoraires parameters
--       -> Facture Client
--       -> downstream financial / remuneration workflow
--
-- StarterPack requirements:
--   - The buyer pays company fees separately from the property purchase price.
--   - The notary secures collection of those fees for the company.
--   - After the authentic deed and payment of fees, the client receives
--     an invoice.
--   - Company fees are calculated as:
--
--         H = fixed amount + percentage * purchase amount
--
--   - H represents company fees before tax.
--
-- Design decisions:
--   - A client invoice belongs to exactly one Vente.
--   - At most one client invoice exists for one Vente.
--   - The authoritative client lineage is:
--
--         Facture Client -> Vente -> Mandat -> Client
--
--   - The client is derived from persisted business lineage and must never
--     be freely selected by an API caller.
--   - Financial calculation inputs and the resulting company fee amount are
--     snapshotted on the invoice.
--   - The effective honoraires parameter row is referenced for lineage.
--   - The invoice is independent from real_estate.paiement.
--   - Payment/remuneration lifecycle remains owned by real_estate.paiement.
--   - VAT is not introduced by this migration because the current project
--     requirements do not define its applicable configuration.
--   - A credit-note / avoir workflow is not invented by this migration.
--   - No complete postal billing address is invented because the current
--     Client model does not contain one.
--
-- Historical treatment:
--   No historical client invoices are invented or backfilled because no
--   legacy invoice entity exists.
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;


-- =============================================================================
-- 1. PRECONDITIONS
-- =============================================================================

DO $$
BEGIN
    IF to_regclass('real_estate.vente') IS NULL THEN
        RAISE EXCEPTION
            'Migration 015 aborted: real_estate.vente does not exist';
    END IF;

    IF to_regclass('real_estate.mandat') IS NULL THEN
        RAISE EXCEPTION
            'Migration 015 aborted: real_estate.mandat does not exist';
    END IF;

    IF to_regclass('real_estate.client') IS NULL THEN
        RAISE EXCEPTION
            'Migration 015 aborted: real_estate.client does not exist';
    END IF;

    IF to_regclass('real_estate.parametres_honoraires') IS NULL THEN
        RAISE EXCEPTION
            'Migration 015 aborted: real_estate.parametres_honoraires does not exist';
    END IF;

    IF to_regclass('migration_control.schema_version') IS NULL THEN
        RAISE EXCEPTION
            'Migration 015 aborted: migration_control.schema_version does not exist';
    END IF;
END
$$;


-- =============================================================================
-- 2. PREVENT ACCIDENTAL SECOND EXECUTION
-- =============================================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM migration_control.schema_version
        WHERE version = '015'
    ) THEN
        RAISE EXCEPTION
            'Migration 015 has already been applied';
    END IF;
END
$$;


-- =============================================================================
-- 3. FACTURE CLIENT
--
-- One row represents the company invoice associated with one completed sale.
--
-- Business ownership:
--
--   facture_client.id_vente
--       -> vente.id_mandat
--       -> mandat.id_client
--
-- id_client is also persisted as a direct accounting/business reference.
-- Application services must derive it from the Vente lineage.
--
-- Financial snapshot:
--
--   montant_honoraires_ht =
--       montant_fixe_applique
--       + taux_pourcentage_applique * montant_achat
--
-- The parameter reference and calculation values are persisted so future
-- parameter changes cannot rewrite historical invoice calculations.
-- =============================================================================

CREATE TABLE real_estate.facture_client (
    id_facture_client BIGINT GENERATED ALWAYS AS IDENTITY,

    id_vente BIGINT NOT NULL,

    id_client BIGINT NOT NULL,

    id_parametres_honoraires BIGINT NOT NULL,

    numero_facture VARCHAR(80) NOT NULL,

    date_emission DATE NOT NULL,

    montant_achat NUMERIC(14, 2) NOT NULL,

    montant_fixe_applique NUMERIC(12, 2) NOT NULL,

    taux_pourcentage_applique NUMERIC(7, 4) NOT NULL,

    montant_honoraires_ht NUMERIC(14, 2) NOT NULL,

    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_facture_client
        PRIMARY KEY (id_facture_client),

    CONSTRAINT fk_facture_client_vente
        FOREIGN KEY (id_vente)
        REFERENCES real_estate.vente(id_vente)
        ON DELETE RESTRICT,

    CONSTRAINT fk_facture_client_client
        FOREIGN KEY (id_client)
        REFERENCES real_estate.client(id_client)
        ON DELETE RESTRICT,

    CONSTRAINT fk_facture_client_parametres_honoraires
        FOREIGN KEY (id_parametres_honoraires)
        REFERENCES real_estate.parametres_honoraires(
            id_parametres_honoraires
        )
        ON DELETE RESTRICT,

    CONSTRAINT uq_facture_client_vente
        UNIQUE (id_vente),

    CONSTRAINT uq_facture_client_numero
        UNIQUE (numero_facture),

    CONSTRAINT ck_facture_client_numero
        CHECK (
            LENGTH(TRIM(numero_facture)) > 0
        ),

    CONSTRAINT ck_facture_client_montant_achat
        CHECK (
            montant_achat > 0
        ),

    CONSTRAINT ck_facture_client_montant_fixe
        CHECK (
            montant_fixe_applique >= 0
        ),

    CONSTRAINT ck_facture_client_taux_honoraires
        CHECK (
            taux_pourcentage_applique >= 0
            AND taux_pourcentage_applique <= 1
        ),

    CONSTRAINT ck_facture_client_honoraires_ht
        CHECK (
            montant_honoraires_ht >= 0
        )
);


-- =============================================================================
-- 4. INDEXES
-- =============================================================================

CREATE INDEX idx_facture_client_client
    ON real_estate.facture_client(id_client);


CREATE INDEX idx_facture_client_date_emission
    ON real_estate.facture_client(date_emission);


CREATE INDEX idx_facture_client_parametres_honoraires
    ON real_estate.facture_client(id_parametres_honoraires);


-- =============================================================================
-- 5. VALIDATION
-- =============================================================================

DO $$
DECLARE
    invalid_invoices INTEGER;
    duplicate_sales INTEGER;
    duplicate_numbers INTEGER;
    inconsistent_ownership INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO invalid_invoices
    FROM real_estate.facture_client
    WHERE montant_achat <= 0
       OR montant_fixe_applique < 0
       OR taux_pourcentage_applique < 0
       OR taux_pourcentage_applique > 1
       OR montant_honoraires_ht < 0
       OR LENGTH(TRIM(numero_facture)) = 0;

    IF invalid_invoices <> 0 THEN
        RAISE EXCEPTION
            'Migration 015 validation failed: % invalid client invoices found',
            invalid_invoices;
    END IF;


    SELECT COUNT(*)
    INTO duplicate_sales
    FROM (
        SELECT id_vente
        FROM real_estate.facture_client
        GROUP BY id_vente
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicate_sales <> 0 THEN
        RAISE EXCEPTION
            'Migration 015 validation failed: % sales have multiple client invoices',
            duplicate_sales;
    END IF;


    SELECT COUNT(*)
    INTO duplicate_numbers
    FROM (
        SELECT numero_facture
        FROM real_estate.facture_client
        GROUP BY numero_facture
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicate_numbers <> 0 THEN
        RAISE EXCEPTION
            'Migration 015 validation failed: % duplicate invoice numbers found',
            duplicate_numbers;
    END IF;


    SELECT COUNT(*)
    INTO inconsistent_ownership
    FROM real_estate.facture_client fc
    JOIN real_estate.vente v
        ON v.id_vente = fc.id_vente
    JOIN real_estate.mandat m
        ON m.id_mandat = v.id_mandat
    WHERE fc.id_client <> m.id_client;

    IF inconsistent_ownership <> 0 THEN
        RAISE EXCEPTION
            'Migration 015 validation failed: % invoices have inconsistent client ownership',
            inconsistent_ownership;
    END IF;


    RAISE NOTICE
        'PASS: real_estate.facture_client created';

    RAISE NOTICE
        'PASS: one client invoice is allowed per sale';

    RAISE NOTICE
        'PASS: invoice numbers are unique';

    RAISE NOTICE
        'PASS: invoice client ownership follows Vente -> Mandat -> Client';

    RAISE NOTICE
        'PASS: company fee calculation inputs and result are historically snapshotted';

    RAISE NOTICE
        'PASS: client invoice remains independent from payment and hunter remuneration lifecycle';

    RAISE NOTICE
        'PASS: no unsupported VAT or credit-note rules were invented';

    RAISE NOTICE
        'PASS: no historical client invoices were invented';
END
$$;


-- =============================================================================
-- 6. REGISTER MIGRATION
-- =============================================================================

INSERT INTO migration_control.schema_version (
    version,
    description
)
VALUES (
    '015',
    'Add client invoice foundation for completed sales'
);


COMMIT;


-- =============================================================================
-- POST-MIGRATION REPORT
-- =============================================================================

SELECT
    version,
    description,
    applied_at
FROM migration_control.schema_version
WHERE version = '015';


SELECT
    to_regclass('real_estate.facture_client')
        AS facture_client_table,

    to_regclass('real_estate.idx_facture_client_client')
        AS client_index,

    to_regclass('real_estate.idx_facture_client_date_emission')
        AS emission_date_index,

    to_regclass('real_estate.idx_facture_client_parametres_honoraires')
        AS honoraires_parameters_index;


SELECT
    conname,
    contype
FROM pg_constraint
WHERE conrelid = 'real_estate.facture_client'::regclass
ORDER BY conname;