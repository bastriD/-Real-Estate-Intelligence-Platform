-- =====================================================================
-- File: database/olap/001_warehouse_schema.sql
-- Project: Chasse Immobiliere
-- Purpose:
--   Create the initial analytical Data Warehouse structure.
--
-- Source of truth:
--   real_estate OLTP schema
--
-- Architecture:
--   OLTP -> warehouse -> analytics
--
-- Important:
--   - This script creates structures only.
--   - It does NOT load data.
--   - OLTP remains the authoritative source of truth.
--   - Direct client PII is intentionally excluded from the warehouse.
-- =====================================================================

BEGIN;

-- =====================================================================
-- 1. WAREHOUSE SCHEMA
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS warehouse;

COMMENT ON SCHEMA warehouse IS
'Analytical Data Warehouse populated from the real_estate OLTP schema.';


-- =====================================================================
-- 2. DATE DIMENSION
-- =====================================================================

CREATE TABLE warehouse.dim_date (
    date_key            INTEGER PRIMARY KEY,
    full_date           DATE NOT NULL UNIQUE,

    day_of_month        SMALLINT NOT NULL,
    day_of_week         SMALLINT NOT NULL,
    day_name            VARCHAR(16) NOT NULL,

    week_of_year        SMALLINT NOT NULL,

    month_number        SMALLINT NOT NULL,
    month_name          VARCHAR(16) NOT NULL,

    quarter_number      SMALLINT NOT NULL,

    year_number         SMALLINT NOT NULL,

    is_weekend          BOOLEAN NOT NULL,

    CONSTRAINT ck_dim_date_day
        CHECK (day_of_month BETWEEN 1 AND 31),

    CONSTRAINT ck_dim_date_day_of_week
        CHECK (day_of_week BETWEEN 1 AND 7),

    CONSTRAINT ck_dim_date_month
        CHECK (month_number BETWEEN 1 AND 12),

    CONSTRAINT ck_dim_date_quarter
        CHECK (quarter_number BETWEEN 1 AND 4)
);

COMMENT ON TABLE warehouse.dim_date IS
'Calendar dimension used by all analytical fact tables.';


-- =====================================================================
-- 3. CLIENT DIMENSION
--
-- Privacy by Design:
-- Direct PII such as:
--   nom
--   prenom
--   email
--   telephone
--
-- is deliberately NOT copied into the analytical warehouse.
--
-- id_client_source is retained only for controlled ETL reconciliation.
-- =====================================================================

