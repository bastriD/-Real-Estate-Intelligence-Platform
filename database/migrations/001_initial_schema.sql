-- =============================================================================
-- 001_initial_schema.sql
-- Real Estate Intelligence Platform
-- PostgreSQL OLTP target schema V2
--
-- Purpose:
--   Create the clean real_estate transactional schema.
--
-- Important:
--   - Does NOT modify the legacy "Fil_Rouge_Depart" schema.
--   - Does NOT migrate legacy rows.
--   - Legacy migration will be handled separately after schema validation.
-- =============================================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS real_estate;

-- =============================================================================
-- CLIENT
-- =============================================================================

CREATE TABLE real_estate.client (
    id_client BIGINT GENERATED ALWAYS AS IDENTITY,

    nom VARCHAR(120) NOT NULL,
    prenom VARCHAR(120),

    email VARCHAR(255) NOT NULL,
    telephone VARCHAR(40),

    ville VARCHAR(120),

    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',

    consentement_contact BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_client
        PRIMARY KEY (id_client),

    CONSTRAINT uq_client_email
        UNIQUE (email),

    CONSTRAINT ck_client_statut
        CHECK (
            statut IN (
                'ACTIF',
                'INACTIF',
                'ARCHIVE'
            )
        )
);

-- =============================================================================
-- CHASSEUR
-- =============================================================================

CREATE TABLE real_estate.chasseur (
    id_chasseur BIGINT GENERATED ALWAYS AS IDENTITY,

    nom VARCHAR(120) NOT NULL,
    prenom VARCHAR(120),

    email VARCHAR(255) NOT NULL,
    telephone VARCHAR(40),

    date_entree DATE,

    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',

    CONSTRAINT pk_chasseur
        PRIMARY KEY (id_chasseur),

    CONSTRAINT uq_chasseur_email
        UNIQUE (email),

    CONSTRAINT ck_chasseur_statut
        CHECK (
            statut IN (
                'ACTIF',
                'INACTIF'
            )
        )
);

-- =============================================================================
-- SECTEUR
-- =============================================================================

CREATE TABLE real_estate.secteur (
    id_secteur BIGINT GENERATED ALWAYS AS IDENTITY,

    pays VARCHAR(100) NOT NULL DEFAULT 'France',

    ville VARCHAR(120) NOT NULL,
    quartier VARCHAR(150),
    code_postal VARCHAR(20),

    actif BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT pk_secteur
        PRIMARY KEY (id_secteur),

    CONSTRAINT uq_secteur_localisation
        UNIQUE (
            pays,
            ville,
            quartier,
            code_postal
        )
);

-- =============================================================================
-- SOURCE
-- =============================================================================

CREATE TABLE real_estate.source (
    id_source BIGINT GENERATED ALWAYS AS IDENTITY,

    nom VARCHAR(150) NOT NULL,
    type_source VARCHAR(40) NOT NULL,

    url_base TEXT,

    actif BOOLEAN NOT NULL DEFAULT TRUE,

    niveau_confiance VARCHAR(20),

    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_source
        PRIMARY KEY (id_source),

    CONSTRAINT ck_source_type
        CHECK (
            type_source IN (
                'AGENCE',
                'PARTICULIER',
                'PLATEFORME',
                'API',
                'OPEN_DATA',
                'MANUEL',
                'AUTRE'
            )
        ),

    CONSTRAINT ck_source_confiance
        CHECK (
            niveau_confiance IS NULL
            OR niveau_confiance IN (
                'FAIBLE',
                'MOYEN',
                'ELEVE'
            )
        )
);

-- =============================================================================
-- MANDAT
-- =============================================================================

