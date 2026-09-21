-- GAP-BUS-004: incoming hunter invoices and explicit conformity evidence.
-- SOURCE: StarterPack hunter journey, steps 10-12 at baseline 902207e3.
-- PROJECT DECISIONS: structured submission, ADMIN review, preserved rejected
-- versions, one pending/conforming invoice per payment. No historical backfill.
-- Existing remuneration snapshots and payment states remain in paiement.
\set ON_ERROR_STOP on
BEGIN;

DO $$
BEGIN
    IF (SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '015') <> 1 THEN
        RAISE EXCEPTION 'Migration 016 requires migration 015';
    END IF;
    IF EXISTS (SELECT 1 FROM migration_control.schema_version WHERE version = '016') THEN
        RAISE EXCEPTION 'Migration 016 has already been applied';
    END IF;
END;
$$;

CREATE TABLE real_estate.facture_chasseur (
    id_facture_chasseur BIGINT GENERATED ALWAYS AS IDENTITY,
    id_paiement BIGINT NOT NULL,
    id_chasseur BIGINT NOT NULL,
    numero_version INTEGER NOT NULL,
    numero_facture VARCHAR(80) NOT NULL,
    date_facture DATE NOT NULL,
    montant NUMERIC(14,2) NOT NULL,
    date_soumission TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(20) NOT NULL DEFAULT 'SOUMISE',
    date_verification TIMESTAMPTZ,
    id_verificateur BIGINT,
    motif_rejet TEXT,
    CONSTRAINT pk_facture_chasseur PRIMARY KEY (id_facture_chasseur),
    CONSTRAINT fk_facture_chasseur_paiement FOREIGN KEY (id_paiement)
        REFERENCES real_estate.paiement(id_paiement) ON DELETE RESTRICT,
    CONSTRAINT fk_facture_chasseur_chasseur FOREIGN KEY (id_chasseur)
        REFERENCES real_estate.chasseur(id_chasseur) ON DELETE RESTRICT,
    CONSTRAINT fk_facture_chasseur_verificateur FOREIGN KEY (id_verificateur)
        REFERENCES real_estate.utilisateur(id_utilisateur) ON DELETE RESTRICT,
    CONSTRAINT uq_facture_chasseur_paiement_version UNIQUE (id_paiement, numero_version),
    CONSTRAINT ck_facture_chasseur_version CHECK (numero_version > 0),
    CONSTRAINT ck_facture_chasseur_numero CHECK (LENGTH(TRIM(numero_facture)) > 0),
    CONSTRAINT ck_facture_chasseur_montant CHECK (montant > 0),
    CONSTRAINT ck_facture_chasseur_statut CHECK (statut IN ('SOUMISE', 'CONFORME', 'REJETEE')),
    CONSTRAINT ck_facture_chasseur_verification CHECK (
        (statut = 'SOUMISE' AND date_verification IS NULL AND id_verificateur IS NULL AND motif_rejet IS NULL)
        OR (statut = 'CONFORME' AND date_verification IS NOT NULL AND id_verificateur IS NOT NULL AND motif_rejet IS NULL)
        OR (statut = 'REJETEE' AND date_verification IS NOT NULL AND id_verificateur IS NOT NULL
            AND motif_rejet IS NOT NULL AND LENGTH(TRIM(motif_rejet)) > 0)
    ),
    CONSTRAINT ck_facture_chasseur_dates CHECK (
        date_verification IS NULL OR date_verification >= date_soumission
    )
);

CREATE UNIQUE INDEX uq_facture_chasseur_active ON real_estate.facture_chasseur(id_paiement)
    WHERE statut IN ('SOUMISE', 'CONFORME');
CREATE INDEX idx_facture_chasseur_chasseur ON real_estate.facture_chasseur(id_chasseur);
CREATE INDEX idx_facture_chasseur_statut ON real_estate.facture_chasseur(statut);

COMMENT ON TABLE real_estate.facture_chasseur IS
    'Incoming structured hunter invoice. Rejected submissions are retained; remuneration remains in paiement.';
COMMENT ON COLUMN real_estate.facture_chasseur.numero_facture IS
    'Hunter-supplied reference, scoped to the payment history; corrections may retain it. Not a company-generated number.';
COMMENT ON COLUMN real_estate.facture_chasseur.montant IS
    'Submitted amount, compared with paiement.montant_chasseur at conformity verification. No recalculation.';

INSERT INTO migration_control.schema_version(version, description)
VALUES ('016', 'Add hunter invoice submission and conformity verification');
COMMIT;