CREATE TABLE warehouse.dim_client (
    client_key              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_client_source        BIGINT NOT NULL UNIQUE,

    ville                   VARCHAR(255),

    date_creation           TIMESTAMPTZ NOT NULL,

    statut                  VARCHAR(100) NOT NULL,

    consentement_contact    BOOLEAN NOT NULL,

    warehouse_loaded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE warehouse.dim_client IS
'Pseudonymised analytical client dimension. Direct identifying PII is excluded.';

COMMENT ON COLUMN warehouse.dim_client.id_client_source IS
'OLTP technical identifier retained for controlled ETL reconciliation; access must be restricted.';


-- =====================================================================
-- 4. CHASSEUR DIMENSION
--
-- Direct contact PII is also excluded from the first warehouse model.
-- =====================================================================

CREATE TABLE warehouse.dim_chasseur (
    chasseur_key            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_chasseur_source      BIGINT NOT NULL UNIQUE,

    date_entree             DATE,

    statut                  VARCHAR(100) NOT NULL,

    warehouse_loaded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE warehouse.dim_chasseur IS
'Analytical chasseur dimension without email, telephone, name or surname.';


-- =====================================================================
-- 5. SOURCE DIMENSION
-- =====================================================================

CREATE TABLE warehouse.dim_source (
    source_key              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_source_source        BIGINT NOT NULL UNIQUE,

    nom                     VARCHAR(255) NOT NULL,

    type_source             VARCHAR(100) NOT NULL,

    actif                   BOOLEAN NOT NULL,

    niveau_confiance        VARCHAR(100),

    date_creation           TIMESTAMPTZ NOT NULL,

    warehouse_loaded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE warehouse.dim_source IS
'Analytical dimension describing property data sources.';


-- =====================================================================
-- 6. SECTEUR DIMENSION
-- =====================================================================

CREATE TABLE warehouse.dim_secteur (
    secteur_key             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_secteur_source       BIGINT NOT NULL UNIQUE,

    pays                    VARCHAR(255) NOT NULL,

    ville                   VARCHAR(255) NOT NULL,

    quartier                VARCHAR(255),

    code_postal             VARCHAR(32),

    actif                   BOOLEAN NOT NULL,

    warehouse_loaded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE warehouse.dim_secteur IS
'Geographical analytical dimension.';


-- =====================================================================
-- 7. BIEN DIMENSION
-- =====================================================================

CREATE TABLE warehouse.dim_bien (
    bien_key                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_bien_source          BIGINT NOT NULL UNIQUE,

    reference_externe       VARCHAR(255) NOT NULL,

    type_bien               VARCHAR(100) NOT NULL,

    code_postal             VARCHAR(32),

    ville                   VARCHAR(255),

    prix                    NUMERIC,

    surface                 NUMERIC,

    nb_pieces               INTEGER,

    nb_chambres             INTEGER,

    dpe                     CHAR(1),

    statut                  VARCHAR(100) NOT NULL,

    date_publication        TIMESTAMPTZ,

    date_collecte           TIMESTAMPTZ NOT NULL,

    source_key              BIGINT NOT NULL,

    warehouse_loaded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_dim_bien_source
        FOREIGN KEY (source_key)
        REFERENCES warehouse.dim_source(source_key),

    CONSTRAINT ck_dim_bien_prix
        CHECK (prix IS NULL OR prix >= 0),

    CONSTRAINT ck_dim_bien_surface
        CHECK (surface IS NULL OR surface > 0),

    CONSTRAINT ck_dim_bien_nb_pieces
        CHECK (nb_pieces IS NULL OR nb_pieces >= 0),

    CONSTRAINT ck_dim_bien_nb_chambres
        CHECK (nb_chambres IS NULL OR nb_chambres >= 0)
);

COMMENT ON TABLE warehouse.dim_bien IS
'Property dimension used for analytical and future matching/ML workloads.';


-- =====================================================================
-- 8. DEMANDE VERSION DIMENSION
--
-- This dimension is intentionally preserved because one search evolves
-- over time and each version contains the criteria used for matching.
--
-- This will later be particularly useful for:
--   - matching analytics
--   - feature engineering
--   - ML training datasets
--   - search evolution analysis
-- =====================================================================

CREATE TABLE warehouse.dim_demande_version (
    demande_version_key     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_demande_version_source BIGINT NOT NULL UNIQUE,

    id_demande_source       BIGINT NOT NULL,

    numero_version          INTEGER NOT NULL,

    date_version            TIMESTAMPTZ NOT NULL,

    ville                   VARCHAR(255),

    code_postal             VARCHAR(32),

    type_bien               VARCHAR(100),

    budget_min              NUMERIC,

    budget_max              NUMERIC,

    surface_min             NUMERIC,

    nb_pieces_min           INTEGER,

    nb_chambres_min         INTEGER,

    dpe_max                 CHAR(1),

    criteres_souhaites      JSONB NOT NULL,

    active                  BOOLEAN NOT NULL,

    auteur_type             VARCHAR(32) NOT NULL,

    warehouse_loaded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_dim_demande_version_numero
        CHECK (numero_version > 0),

    CONSTRAINT ck_dim_demande_version_budget
        CHECK (
            budget_min IS NULL
            OR budget_max IS NULL
            OR budget_max >= budget_min
        ),

    CONSTRAINT ck_dim_demande_version_surface
        CHECK (
            surface_min IS NULL
            OR surface_min > 0
        ),

    CONSTRAINT ck_dim_demande_version_pieces
        CHECK (
            nb_pieces_min IS NULL
            OR nb_pieces_min >= 0
        ),

    CONSTRAINT ck_dim_demande_version_chambres
        CHECK (
            nb_chambres_min IS NULL
            OR nb_chambres_min >= 0
        ),

    CONSTRAINT ck_dim_demande_version_auteur
        CHECK (
            auteur_type IN (
                'CLIENT',
                'CHASSEUR',
                'SYSTEME',
                'INCONNU'
            )
        )
);

COMMENT ON TABLE warehouse.dim_demande_version IS
'Historical search criteria dimension. One OLTP demande_version becomes one analytical dimension member.';


-- =====================================================================
-- 9. FACT MANDAT
--
-- Grain:
--   EXACTLY ONE ROW PER OLTP MANDAT
-- =====================================================================

CREATE TABLE warehouse.fact_mandat (
    mandat_fact_key         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_mandat_source        BIGINT NOT NULL UNIQUE,

    reference_mandat        VARCHAR(255) NOT NULL,

    client_key              BIGINT NOT NULL,

    chasseur_key            BIGINT NOT NULL,

    date_signature_key      INTEGER NOT NULL,

    date_debut_key          INTEGER NOT NULL,

    date_fin_key            INTEGER NOT NULL,

    type_mandat             VARCHAR(100) NOT NULL,

    mode_signature          VARCHAR(100) NOT NULL,

    statut                  VARCHAR(100) NOT NULL,

    est_exclusif            BOOLEAN NOT NULL,

    duree_jours             INTEGER NOT NULL,

    mandat_count            SMALLINT NOT NULL DEFAULT 1,

    warehouse_loaded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_fact_mandat_client
        FOREIGN KEY (client_key)
        REFERENCES warehouse.dim_client(client_key),

    CONSTRAINT fk_fact_mandat_chasseur
        FOREIGN KEY (chasseur_key)
        REFERENCES warehouse.dim_chasseur(chasseur_key),

    CONSTRAINT fk_fact_mandat_date_signature
        FOREIGN KEY (date_signature_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT fk_fact_mandat_date_debut
        FOREIGN KEY (date_debut_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT fk_fact_mandat_date_fin
        FOREIGN KEY (date_fin_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT ck_fact_mandat_duree
        CHECK (duree_jours >= 0),

    CONSTRAINT ck_fact_mandat_count
        CHECK (mandat_count = 1)
);

COMMENT ON TABLE warehouse.fact_mandat IS
'Fact table at one-row-per-mandat grain.';


-- =====================================================================
-- 10. MANDAT <-> SECTEUR BRIDGE
--
-- OLTP explicitly allows one mandate to be associated with multiple
-- sectors through real_estate.mandat_secteur.
--
-- Therefore secteur_key MUST NOT be placed directly into fact_mandat.
-- =====================================================================

CREATE TABLE warehouse.bridge_mandat_secteur (
    mandat_fact_key         BIGINT NOT NULL,

    secteur_key             BIGINT NOT NULL,

    warehouse_loaded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (
        mandat_fact_key,
        secteur_key
    ),

    CONSTRAINT fk_bridge_mandat_secteur_mandat
        FOREIGN KEY (mandat_fact_key)
        REFERENCES warehouse.fact_mandat(mandat_fact_key)
        ON DELETE CASCADE,

    CONSTRAINT fk_bridge_mandat_secteur_secteur
        FOREIGN KEY (secteur_key)
        REFERENCES warehouse.dim_secteur(secteur_key)
);

COMMENT ON TABLE warehouse.bridge_mandat_secteur IS
'Bridge preserving the many-to-many relationship between mandates and geographical sectors.';


-- =====================================================================
-- 11. FACT PRESENTATION
--
-- Grain:
--   EXACTLY ONE ROW PER OLTP PRESENTATION
--
-- Business meaning:
--   One property considered/presented for one version of a customer
--   search.
--
-- Important future ML dataset:
--
--   demande_version
--          +
--        bien
--          +
--   score_matching
--          +
--        statut
-- =====================================================================

CREATE TABLE warehouse.fact_presentation (
    presentation_fact_key       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_presentation_source      BIGINT NOT NULL UNIQUE,

    demande_version_key         BIGINT NOT NULL,

    bien_key                    BIGINT NOT NULL,

    client_key                  BIGINT NOT NULL,

    chasseur_key                BIGINT NOT NULL,

    date_selection_key          INTEGER NOT NULL,

    date_presentation_key       INTEGER,

    score_matching              NUMERIC,

    statut                      VARCHAR(100) NOT NULL,

    presentation_count          SMALLINT NOT NULL DEFAULT 1,

    warehouse_loaded_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_fact_presentation_demande_version
        FOREIGN KEY (demande_version_key)
        REFERENCES warehouse.dim_demande_version(demande_version_key),

    CONSTRAINT fk_fact_presentation_bien
        FOREIGN KEY (bien_key)
        REFERENCES warehouse.dim_bien(bien_key),

    CONSTRAINT fk_fact_presentation_client
        FOREIGN KEY (client_key)
        REFERENCES warehouse.dim_client(client_key),

    CONSTRAINT fk_fact_presentation_chasseur
        FOREIGN KEY (chasseur_key)
        REFERENCES warehouse.dim_chasseur(chasseur_key),

    CONSTRAINT fk_fact_presentation_date_selection
        FOREIGN KEY (date_selection_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT fk_fact_presentation_date_presentation
        FOREIGN KEY (date_presentation_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT ck_fact_presentation_score
        CHECK (
            score_matching IS NULL
            OR score_matching >= 0
        ),

    CONSTRAINT ck_fact_presentation_count
        CHECK (presentation_count = 1)
);

COMMENT ON TABLE warehouse.fact_presentation IS
'Fact table at one-row-per-property-presentation/search-version grain.';


-- =====================================================================
-- 12. FACT PAIEMENT
--
-- Grain:
--   EXACTLY ONE ROW PER OLTP PAIEMENT
--
-- IMPORTANT:
-- paiement is related to mandat.
--
-- There is currently NO legitimate OLTP relationship:
--
-- paiement -> bien
--
-- Therefore this warehouse fact intentionally contains no bien_key.
-- =====================================================================

CREATE TABLE warehouse.fact_paiement (
    paiement_fact_key               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_paiement_source              BIGINT NOT NULL UNIQUE,

    id_bareme_source                BIGINT,

    mandat_fact_key                 BIGINT NOT NULL,

    client_key                      BIGINT NOT NULL,

    chasseur_key                    BIGINT NOT NULL,

    date_acte_authentique_key       INTEGER,

    date_reception_honoraires_key   INTEGER,

    date_paiement_chasseur_key      INTEGER,

    montant_achat                   NUMERIC,

    montant_honoraires              NUMERIC,

    montant_chasseur                NUMERIC,

    statut                          VARCHAR(100) NOT NULL,

    paiement_count                  SMALLINT NOT NULL DEFAULT 1,

    warehouse_loaded_at             TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_fact_paiement_mandat
        FOREIGN KEY (mandat_fact_key)
        REFERENCES warehouse.fact_mandat(mandat_fact_key),

    CONSTRAINT fk_fact_paiement_client
        FOREIGN KEY (client_key)
        REFERENCES warehouse.dim_client(client_key),

    CONSTRAINT fk_fact_paiement_chasseur
        FOREIGN KEY (chasseur_key)
        REFERENCES warehouse.dim_chasseur(chasseur_key),

    CONSTRAINT fk_fact_paiement_date_acte
        FOREIGN KEY (date_acte_authentique_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT fk_fact_paiement_date_reception
        FOREIGN KEY (date_reception_honoraires_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT fk_fact_paiement_date_chasseur
        FOREIGN KEY (date_paiement_chasseur_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT ck_fact_paiement_montant_achat
        CHECK (
            montant_achat IS NULL
            OR montant_achat >= 0
        ),

    CONSTRAINT ck_fact_paiement_honoraires
        CHECK (
            montant_honoraires IS NULL
            OR montant_honoraires >= 0
        ),

    CONSTRAINT ck_fact_paiement_chasseur
        CHECK (
            montant_chasseur IS NULL
            OR montant_chasseur >= 0
        ),

    CONSTRAINT ck_fact_paiement_count
        CHECK (paiement_count = 1)
);

COMMENT ON TABLE warehouse.fact_paiement IS
'Financial fact table at one-row-per-payment grain. No property relationship is fabricated.';


-- =====================================================================
-- 13. INDEXES
-- =====================================================================

CREATE INDEX idx_dim_bien_source_key
    ON warehouse.dim_bien(source_key);

CREATE INDEX idx_dim_bien_ville
    ON warehouse.dim_bien(ville);

CREATE INDEX idx_dim_bien_type_bien
    ON warehouse.dim_bien(type_bien);

CREATE INDEX idx_dim_bien_dpe
    ON warehouse.dim_bien(dpe);

CREATE INDEX idx_dim_demande_version_demande
    ON warehouse.dim_demande_version(id_demande_source);

CREATE INDEX idx_dim_demande_version_type_bien
    ON warehouse.dim_demande_version(type_bien);

CREATE INDEX idx_dim_demande_version_ville
    ON warehouse.dim_demande_version(ville);

CREATE INDEX idx_fact_mandat_client
    ON warehouse.fact_mandat(client_key);

CREATE INDEX idx_fact_mandat_chasseur
    ON warehouse.fact_mandat(chasseur_key);

CREATE INDEX idx_fact_mandat_signature
    ON warehouse.fact_mandat(date_signature_key);

CREATE INDEX idx_fact_presentation_demande_version
    ON warehouse.fact_presentation(demande_version_key);

CREATE INDEX idx_fact_presentation_bien
    ON warehouse.fact_presentation(bien_key);

CREATE INDEX idx_fact_presentation_client
    ON warehouse.fact_presentation(client_key);

CREATE INDEX idx_fact_presentation_chasseur
    ON warehouse.fact_presentation(chasseur_key);

CREATE INDEX idx_fact_presentation_selection_date
    ON warehouse.fact_presentation(date_selection_key);

CREATE INDEX idx_fact_paiement_mandat
    ON warehouse.fact_paiement(mandat_fact_key);

CREATE INDEX idx_fact_paiement_client
    ON warehouse.fact_paiement(client_key);

CREATE INDEX idx_fact_paiement_chasseur
    ON warehouse.fact_paiement(chasseur_key);

CREATE INDEX idx_bridge_mandat_secteur_secteur
    ON warehouse.bridge_mandat_secteur(secteur_key);


-- =====================================================================
-- 14. COMPLETION
-- =====================================================================

COMMIT;