CREATE TABLE real_estate.mandat (
    id_mandat BIGINT GENERATED ALWAYS AS IDENTITY,

    reference_mandat VARCHAR(80) NOT NULL,

    type_mandat VARCHAR(20) NOT NULL,

    date_signature DATE NOT NULL,

    mode_signature VARCHAR(30) NOT NULL,

    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,

    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',

    commentaire TEXT,

    id_client BIGINT NOT NULL,
    id_chasseur BIGINT NOT NULL,

    CONSTRAINT pk_mandat
        PRIMARY KEY (id_mandat),

    CONSTRAINT uq_mandat_reference
        UNIQUE (reference_mandat),

    CONSTRAINT fk_mandat_client
        FOREIGN KEY (id_client)
        REFERENCES real_estate.client(id_client)
        ON DELETE RESTRICT,

    CONSTRAINT fk_mandat_chasseur
        FOREIGN KEY (id_chasseur)
        REFERENCES real_estate.chasseur(id_chasseur)
        ON DELETE RESTRICT,

    CONSTRAINT ck_mandat_type
        CHECK (
            type_mandat IN (
                'EXCLUSIF',
                'NON_EXCLUSIF'
            )
        ),

    CONSTRAINT ck_mandat_mode_signature
        CHECK (
            mode_signature IN (
                'PAPIER',
                'ELECTRONIQUE',
                'AUTRE',
                'INCONNU'
            )
        ),

    CONSTRAINT ck_mandat_statut
        CHECK (
            statut IN (
                'BROUILLON',
                'ACTIF',
                'SUSPENDU',
                'TERMINE',
                'EXPIRE',
                'ANNULE'
            )
        ),

    CONSTRAINT ck_mandat_dates
        CHECK (
            date_fin >= date_debut
        )
);

-- NOTE:
-- The exact business rule:
--
--     date_fin = date_signature + INTERVAL '6 months'
--
-- is intentionally NOT enforced in this initial migration.
-- Renewal semantics must be validated before introducing that constraint.

-- =============================================================================
-- MANDAT_SECTEUR
-- =============================================================================

CREATE TABLE real_estate.mandat_secteur (
    id_mandat BIGINT NOT NULL,
    id_secteur BIGINT NOT NULL,

    CONSTRAINT pk_mandat_secteur
        PRIMARY KEY (
            id_mandat,
            id_secteur
        ),

    CONSTRAINT fk_mandat_secteur_mandat
        FOREIGN KEY (id_mandat)
        REFERENCES real_estate.mandat(id_mandat)
        ON DELETE CASCADE,

    CONSTRAINT fk_mandat_secteur_secteur
        FOREIGN KEY (id_secteur)
        REFERENCES real_estate.secteur(id_secteur)
        ON DELETE RESTRICT
);

-- =============================================================================
-- DEMANDE
-- =============================================================================

CREATE TABLE real_estate.demande (
    id_demande BIGINT GENERATED ALWAYS AS IDENTITY,

    reference_demande VARCHAR(80),

    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    id_mandat BIGINT NOT NULL,

    CONSTRAINT pk_demande
        PRIMARY KEY (id_demande),

    CONSTRAINT uq_demande_reference
        UNIQUE (reference_demande),

    CONSTRAINT fk_demande_mandat
        FOREIGN KEY (id_mandat)
        REFERENCES real_estate.mandat(id_mandat)
        ON DELETE RESTRICT,

    CONSTRAINT ck_demande_statut
        CHECK (
            statut IN (
                'ACTIVE',
                'SUSPENDUE',
                'CLOTUREE',
                'ANNULEE'
            )
        )
);

-- =============================================================================
-- DEMANDE_VERSION
-- =============================================================================

