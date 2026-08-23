BEGIN;

-- =====================================================================
-- MIGRATION 003
-- REAL ESTATE ANALYTICAL DATA WAREHOUSE
--
-- Architecture:
--
-- RAW / STAGING
--       |
--       v
-- real_estate OLTP
--       |
--       v
-- warehouse
--
-- Analytical domains:
--
-- 1. Market analytics
--    - advertisements
--    - prices
--    - price/m2
--    - locations
--    - sources
--
-- 2. Business analytics
--    - mandates
--    - customers
--    - hunters
--    - search versions
--    - presentations / matching
--    - payments
--
-- OLTP remains the authoritative source of truth.
-- =====================================================================


-- =====================================================================
-- 1. WAREHOUSE SCHEMA
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS warehouse;

COMMENT ON SCHEMA warehouse IS
'Analytical warehouse populated from the real_estate OLTP and ingestion layers.';


-- =====================================================================
-- 2. DATE DIMENSION
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key integer PRIMARY KEY,
    date_complete date NOT NULL UNIQUE,
    jour smallint NOT NULL,
    jour_semaine smallint NOT NULL,
    nom_jour varchar(20) NOT NULL,
    semaine_annee smallint NOT NULL,
    mois smallint NOT NULL,
    nom_mois varchar(20) NOT NULL,
    trimestre smallint NOT NULL,
    annee smallint NOT NULL,
    est_weekend boolean NOT NULL,

    CONSTRAINT ck_dim_date_key_positive
        CHECK (date_key > 0),

    CONSTRAINT ck_dim_date_jour
        CHECK (jour BETWEEN 1 AND 31),

    CONSTRAINT ck_dim_date_jour_semaine
        CHECK (jour_semaine BETWEEN 1 AND 7),

    CONSTRAINT ck_dim_date_semaine
        CHECK (semaine_annee BETWEEN 1 AND 53),

    CONSTRAINT ck_dim_date_mois
        CHECK (mois BETWEEN 1 AND 12),

    CONSTRAINT ck_dim_date_trimestre
        CHECK (trimestre BETWEEN 1 AND 4)
);

COMMENT ON TABLE warehouse.dim_date IS
'Shared calendar dimension for all warehouse fact tables.';

CREATE INDEX IF NOT EXISTS idx_dim_date_annee_mois
    ON warehouse.dim_date (annee, mois);

CREATE INDEX IF NOT EXISTS idx_dim_date_annee_semaine
    ON warehouse.dim_date (annee, semaine_annee);


-- =====================================================================
-- 3. SOURCE DIMENSION
-- SCD-style dimension
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_source (
    source_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_source_source bigint NOT NULL,
    nom varchar(150) NOT NULL,
    type_source varchar(40) NOT NULL,
    url_base text,
    actif boolean NOT NULL,
    niveau_confiance varchar(20),
    date_creation_source timestamptz,

    valid_from timestamptz NOT NULL,
    valid_to timestamptz,
    is_current boolean NOT NULL DEFAULT true,

    dw_created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dw_updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_dim_source_confiance
        CHECK (
            niveau_confiance IS NULL
            OR niveau_confiance IN ('FAIBLE', 'MOYEN', 'ELEVE')
        ),

    CONSTRAINT ck_dim_source_validity
        CHECK (
            valid_to IS NULL
            OR valid_to >= valid_from
        )
);

COMMENT ON TABLE warehouse.dim_source IS
'Property data-source dimension with historisation support.';

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_source_current
    ON warehouse.dim_source (id_source_source)
    WHERE is_current = true;

CREATE INDEX IF NOT EXISTS idx_dim_source_business_key
    ON warehouse.dim_source (id_source_source);

CREATE INDEX IF NOT EXISTS idx_dim_source_validity
    ON warehouse.dim_source (
        id_source_source,
        valid_from,
        valid_to
    );


-- =====================================================================
-- 4. MARKET LOCATION DIMENSION
--
-- Represents the geographical location of an advertisement/property.
-- This is intentionally distinct from dim_secteur, which represents
-- the business search-sector entity.
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_localisation (
    localisation_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pays varchar(100) NOT NULL,
    code_postal varchar(20),
    ville varchar(120) NOT NULL,
    region varchar(120),
    departement_region varchar(120),

    dw_created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dw_updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_dim_localisation_business
        UNIQUE (pays, code_postal, ville)
);

