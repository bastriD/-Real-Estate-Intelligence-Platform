-- =============================================================================
-- 004_staging_schema.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Create the normalized STAGING layer between RAW ingestion and the clean
--   OLTP target model.
--
-- Principles:
--   - RAW keeps source values as received.
--   - STAGING converts valid values to typed PostgreSQL columns.
--   - Parsing failures are preserved through quality flags / rejection reason.
--   - No source row is silently discarded.
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;

CREATE SCHEMA IF NOT EXISTS staging;


-- =============================================================================
-- STAGING RECHERCHES
-- =============================================================================

CREATE TABLE IF NOT EXISTS staging.recherches (
    staging_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    raw_id BIGINT NOT NULL,

    legacy_generated_id BIGINT,
    reference VARCHAR(80),

    date_creation DATE,

    ville VARCHAR(120),
    code_postal VARCHAR(20),
    type_bien VARCHAR(80),

    budget_max NUMERIC(12,2),
    surface_min NUMERIC(10,2),

    criteres_souhaites JSONB NOT NULL DEFAULT '[]'::jsonb,

    nb_pieces_min INTEGER,
    nb_chambres_min INTEGER,

    dpe_max CHAR(1),

    ingestion_batch TEXT NOT NULL,
    source_file TEXT NOT NULL,

    quality_valid BOOLEAN NOT NULL DEFAULT TRUE,
    quality_errors JSONB NOT NULL DEFAULT '[]'::jsonb,

    staged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_staging_recherche_raw_id
        UNIQUE (raw_id),

    CONSTRAINT ck_staging_recherche_budget
        CHECK (
            budget_max IS NULL
            OR budget_max >= 0
        ),

    CONSTRAINT ck_staging_recherche_surface
        CHECK (
            surface_min IS NULL
            OR surface_min >= 0
        ),

    CONSTRAINT ck_staging_recherche_pieces
        CHECK (
            nb_pieces_min IS NULL
            OR nb_pieces_min >= 0
        ),

    CONSTRAINT ck_staging_recherche_chambres
        CHECK (
            nb_chambres_min IS NULL
            OR nb_chambres_min >= 0
        ),

    CONSTRAINT ck_staging_recherche_dpe
        CHECK (
            dpe_max IS NULL
            OR dpe_max IN ('A', 'B', 'C', 'D', 'E', 'F', 'G')
        )
);


-- =============================================================================
-- STAGING ANNONCES
-- =============================================================================

CREATE TABLE IF NOT EXISTS staging.annonces (
    staging_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    raw_id BIGINT NOT NULL,

    source_uuid UUID,
    reference VARCHAR(150),
    recherche_ref VARCHAR(80),

    type_bien VARCHAR(80),
    titre VARCHAR(255),

    ville VARCHAR(120),
    code_postal VARCHAR(20),

    date_publication TIMESTAMPTZ,

    prix NUMERIC(12,2),

    surface NUMERIC(10,2),

    nb_pieces INTEGER,
    nb_chambres INTEGER,

    meuble BOOLEAN,

    dpe CHAR(1),

    description TEXT,

    terrasse BOOLEAN,
    calme BOOLEAN,
    vue BOOLEAN,
    jardin BOOLEAN,

    contact_nom VARCHAR(255),
    contact_telephone VARCHAR(80),
    contact_email VARCHAR(255),
    contact_agence VARCHAR(255),

    photos JSONB NOT NULL DEFAULT '[]'::jsonb,

    exclusivite BOOLEAN,
    particulier BOOLEAN,

    annee_construction INTEGER,

    adresse TEXT,

    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),

    etage TEXT,

    charges_mensuelles NUMERIC(10,2),

    ingestion_batch TEXT NOT NULL,
    source_file TEXT NOT NULL,

    quality_valid BOOLEAN NOT NULL DEFAULT TRUE,
    quality_errors JSONB NOT NULL DEFAULT '[]'::jsonb,

    staged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_staging_annonce_raw_id
        UNIQUE (raw_id),

    CONSTRAINT ck_staging_annonce_prix
        CHECK (
            prix IS NULL
            OR prix >= 0
        ),

    CONSTRAINT ck_staging_annonce_surface
        CHECK (
            surface IS NULL
            OR surface >= 0
        ),

    CONSTRAINT ck_staging_annonce_pieces
        CHECK (
            nb_pieces IS NULL
            OR nb_pieces >= 0
        ),

    CONSTRAINT ck_staging_annonce_chambres
        CHECK (
            nb_chambres IS NULL
            OR nb_chambres >= 0
        ),

    CONSTRAINT ck_staging_annonce_dpe
        CHECK (
            dpe IS NULL
            OR dpe IN ('A', 'B', 'C', 'D', 'E', 'F', 'G')
        ),

    CONSTRAINT ck_staging_annonce_latitude
        CHECK (
            latitude IS NULL
            OR latitude BETWEEN -90 AND 90
        ),

    CONSTRAINT ck_staging_annonce_longitude
        CHECK (
            longitude IS NULL
            OR longitude BETWEEN -180 AND 180
        ),

    CONSTRAINT ck_staging_annonce_annee
        CHECK (
            annee_construction IS NULL
            OR annee_construction BETWEEN 1800 AND 2100
        ),

    CONSTRAINT ck_staging_annonce_charges
        CHECK (
            charges_mensuelles IS NULL
            OR charges_mensuelles >= 0
        )
);


-- =============================================================================
-- REJECTION / QUALITY VIEW
-- =============================================================================

CREATE OR REPLACE VIEW staging.v_annonces_invalides AS
SELECT
    staging_id,
    raw_id,
    reference,
    recherche_ref,
    quality_errors,
    ingestion_batch,
    source_file,
    staged_at
FROM staging.annonces
WHERE quality_valid = FALSE;


CREATE OR REPLACE VIEW staging.v_recherches_invalides AS
SELECT
    staging_id,
    raw_id,
    reference,
    quality_errors,
    ingestion_batch,
    source_file,
    staged_at
FROM staging.recherches
WHERE quality_valid = FALSE;


-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_staging_recherches_reference
    ON staging.recherches(reference);

CREATE INDEX IF NOT EXISTS idx_staging_recherches_batch
    ON staging.recherches(ingestion_batch);

CREATE INDEX IF NOT EXISTS idx_staging_annonces_reference
    ON staging.annonces(reference);

CREATE INDEX IF NOT EXISTS idx_staging_annonces_recherche_ref
    ON staging.annonces(recherche_ref);

CREATE INDEX IF NOT EXISTS idx_staging_annonces_batch
    ON staging.annonces(ingestion_batch);

CREATE INDEX IF NOT EXISTS idx_staging_annonces_quality
    ON staging.annonces(quality_valid);


COMMIT;