CREATE TABLE real_estate.demande_version (
    id_demande_version BIGINT GENERATED ALWAYS AS IDENTITY,

    numero_version INTEGER NOT NULL,

    date_version TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    motif_modification TEXT NOT NULL,

    ville VARCHAR(120),
    code_postal VARCHAR(20),
    type_bien VARCHAR(50),

    budget_min NUMERIC(12,2),
    budget_max NUMERIC(12,2),

    surface_min NUMERIC(10,2),

    nb_pieces_min INTEGER,
    nb_chambres_min INTEGER,

    dpe_max CHAR(1),

    criteres_souhaites JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- Original legacy search text is deliberately retained during migration.
    -- Structured criteria must never be invented when they cannot be inferred
    -- reliably from the historical description.
    description_recherche_legacy TEXT,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    id_demande BIGINT NOT NULL,

    auteur_client_id BIGINT,
    auteur_chasseur_id BIGINT,
    auteur_systeme BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_demande_version
        PRIMARY KEY (id_demande_version),

    CONSTRAINT fk_demande_version_demande
        FOREIGN KEY (id_demande)
        REFERENCES real_estate.demande(id_demande)
        ON DELETE RESTRICT,

    CONSTRAINT fk_demande_version_client
        FOREIGN KEY (auteur_client_id)
        REFERENCES real_estate.client(id_client)
        ON DELETE RESTRICT,

    CONSTRAINT fk_demande_version_chasseur
        FOREIGN KEY (auteur_chasseur_id)
        REFERENCES real_estate.chasseur(id_chasseur)
        ON DELETE RESTRICT,

    CONSTRAINT uq_demande_version_numero
        UNIQUE (
            id_demande,
            numero_version
        ),

    CONSTRAINT ck_demande_version_numero
        CHECK (
            numero_version > 0
        ),

    CONSTRAINT ck_demande_version_auteur
        CHECK (
            (
                CASE
                    WHEN auteur_client_id IS NOT NULL THEN 1
                    ELSE 0
                END
            )
            +
            (
                CASE
                    WHEN auteur_chasseur_id IS NOT NULL THEN 1
                    ELSE 0
                END
            )
            +
            (
                CASE
                    WHEN auteur_systeme THEN 1
                    ELSE 0
                END
            )
            = 1
        ),

    CONSTRAINT ck_demande_version_budget_min
        CHECK (
            budget_min IS NULL
            OR budget_min >= 0
        ),

    CONSTRAINT ck_demande_version_budget_max
        CHECK (
            budget_max IS NULL
            OR budget_max >= 0
        ),

    CONSTRAINT ck_demande_version_budget_range
        CHECK (
            budget_min IS NULL
            OR budget_max IS NULL
            OR budget_min <= budget_max
        ),

    CONSTRAINT ck_demande_version_surface
        CHECK (
            surface_min IS NULL
            OR surface_min >= 0
        ),

    CONSTRAINT ck_demande_version_pieces
        CHECK (
            nb_pieces_min IS NULL
            OR nb_pieces_min >= 0
        ),

    CONSTRAINT ck_demande_version_chambres
        CHECK (
            nb_chambres_min IS NULL
            OR nb_chambres_min >= 0
        ),

    CONSTRAINT ck_demande_version_dpe
        CHECK (
            dpe_max IS NULL
            OR dpe_max IN (
                'A',
                'B',
                'C',
                'D',
                'E',
                'F',
                'G'
            )
        )
);

-- Maximum one active version per demand.
CREATE UNIQUE INDEX uq_demande_version_active
    ON real_estate.demande_version(id_demande)
    WHERE active = TRUE;

-- =============================================================================
-- BIEN
-- =============================================================================