COMMENT ON TABLE warehouse.dim_localisation IS
'Geographical dimension used for market and advertisement analytics.';

CREATE INDEX IF NOT EXISTS idx_dim_localisation_ville
    ON warehouse.dim_localisation (ville);

CREATE INDEX IF NOT EXISTS idx_dim_localisation_code_postal
    ON warehouse.dim_localisation (code_postal);


-- =====================================================================
-- 5. PROPERTY DIMENSION
-- SCD-style dimension
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_bien (
    bien_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_bien_source bigint,
    id_source_source bigint NOT NULL,

    reference_externe varchar(150) NOT NULL,
    titre varchar(255),
    type_bien varchar(50) NOT NULL,

    adresse text,

    latitude numeric(9,6),
    longitude numeric(9,6),

    dpe char(1),
    statut varchar(20),

    valid_from timestamptz NOT NULL,
    valid_to timestamptz,
    is_current boolean NOT NULL DEFAULT true,

    dw_created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dw_updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_dim_bien_latitude
        CHECK (
            latitude IS NULL
            OR latitude BETWEEN -90 AND 90
        ),

    CONSTRAINT ck_dim_bien_longitude
        CHECK (
            longitude IS NULL
            OR longitude BETWEEN -180 AND 180
        ),

    CONSTRAINT ck_dim_bien_dpe
        CHECK (
            dpe IS NULL
            OR dpe IN ('A','B','C','D','E','F','G')
        ),

    CONSTRAINT ck_dim_bien_statut
        CHECK (
            statut IS NULL
            OR statut IN (
                'ACTIF',
                'EXPIRE',
                'VENDU',
                'INDISPONIBLE'
            )
        ),

    CONSTRAINT ck_dim_bien_validity
        CHECK (
            valid_to IS NULL
            OR valid_to >= valid_from
        )
);

COMMENT ON TABLE warehouse.dim_bien IS
'Property dimension shared by market analytics and matching analytics.';

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_bien_current
    ON warehouse.dim_bien (
        id_source_source,
        reference_externe
    )
    WHERE is_current = true;

CREATE INDEX IF NOT EXISTS idx_dim_bien_business_key
    ON warehouse.dim_bien (
        id_source_source,
        reference_externe
    );

CREATE INDEX IF NOT EXISTS idx_dim_bien_type
    ON warehouse.dim_bien (type_bien);

CREATE INDEX IF NOT EXISTS idx_dim_bien_dpe
    ON warehouse.dim_bien (dpe);

CREATE INDEX IF NOT EXISTS idx_dim_bien_validity
    ON warehouse.dim_bien (
        id_source_source,
        reference_externe,
        valid_from,
        valid_to
    );


-- =====================================================================
-- 6. CLIENT DIMENSION
--
-- Privacy by Design:
--
-- Direct identifying data is deliberately excluded:
-- - nom
-- - prenom
-- - email
-- - telephone
--
-- id_client_source is retained strictly for ETL reconciliation and
-- controlled lineage.
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_client (
    client_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_client_source bigint NOT NULL,

    ville varchar(120),
    date_creation_source timestamptz,
    statut varchar(40) NOT NULL,
    consentement_contact boolean NOT NULL,

    dw_created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dw_updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_dim_client_source
        UNIQUE (id_client_source)
);

COMMENT ON TABLE warehouse.dim_client IS
'Pseudonymised analytical customer dimension. Direct PII is intentionally excluded.';


-- =====================================================================
-- 7. CHASSEUR DIMENSION
--
-- Contact PII is excluded from the analytical warehouse.
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_chasseur (
    chasseur_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_chasseur_source bigint NOT NULL,

    date_entree date,
    statut varchar(40) NOT NULL,

    dw_created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dw_updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_dim_chasseur_source
        UNIQUE (id_chasseur_source)
);

COMMENT ON TABLE warehouse.dim_chasseur IS
'Analytical hunter dimension without direct identity/contact attributes.';


