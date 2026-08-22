-- =============================================================================
-- 003_raw_ingestion_schema.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Create RAW ingestion tables for generated search criteria and property
--   announcements.
--
-- RAW principles:
--   - preserve source values as received
--   - tolerate heterogeneous formats
--   - avoid premature coercion
--   - retain ingestion metadata
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;

CREATE SCHEMA IF NOT EXISTS raw;


-- =============================================================================
-- RAW RECHERCHES
-- =============================================================================

CREATE TABLE IF NOT EXISTS raw.recherches (
    raw_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id TEXT,
    reference TEXT,
    date_creation TEXT,
    ville TEXT,
    code_postal TEXT,
    type_bien TEXT,
    budget_max TEXT,
    surface_min TEXT,
    criteres_souhaites TEXT,
    nb_pieces_min TEXT,
    nb_chambres_min TEXT,
    dpe_max TEXT,

    source_file TEXT NOT NULL,
    ingestion_batch TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- =============================================================================
-- RAW ANNONCES
-- =============================================================================

CREATE TABLE IF NOT EXISTS raw.annonces (
    raw_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id TEXT,
    reference TEXT,
    recherche_ref TEXT,
    type_bien TEXT,
    titre TEXT,
    ville TEXT,
    code_postal TEXT,
    date_publication TEXT,
    prix TEXT,
    surface TEXT,
    nb_pieces TEXT,
    nb_chambres TEXT,
    meuble TEXT,
    dpe TEXT,
    description TEXT,
    terrasse TEXT,
    calme TEXT,

    contact_nom TEXT,
    contact_telephone TEXT,
    contact_email TEXT,
    contact_agence TEXT,

    photos TEXT,

    exclusivite TEXT,
    particulier TEXT,

    surface_m2 TEXT,
    annee_construction TEXT,
    adresse TEXT,
    latitude TEXT,
    longitude TEXT,
    etage TEXT,
    charges_mensuelles TEXT,

    vue TEXT,
    jardin TEXT,

    source_file TEXT NOT NULL,
    ingestion_batch TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- =============================================================================
-- BASELINE INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_raw_recherches_reference
    ON raw.recherches(reference);

CREATE INDEX IF NOT EXISTS idx_raw_annonces_reference
    ON raw.annonces(reference);

CREATE INDEX IF NOT EXISTS idx_raw_annonces_recherche_ref
    ON raw.annonces(recherche_ref);


COMMIT;