CREATE TABLE real_estate.bien (
    id_bien BIGINT GENERATED ALWAYS AS IDENTITY,

    reference_externe VARCHAR(150) NOT NULL,

    type_bien VARCHAR(50) NOT NULL,
    titre VARCHAR(255),

    adresse TEXT,
    code_postal VARCHAR(20),
    ville VARCHAR(120),

    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),

    prix NUMERIC(12,2),
    surface NUMERIC(10,2),

    nb_pieces INTEGER,
    nb_chambres INTEGER,

    dpe CHAR(1),

    description TEXT,

    date_publication TIMESTAMPTZ,
    date_collecte TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',

    id_source BIGINT NOT NULL,

    CONSTRAINT pk_bien
        PRIMARY KEY (id_bien),

    CONSTRAINT fk_bien_source
        FOREIGN KEY (id_source)
        REFERENCES real_estate.source(id_source)
        ON DELETE RESTRICT,

    CONSTRAINT uq_bien_source_reference
        UNIQUE (
            id_source,
            reference_externe
        ),

    CONSTRAINT ck_bien_prix
        CHECK (
            prix IS NULL
            OR prix >= 0
        ),

    CONSTRAINT ck_bien_surface
        CHECK (
            surface IS NULL
            OR surface >= 0
        ),

    CONSTRAINT ck_bien_pieces
        CHECK (
            nb_pieces IS NULL
            OR nb_pieces >= 0
        ),

    CONSTRAINT ck_bien_chambres
        CHECK (
            nb_chambres IS NULL
            OR nb_chambres >= 0
        ),

    CONSTRAINT ck_bien_latitude
        CHECK (
            latitude IS NULL
            OR latitude BETWEEN -90 AND 90
        ),

    CONSTRAINT ck_bien_longitude
        CHECK (
            longitude IS NULL
            OR longitude BETWEEN -180 AND 180
        ),

    CONSTRAINT ck_bien_dpe
        CHECK (
            dpe IS NULL
            OR dpe IN (
                'A',
                'B',
                'C',
                'D',
                'E',
                'F',
                'G'
            )
        ),

    CONSTRAINT ck_bien_statut
        CHECK (
            statut IN (
                'ACTIF',
                'EXPIRE',
                'VENDU',
                'INDISPONIBLE'
            )
        )
);

-- =============================================================================
-- PRESENTATION
-- =============================================================================

