-- =============================================================================
-- 002_explain_analyze.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Measure representative OLTP query plans before adding new indexes.
--
-- BC05 C2:
--   Optimization decisions must be based on observed PostgreSQL execution
--   plans, not speculative indexing.
--
-- This script is READ-ONLY.
-- =============================================================================

\set ON_ERROR_STOP on

-- Refresh planner statistics before measurement.
ANALYZE real_estate.client;
ANALYZE real_estate.chasseur;
ANALYZE real_estate.secteur;
ANALYZE real_estate.mandat;
ANALYZE real_estate.mandat_secteur;
ANALYZE real_estate.demande;
ANALYZE real_estate.demande_version;
ANALYZE real_estate.source;
ANALYZE real_estate.bien;
ANALYZE real_estate.presentation;
ANALYZE real_estate.commentaire;
ANALYZE real_estate.document;
ANALYZE real_estate.bareme_commission;
ANALYZE real_estate.paiement;


-- =============================================================================
-- PLAN 1
-- Active mandates by chasseur
-- =============================================================================

EXPLAIN (
    ANALYZE,
    BUFFERS,
    VERBOSE,
    FORMAT TEXT
)
SELECT
    h.id_chasseur,
    h.nom,
    h.prenom,
    m.id_mandat,
    m.reference_mandat,
    m.date_debut,
    m.date_fin,
    c.id_client,
    c.nom,
    c.prenom
FROM real_estate.chasseur h
JOIN real_estate.mandat m
  ON m.id_chasseur = h.id_chasseur
JOIN real_estate.client c
  ON c.id_client = m.id_client
WHERE m.statut = 'ACTIF'
ORDER BY
    h.nom,
    h.prenom,
    m.date_debut;


-- =============================================================================
-- PLAN 2
-- Current active demand versions
-- =============================================================================

EXPLAIN (
    ANALYZE,
    BUFFERS,
    VERBOSE,
    FORMAT TEXT
)
SELECT
    d.id_demande,
    d.reference_demande,
    dv.id_demande_version,
    dv.numero_version,
    dv.ville,
    dv.code_postal,
    dv.type_bien,
    dv.budget_max,
    dv.surface_min,
    dv.nb_pieces_min,
    dv.nb_chambres_min,
    dv.dpe_max
FROM real_estate.demande d
JOIN real_estate.demande_version dv
  ON dv.id_demande = d.id_demande
 AND dv.active = TRUE
WHERE d.statut = 'ACTIVE'
ORDER BY d.id_demande;


-- =============================================================================
-- PLAN 3
-- Mandate sectors
-- =============================================================================

EXPLAIN (
    ANALYZE,
    BUFFERS,
    VERBOSE,
    FORMAT TEXT
)
SELECT
    m.reference_mandat,
    s.pays,
    s.ville,
    s.quartier,
    s.code_postal
FROM real_estate.mandat m
JOIN real_estate.mandat_secteur ms
  ON ms.id_mandat = m.id_mandat
JOIN real_estate.secteur s
  ON s.id_secteur = ms.id_secteur
WHERE m.id_mandat = 1;


-- =============================================================================
-- PLAN 4
-- Candidate-property deterministic filtering
--
-- There are currently no migrated BIEN rows, so this plan establishes the
-- baseline structure. Later seed/generated data will make this measurement
-- materially useful for index tuning.
-- =============================================================================

EXPLAIN (
    ANALYZE,
    BUFFERS,
    VERBOSE,
    FORMAT TEXT
)
WITH current_request AS (
    SELECT
        dv.id_demande_version,
        dv.ville,
        dv.code_postal,
        dv.type_bien,
        dv.budget_max,
        dv.surface_min,
        dv.nb_pieces_min,
        dv.nb_chambres_min,
        dv.dpe_max
    FROM real_estate.demande_version dv
    WHERE dv.id_demande_version = 1
      AND dv.active = TRUE
)
SELECT
    b.id_bien,
    b.reference_externe,
    b.type_bien,
    b.ville,
    b.code_postal,
    b.prix,
    b.surface,
    b.nb_pieces,
    b.nb_chambres,
    b.dpe
FROM current_request cr
JOIN real_estate.bien b
  ON b.statut = 'ACTIF'
 AND (cr.ville IS NULL OR b.ville = cr.ville)
 AND (cr.code_postal IS NULL OR b.code_postal = cr.code_postal)
 AND (cr.type_bien IS NULL OR b.type_bien = cr.type_bien)
 AND (cr.budget_max IS NULL OR b.prix IS NULL OR b.prix <= cr.budget_max)
 AND (cr.surface_min IS NULL OR b.surface IS NULL OR b.surface >= cr.surface_min)
 AND (cr.nb_pieces_min IS NULL OR b.nb_pieces IS NULL OR b.nb_pieces >= cr.nb_pieces_min)
 AND (cr.nb_chambres_min IS NULL OR b.nb_chambres IS NULL OR b.nb_chambres >= cr.nb_chambres_min)
 AND (cr.dpe_max IS NULL OR b.dpe IS NULL OR b.dpe <= cr.dpe_max);


-- =============================================================================
-- PLAN 5
-- Current hunter workload
-- =============================================================================

EXPLAIN (
    ANALYZE,
    BUFFERS,
    VERBOSE,
    FORMAT TEXT
)
SELECT
    h.id_chasseur,
    h.nom,
    h.prenom,

    COUNT(m.id_mandat)
        FILTER (WHERE m.statut = 'ACTIF') AS mandats_actifs,

    COUNT(d.id_demande)
        FILTER (WHERE d.statut = 'ACTIVE') AS demandes_actives

FROM real_estate.chasseur h

LEFT JOIN real_estate.mandat m
  ON m.id_chasseur = h.id_chasseur

LEFT JOIN real_estate.demande d
  ON d.id_mandat = m.id_mandat

GROUP BY
    h.id_chasseur,
    h.nom,
    h.prenom

ORDER BY
    demandes_actives DESC,
    mandats_actifs DESC,
    h.nom;


-- =============================================================================
-- INDEX INVENTORY
-- =============================================================================

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'real_estate'
ORDER BY
    tablename,
    indexname;


-- =============================================================================
-- TABLE STATISTICS
-- =============================================================================

SELECT
    relname AS table_name,
    n_live_tup AS estimated_live_rows,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables
WHERE schemaname = 'real_estate'
ORDER BY relname;