-- =====================================================================
-- 8. BUSINESS SECTOR DIMENSION
--
-- This represents real_estate.secteur.
--
-- It must remain separate from dim_localisation because a sector is a
-- business search perimeter associated with mandates.
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_secteur (
    secteur_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_secteur_source bigint NOT NULL,

    pays varchar(100) NOT NULL,
    ville varchar(120) NOT NULL,
    quartier varchar(120),
    code_postal varchar(20),

    actif boolean NOT NULL,

    dw_created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dw_updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_dim_secteur_source
        UNIQUE (id_secteur_source)
);

COMMENT ON TABLE warehouse.dim_secteur IS
'Business geographical search-sector dimension originating from real_estate.secteur.';

CREATE INDEX IF NOT EXISTS idx_dim_secteur_ville
    ON warehouse.dim_secteur (ville);

CREATE INDEX IF NOT EXISTS idx_dim_secteur_code_postal
    ON warehouse.dim_secteur (code_postal);


-- =====================================================================
-- 9. SEARCH VERSION DIMENSION
--
-- One member represents one historical version of one customer search.
--
-- This dimension is essential for:
-- - search evolution analysis
-- - matching analytics
-- - ML feature engineering
-- - AI feasibility analysis
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_demande_version (
    demande_version_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_demande_version_source bigint NOT NULL,
    id_demande_source bigint NOT NULL,

    numero_version integer NOT NULL,
    date_version timestamptz NOT NULL,

    ville varchar(120),
    code_postal varchar(20),
    type_bien varchar(50),

    budget_min numeric(14,2),
    budget_max numeric(14,2),

    surface_min numeric(10,2),

    nb_pieces_min integer,
    nb_chambres_min integer,

    dpe_max char(1),

    criteres_souhaites jsonb NOT NULL,

    active boolean NOT NULL,

    auteur_type varchar(20) NOT NULL,

    dw_created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dw_updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_dim_demande_version_source
        UNIQUE (id_demande_version_source),

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

    CONSTRAINT ck_dim_demande_version_dpe
        CHECK (
            dpe_max IS NULL
            OR dpe_max IN ('A','B','C','D','E','F','G')
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
'Historical customer search criteria dimension used by analytics and future ML matching.';

CREATE INDEX IF NOT EXISTS idx_dim_demande_version_demande
    ON warehouse.dim_demande_version (id_demande_source);

CREATE INDEX IF NOT EXISTS idx_dim_demande_version_ville
    ON warehouse.dim_demande_version (ville);

CREATE INDEX IF NOT EXISTS idx_dim_demande_version_type_bien
    ON warehouse.dim_demande_version (type_bien);


-- =====================================================================
-- 10. MARKET FACT: ADVERTISEMENT OBSERVATION
--
-- Grain:
-- one property advertisement observation per ingestion batch.
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.fact_annonce (
    annonce_fact_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    bien_key bigint NOT NULL,
    source_key bigint NOT NULL,
    localisation_key bigint NOT NULL,

    publication_date_key integer NOT NULL,
    collection_date_key integer NOT NULL,

    prix numeric(12,2) NOT NULL,
    surface numeric(10,2) NOT NULL,
    prix_m2 numeric(14,2) NOT NULL,

    nb_pieces integer,
    nb_chambres integer,

    annonce_count smallint NOT NULL DEFAULT 1,

    reference_externe varchar(150) NOT NULL,

    ingestion_batch text NOT NULL,
    source_file text NOT NULL,

    date_collecte_exacte timestamptz NOT NULL,
    date_publication_exacte timestamptz NOT NULL,

    dw_loaded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_fact_annonce_bien
        FOREIGN KEY (bien_key)
        REFERENCES warehouse.dim_bien (bien_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_annonce_source
        FOREIGN KEY (source_key)
        REFERENCES warehouse.dim_source (source_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_annonce_localisation
        FOREIGN KEY (localisation_key)
        REFERENCES warehouse.dim_localisation (localisation_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_annonce_publication_date
        FOREIGN KEY (publication_date_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_annonce_collection_date
        FOREIGN KEY (collection_date_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

    CONSTRAINT ck_fact_annonce_prix
        CHECK (prix >= 0),

    CONSTRAINT ck_fact_annonce_surface
        CHECK (surface > 0),

    CONSTRAINT ck_fact_annonce_prix_m2
        CHECK (prix_m2 >= 0),

    CONSTRAINT ck_fact_annonce_pieces
        CHECK (
            nb_pieces IS NULL
            OR nb_pieces >= 0
        ),

    CONSTRAINT ck_fact_annonce_chambres
        CHECK (
            nb_chambres IS NULL
            OR nb_chambres >= 0
        ),

    CONSTRAINT ck_fact_annonce_count
        CHECK (annonce_count = 1),

    CONSTRAINT uq_fact_annonce_observation
        UNIQUE (
            source_key,
            reference_externe,
            ingestion_batch
        )
);

COMMENT ON TABLE warehouse.fact_annonce IS
'Market observation fact: one property advertisement observation per ingestion batch.';

CREATE INDEX IF NOT EXISTS idx_fact_annonce_bien
    ON warehouse.fact_annonce (bien_key);

CREATE INDEX IF NOT EXISTS idx_fact_annonce_source
    ON warehouse.fact_annonce (source_key);

CREATE INDEX IF NOT EXISTS idx_fact_annonce_localisation
    ON warehouse.fact_annonce (localisation_key);

CREATE INDEX IF NOT EXISTS idx_fact_annonce_publication_date
    ON warehouse.fact_annonce (publication_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_annonce_collection_date
    ON warehouse.fact_annonce (collection_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_annonce_batch
    ON warehouse.fact_annonce (ingestion_batch);

CREATE INDEX IF NOT EXISTS idx_fact_annonce_prix
    ON warehouse.fact_annonce (prix);

CREATE INDEX IF NOT EXISTS idx_fact_annonce_prix_m2
    ON warehouse.fact_annonce (prix_m2);


-- =====================================================================
-- 11. BUSINESS FACT: MANDATE
--
-- Grain:
-- exactly one row per OLTP mandate.
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.fact_mandat (
    mandat_fact_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_mandat_source bigint NOT NULL,
    reference_mandat varchar(150) NOT NULL,

    client_key bigint NOT NULL,
    chasseur_key bigint NOT NULL,

    date_signature_key integer NOT NULL,
    date_debut_key integer NOT NULL,
    date_fin_key integer NOT NULL,

    type_mandat varchar(40) NOT NULL,
    mode_signature varchar(40) NOT NULL,
    statut varchar(40) NOT NULL,

    est_exclusif boolean NOT NULL,

    duree_jours integer NOT NULL,

    mandat_count smallint NOT NULL DEFAULT 1,

    dw_loaded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_fact_mandat_source
        UNIQUE (id_mandat_source),

    CONSTRAINT fk_fact_mandat_client
        FOREIGN KEY (client_key)
        REFERENCES warehouse.dim_client (client_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_mandat_chasseur
        FOREIGN KEY (chasseur_key)
        REFERENCES warehouse.dim_chasseur (chasseur_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_mandat_date_signature
        FOREIGN KEY (date_signature_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_mandat_date_debut
        FOREIGN KEY (date_debut_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_mandat_date_fin
        FOREIGN KEY (date_fin_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

    CONSTRAINT ck_fact_mandat_duree
        CHECK (duree_jours >= 0),

    CONSTRAINT ck_fact_mandat_count
        CHECK (mandat_count = 1)
);

COMMENT ON TABLE warehouse.fact_mandat IS
'Business fact at exactly one row per mandate.';

CREATE INDEX IF NOT EXISTS idx_fact_mandat_client
    ON warehouse.fact_mandat (client_key);

CREATE INDEX IF NOT EXISTS idx_fact_mandat_chasseur
    ON warehouse.fact_mandat (chasseur_key);

CREATE INDEX IF NOT EXISTS idx_fact_mandat_signature
    ON warehouse.fact_mandat (date_signature_key);

CREATE INDEX IF NOT EXISTS idx_fact_mandat_statut
    ON warehouse.fact_mandat (statut);


-- =====================================================================
-- 12. MANDATE / SECTOR BRIDGE
--
-- OLTP:
-- mandat N <-> N secteur
--
-- We intentionally preserve the many-to-many relationship rather
-- than forcing a single sector into fact_mandat.
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.bridge_mandat_secteur (
    mandat_fact_key bigint NOT NULL,
    secteur_key bigint NOT NULL,

    dw_loaded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (
        mandat_fact_key,
        secteur_key
    ),

    CONSTRAINT fk_bridge_mandat_secteur_mandat
        FOREIGN KEY (mandat_fact_key)
        REFERENCES warehouse.fact_mandat (mandat_fact_key)
        ON DELETE CASCADE,

    CONSTRAINT fk_bridge_mandat_secteur_secteur
        FOREIGN KEY (secteur_key)
        REFERENCES warehouse.dim_secteur (secteur_key)
        ON DELETE RESTRICT
);

COMMENT ON TABLE warehouse.bridge_mandat_secteur IS
'Bridge preserving the OLTP many-to-many relationship between mandates and business sectors.';

CREATE INDEX IF NOT EXISTS idx_bridge_mandat_secteur_secteur
    ON warehouse.bridge_mandat_secteur (secteur_key);


-- =====================================================================
-- 13. BUSINESS / MATCHING FACT: PRESENTATION
--
-- Grain:
-- exactly one OLTP presentation.
--
-- Analytical meaning:
--
-- demande_version
--       +
--     bien
--       +
-- score_matching
--       +
--    statut
--
-- This is a primary future ML/matching dataset.
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.fact_presentation (
    presentation_fact_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_presentation_source bigint NOT NULL,

    demande_version_key bigint NOT NULL,
    bien_key bigint NOT NULL,

    client_key bigint NOT NULL,
    chasseur_key bigint NOT NULL,

    date_selection_key integer NOT NULL,
    date_presentation_key integer,

    score_matching numeric(10,6),

    statut varchar(40) NOT NULL,

    presentation_count smallint NOT NULL DEFAULT 1,

    dw_loaded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_fact_presentation_source
        UNIQUE (id_presentation_source),

    CONSTRAINT fk_fact_presentation_demande_version
        FOREIGN KEY (demande_version_key)
        REFERENCES warehouse.dim_demande_version (demande_version_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_presentation_bien
        FOREIGN KEY (bien_key)
        REFERENCES warehouse.dim_bien (bien_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_presentation_client
        FOREIGN KEY (client_key)
        REFERENCES warehouse.dim_client (client_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_presentation_chasseur
        FOREIGN KEY (chasseur_key)
        REFERENCES warehouse.dim_chasseur (chasseur_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_presentation_date_selection
        FOREIGN KEY (date_selection_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_presentation_date_presentation
        FOREIGN KEY (date_presentation_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

    CONSTRAINT ck_fact_presentation_score
        CHECK (
            score_matching IS NULL
            OR score_matching >= 0
        ),

    CONSTRAINT ck_fact_presentation_count
        CHECK (presentation_count = 1)
);

COMMENT ON TABLE warehouse.fact_presentation IS
'Matching fact at exactly one property presentation per search version.';

CREATE INDEX IF NOT EXISTS idx_fact_presentation_demande_version
    ON warehouse.fact_presentation (demande_version_key);

CREATE INDEX IF NOT EXISTS idx_fact_presentation_bien
    ON warehouse.fact_presentation (bien_key);

CREATE INDEX IF NOT EXISTS idx_fact_presentation_client
    ON warehouse.fact_presentation (client_key);

CREATE INDEX IF NOT EXISTS idx_fact_presentation_chasseur
    ON warehouse.fact_presentation (chasseur_key);

CREATE INDEX IF NOT EXISTS idx_fact_presentation_selection_date
    ON warehouse.fact_presentation (date_selection_key);

CREATE INDEX IF NOT EXISTS idx_fact_presentation_statut
    ON warehouse.fact_presentation (statut);


-- =====================================================================
-- 14. FINANCIAL FACT: PAYMENT
--
-- Grain:
-- exactly one OLTP payment.
--
-- IMPORTANT:
--
-- OLTP relation:
--
-- paiement -> mandat
--
-- There is currently no direct:
--
-- paiement -> bien
--
-- Therefore NO fabricated bien_key exists here.
-- =====================================================================

CREATE TABLE IF NOT EXISTS warehouse.fact_paiement (
    paiement_fact_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_paiement_source bigint NOT NULL,
    id_bareme_source bigint,

    mandat_fact_key bigint NOT NULL,

    client_key bigint NOT NULL,
    chasseur_key bigint NOT NULL,

    date_acte_authentique_key integer,
    date_reception_honoraires_key integer,
    date_paiement_chasseur_key integer,

    montant_achat numeric(14,2),
    montant_honoraires numeric(14,2),
    montant_chasseur numeric(14,2),

    statut varchar(40) NOT NULL,

    paiement_count smallint NOT NULL DEFAULT 1,

    dw_loaded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_fact_paiement_source
        UNIQUE (id_paiement_source),

    CONSTRAINT fk_fact_paiement_mandat
        FOREIGN KEY (mandat_fact_key)
        REFERENCES warehouse.fact_mandat (mandat_fact_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_paiement_client
        FOREIGN KEY (client_key)
        REFERENCES warehouse.dim_client (client_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_paiement_chasseur
        FOREIGN KEY (chasseur_key)
        REFERENCES warehouse.dim_chasseur (chasseur_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_paiement_date_acte
        FOREIGN KEY (date_acte_authentique_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_paiement_date_reception
        FOREIGN KEY (date_reception_honoraires_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

    CONSTRAINT fk_fact_paiement_date_chasseur
        FOREIGN KEY (date_paiement_chasseur_key)
        REFERENCES warehouse.dim_date (date_key)
        ON DELETE RESTRICT,

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
'Financial fact at exactly one row per OLTP payment. No property relationship is fabricated.';

CREATE INDEX IF NOT EXISTS idx_fact_paiement_mandat
    ON warehouse.fact_paiement (mandat_fact_key);

CREATE INDEX IF NOT EXISTS idx_fact_paiement_client
    ON warehouse.fact_paiement (client_key);

CREATE INDEX IF NOT EXISTS idx_fact_paiement_chasseur
    ON warehouse.fact_paiement (chasseur_key);

CREATE INDEX IF NOT EXISTS idx_fact_paiement_statut
    ON warehouse.fact_paiement (statut);

CREATE INDEX IF NOT EXISTS idx_fact_paiement_date_acte
    ON warehouse.fact_paiement (date_acte_authentique_key);


-- =====================================================================
-- 15. UNKNOWN DIMENSION MEMBERS
--
-- Surrogate key 0 provides a controlled unknown-member strategy for
-- dimensions where ETL may legitimately encounter incomplete mappings.
-- =====================================================================

INSERT INTO warehouse.dim_source (
    source_key,
    id_source_source,
    nom,
    type_source,
    url_base,
    actif,
    niveau_confiance,
    date_creation_source,
    valid_from,
    valid_to,
    is_current,
    dw_created_at,
    dw_updated_at
)
OVERRIDING SYSTEM VALUE
VALUES (
    0,
    0,
    'UNKNOWN',
    'AUTRE',
    NULL,
    false,
    NULL,
    NULL,
    TIMESTAMPTZ '1900-01-01 00:00:00+00',
    NULL,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (source_key) DO NOTHING;


INSERT INTO warehouse.dim_localisation (
    localisation_key,
    pays,
    code_postal,
    ville,
    region,
    departement_region,
    dw_created_at,
    dw_updated_at
)
OVERRIDING SYSTEM VALUE
VALUES (
    0,
    'INCONNU',
    NULL,
    'INCONNUE',
    NULL,
    NULL,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (localisation_key) DO NOTHING;


INSERT INTO warehouse.dim_bien (
    bien_key,
    id_bien_source,
    id_source_source,
    reference_externe,
    titre,
    type_bien,
    adresse,
    latitude,
    longitude,
    dpe,
    statut,
    valid_from,
    valid_to,
    is_current,
    dw_created_at,
    dw_updated_at
)
OVERRIDING SYSTEM VALUE
VALUES (
    0,
    NULL,
    0,
    'UNKNOWN',
    'UNKNOWN',
    'UNKNOWN',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    TIMESTAMPTZ '1900-01-01 00:00:00+00',
    NULL,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (bien_key) DO NOTHING;


INSERT INTO warehouse.dim_client (
    client_key,
    id_client_source,
    ville,
    date_creation_source,
    statut,
    consentement_contact,
    dw_created_at,
    dw_updated_at
)
OVERRIDING SYSTEM VALUE
VALUES (
    0,
    0,
    NULL,
    NULL,
    'INCONNU',
    false,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (client_key) DO NOTHING;


INSERT INTO warehouse.dim_chasseur (
    chasseur_key,
    id_chasseur_source,
    date_entree,
    statut,
    dw_created_at,
    dw_updated_at
)
OVERRIDING SYSTEM VALUE
VALUES (
    0,
    0,
    NULL,
    'INCONNU',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (chasseur_key) DO NOTHING;


INSERT INTO warehouse.dim_secteur (
    secteur_key,
    id_secteur_source,
    pays,
    ville,
    quartier,
    code_postal,
    actif,
    dw_created_at,
    dw_updated_at
)
OVERRIDING SYSTEM VALUE
VALUES (
    0,
    0,
    'INCONNU',
    'INCONNUE',
    NULL,
    NULL,
    false,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (secteur_key) DO NOTHING;


INSERT INTO warehouse.dim_demande_version (
    demande_version_key,
    id_demande_version_source,
    id_demande_source,
    numero_version,
    date_version,
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
    active,
    auteur_type,
    dw_created_at,
    dw_updated_at
)
OVERRIDING SYSTEM VALUE
VALUES (
    0,
    0,
    0,
    1,
    TIMESTAMPTZ '1900-01-01 00:00:00+00',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    '{}'::jsonb,
    false,
    'INCONNU',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (demande_version_key) DO NOTHING;


-- =====================================================================
-- 16. CALENDAR POPULATION
--
-- Fixed analytical calendar:
-- 2020-01-01 -> 2035-12-31
--
-- Current observed business/data range:
-- 2024 -> 2027
--
-- The wider range avoids annual schema/data maintenance while adding
-- only ~5,800 dimension rows.
-- =====================================================================

INSERT INTO warehouse.dim_date (
    date_key,
    date_complete,
    jour,
    jour_semaine,
    nom_jour,
    semaine_annee,
    mois,
    nom_mois,
    trimestre,
    annee,
    est_weekend
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::integer,

    d::date,

    EXTRACT(DAY FROM d)::smallint,

    EXTRACT(ISODOW FROM d)::smallint,

    CASE EXTRACT(ISODOW FROM d)::integer
        WHEN 1 THEN 'LUNDI'
        WHEN 2 THEN 'MARDI'
        WHEN 3 THEN 'MERCREDI'
        WHEN 4 THEN 'JEUDI'
        WHEN 5 THEN 'VENDREDI'
        WHEN 6 THEN 'SAMEDI'
        WHEN 7 THEN 'DIMANCHE'
    END,

    EXTRACT(WEEK FROM d)::smallint,

    EXTRACT(MONTH FROM d)::smallint,

    CASE EXTRACT(MONTH FROM d)::integer
        WHEN 1 THEN 'JANVIER'
        WHEN 2 THEN 'FEVRIER'
        WHEN 3 THEN 'MARS'
        WHEN 4 THEN 'AVRIL'
        WHEN 5 THEN 'MAI'
        WHEN 6 THEN 'JUIN'
        WHEN 7 THEN 'JUILLET'
        WHEN 8 THEN 'AOUT'
        WHEN 9 THEN 'SEPTEMBRE'
        WHEN 10 THEN 'OCTOBRE'
        WHEN 11 THEN 'NOVEMBRE'
        WHEN 12 THEN 'DECEMBRE'
    END,

    EXTRACT(QUARTER FROM d)::smallint,

    EXTRACT(YEAR FROM d)::smallint,

    EXTRACT(ISODOW FROM d)::integer IN (6,7)

FROM generate_series(
    DATE '2020-01-01',
    DATE '2035-12-31',
    INTERVAL '1 day'
) AS gs(d)

ON CONFLICT (date_key) DO NOTHING;


-- =====================================================================
-- 17. MIGRATION COMPLETE
-- =====================================================================

COMMIT;