CREATE TABLE real_estate.presentation (
    id_presentation BIGINT GENERATED ALWAYS AS IDENTITY,

    date_selection TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    date_presentation TIMESTAMPTZ,

    score_matching NUMERIC(5,2),

    statut VARCHAR(20) NOT NULL DEFAULT 'IDENTIFIE',

    id_demande_version BIGINT NOT NULL,
    id_bien BIGINT NOT NULL,

    CONSTRAINT pk_presentation
        PRIMARY KEY (id_presentation),

    CONSTRAINT fk_presentation_demande_version
        FOREIGN KEY (id_demande_version)
        REFERENCES real_estate.demande_version(id_demande_version)
        ON DELETE RESTRICT,

    CONSTRAINT fk_presentation_bien
        FOREIGN KEY (id_bien)
        REFERENCES real_estate.bien(id_bien)
        ON DELETE RESTRICT,

    CONSTRAINT uq_presentation_demande_bien
        UNIQUE (
            id_demande_version,
            id_bien
        ),

    CONSTRAINT ck_presentation_score
        CHECK (
            score_matching IS NULL
            OR score_matching BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_presentation_statut
        CHECK (
            statut IN (
                'IDENTIFIE',
                'QUALIFIE',
                'PRESENTE',
                'REJETE',
                'VISITE',
                'RETENU'
            )
        )
);

-- =============================================================================
-- COMMENTAIRE
-- =============================================================================

CREATE TABLE real_estate.commentaire (
    id_commentaire BIGINT GENERATED ALWAYS AS IDENTITY,

    date_commentaire TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    contenu TEXT NOT NULL,

    priorite SMALLINT,

    decision VARCHAR(20),

    id_demande_version BIGINT NOT NULL,
    id_bien BIGINT NOT NULL,

    auteur_client_id BIGINT,
    auteur_chasseur_id BIGINT,

    CONSTRAINT pk_commentaire
        PRIMARY KEY (id_commentaire),

    CONSTRAINT fk_commentaire_demande_version
        FOREIGN KEY (id_demande_version)
        REFERENCES real_estate.demande_version(id_demande_version)
        ON DELETE RESTRICT,

    CONSTRAINT fk_commentaire_bien
        FOREIGN KEY (id_bien)
        REFERENCES real_estate.bien(id_bien)
        ON DELETE RESTRICT,

    CONSTRAINT fk_commentaire_client
        FOREIGN KEY (auteur_client_id)
        REFERENCES real_estate.client(id_client)
        ON DELETE RESTRICT,

    CONSTRAINT fk_commentaire_chasseur
        FOREIGN KEY (auteur_chasseur_id)
        REFERENCES real_estate.chasseur(id_chasseur)
        ON DELETE RESTRICT,

    CONSTRAINT ck_commentaire_auteur
        CHECK (
            (
                CASE
                    WHEN auteur_client_id IS NOT NULL THEN 1
                    ELSE 0
                END
            )
            +
            (
                CASE
                    WHEN auteur_chasseur_id IS NOT NULL THEN 1
                    ELSE 0
                END
            )
            = 1
        ),

    CONSTRAINT ck_commentaire_priorite
        CHECK (
            priorite IS NULL
            OR priorite BETWEEN 1 AND 5
        ),

    CONSTRAINT ck_commentaire_decision
        CHECK (
            decision IS NULL
            OR decision IN (
                'RETENIR',
                'ECARTER',
                'VISITER',
                'REQUALIFIER',
                'INFORMATION'
            )
        )
);

-- =============================================================================
-- DOCUMENT
-- =============================================================================

CREATE TABLE real_estate.document (
    id_document BIGINT GENERATED ALWAYS AS IDENTITY,

    nom_fichier VARCHAR(255) NOT NULL,

    type_document VARCHAR(60),
    mime_type VARCHAR(120),

    chemin_stockage TEXT NOT NULL,

    checksum VARCHAR(128),

    date_ajout TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    classification VARCHAR(20) NOT NULL DEFAULT 'INTERNE',

    indexable_ia BOOLEAN NOT NULL DEFAULT FALSE,

    id_bien BIGINT NOT NULL,

    CONSTRAINT pk_document
        PRIMARY KEY (id_document),

    CONSTRAINT fk_document_bien
        FOREIGN KEY (id_bien)
        REFERENCES real_estate.bien(id_bien)
        ON DELETE RESTRICT,

    CONSTRAINT ck_document_classification
        CHECK (
            classification IN (
                'PUBLIC',
                'INTERNE',
                'CONFIDENTIEL',
                'RESTREINT'
            )
        )
);

-- =============================================================================
-- BAREME_COMMISSION
-- =============================================================================

CREATE TABLE real_estate.bareme_commission (
    id_bareme BIGINT GENERATED ALWAYS AS IDENTITY,

    montant_min NUMERIC(12,2) NOT NULL,
    montant_max NUMERIC(12,2),

    taux_commission NUMERIC(7,4) NOT NULL,

    montant_fixe NUMERIC(12,2) NOT NULL DEFAULT 0,

    date_debut_validite DATE NOT NULL,
    date_fin_validite DATE,

    actif BOOLEAN NOT NULL DEFAULT TRUE,

    id_chasseur BIGINT NOT NULL,

    CONSTRAINT pk_bareme_commission
        PRIMARY KEY (id_bareme),

    CONSTRAINT fk_bareme_commission_chasseur
        FOREIGN KEY (id_chasseur)
        REFERENCES real_estate.chasseur(id_chasseur)
        ON DELETE RESTRICT,

    CONSTRAINT ck_bareme_montant_min
        CHECK (
            montant_min >= 0
        ),

    CONSTRAINT ck_bareme_montant_max
        CHECK (
            montant_max IS NULL
            OR montant_max >= montant_min
        ),

    CONSTRAINT ck_bareme_taux
        CHECK (
            taux_commission >= 0
            AND taux_commission <= 1
        ),

    CONSTRAINT ck_bareme_montant_fixe
        CHECK (
            montant_fixe >= 0
        ),

    CONSTRAINT ck_bareme_dates
        CHECK (
            date_fin_validite IS NULL
            OR date_fin_validite >= date_debut_validite
        )
);

-- =============================================================================
-- PAIEMENT
-- =============================================================================

CREATE TABLE real_estate.paiement (
    id_paiement BIGINT GENERATED ALWAYS AS IDENTITY,

    date_acte_authentique DATE,

    montant_achat NUMERIC(12,2),

    montant_honoraires NUMERIC(12,2),

    montant_chasseur NUMERIC(12,2),

    date_reception_honoraires DATE,
    date_paiement_chasseur DATE,

    statut VARCHAR(20) NOT NULL DEFAULT 'ATTENDU',

    id_mandat BIGINT NOT NULL,

    id_bareme BIGINT,

    CONSTRAINT pk_paiement
        PRIMARY KEY (id_paiement),

    CONSTRAINT fk_paiement_mandat
        FOREIGN KEY (id_mandat)
        REFERENCES real_estate.mandat(id_mandat)
        ON DELETE RESTRICT,

    CONSTRAINT fk_paiement_bareme
        FOREIGN KEY (id_bareme)
        REFERENCES real_estate.bareme_commission(id_bareme)
        ON DELETE RESTRICT,

    CONSTRAINT ck_paiement_montant_achat
        CHECK (
            montant_achat IS NULL
            OR montant_achat >= 0
        ),

    CONSTRAINT ck_paiement_honoraires
        CHECK (
            montant_honoraires IS NULL
            OR montant_honoraires >= 0
        ),

    CONSTRAINT ck_paiement_chasseur
        CHECK (
            montant_chasseur IS NULL
            OR montant_chasseur >= 0
        ),

    CONSTRAINT ck_paiement_statut
        CHECK (
            statut IN (
                'ATTENDU',
                'RECU',
                'VERIFIE',
                'PROGRAMME',
                'PAYE',
                'ANNULE'
            )
        ),

    CONSTRAINT ck_paiement_dates
        CHECK (
            date_paiement_chasseur IS NULL
            OR date_reception_honoraires IS NULL
            OR date_paiement_chasseur >= date_reception_honoraires
        )
);

-- =============================================================================
-- BASELINE FOREIGN-KEY INDEXES
-- =============================================================================

CREATE INDEX idx_mandat_id_client
    ON real_estate.mandat(id_client);

CREATE INDEX idx_mandat_id_chasseur
    ON real_estate.mandat(id_chasseur);

CREATE INDEX idx_mandat_secteur_id_secteur
    ON real_estate.mandat_secteur(id_secteur);

CREATE INDEX idx_demande_id_mandat
    ON real_estate.demande(id_mandat);

CREATE INDEX idx_demande_version_id_demande
    ON real_estate.demande_version(id_demande);

CREATE INDEX idx_demande_version_auteur_client
    ON real_estate.demande_version(auteur_client_id);

CREATE INDEX idx_demande_version_auteur_chasseur
    ON real_estate.demande_version(auteur_chasseur_id);

CREATE INDEX idx_bien_id_source
    ON real_estate.bien(id_source);

CREATE INDEX idx_presentation_id_demande_version
    ON real_estate.presentation(id_demande_version);

CREATE INDEX idx_presentation_id_bien
    ON real_estate.presentation(id_bien);

CREATE INDEX idx_commentaire_id_demande_version
    ON real_estate.commentaire(id_demande_version);

CREATE INDEX idx_commentaire_id_bien
    ON real_estate.commentaire(id_bien);

CREATE INDEX idx_commentaire_auteur_client
    ON real_estate.commentaire(auteur_client_id);

CREATE INDEX idx_commentaire_auteur_chasseur
    ON real_estate.commentaire(auteur_chasseur_id);

CREATE INDEX idx_document_id_bien
    ON real_estate.document(id_bien);

CREATE INDEX idx_bareme_id_chasseur
    ON real_estate.bareme_commission(id_chasseur);

CREATE INDEX idx_paiement_id_mandat
    ON real_estate.paiement(id_mandat);

CREATE INDEX idx_paiement_id_bareme
    ON real_estate.paiement(id_bareme);

-- =============================================================================
-- INITIAL SEARCH INDEXES
-- =============================================================================

CREATE INDEX idx_bien_ville
    ON real_estate.bien(ville);

CREATE INDEX idx_bien_type_bien
    ON real_estate.bien(type_bien);

CREATE INDEX idx_demande_version_ville
    ON real_estate.demande_version(ville);

CREATE INDEX idx_demande_version_type_bien
    ON real_estate.demande_version(type_bien);

-- JSONB GIN index intentionally deferred until workload measurements justify it.
-- Price/surface/composite indexes are also deferred until EXPLAIN ANALYZE testing.

COMMIT;
