-- =============================================================================
-- 001_operational_queries.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Provide representative OLTP operational queries for BC05 C2.
--
-- Scope:
--   - active mandates by hunter
--   - current active demand version
--   - mandate-sector lookup
--   - candidate properties for a demand
--   - presentation history
--   - comments / feedback
--   - commission and payment follow-up
--
-- Notes:
--   These queries are intentionally operational.
--   They are not OLAP/reporting queries.
-- =============================================================================

\set ON_ERROR_STOP on


-- =============================================================================
-- QUERY 1
-- Active mandates by chasseur
-- =============================================================================

SELECT
    h.id_chasseur,
    h.nom,
    h.prenom,
    m.id_mandat,
    m.reference_mandat,
    m.type_mandat,
    m.date_debut,
    m.date_fin,
    m.statut,
    c.id_client,
    c.nom AS client_nom,
    c.prenom AS client_prenom
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
-- QUERY 2
-- Current active demand version for every active demand
-- =============================================================================

SELECT
    d.id_demande,
    d.reference_demande,
    d.statut AS demande_statut,

    dv.id_demande_version,
    dv.numero_version,
    dv.date_version,

    dv.ville,
    dv.code_postal,
    dv.type_bien,
    dv.budget_min,
    dv.budget_max,
    dv.surface_min,
    dv.nb_pieces_min,
    dv.nb_chambres_min,
    dv.dpe_max,
    dv.criteres_souhaites

FROM real_estate.demande d

JOIN real_estate.demande_version dv
  ON dv.id_demande = d.id_demande
 AND dv.active = TRUE

WHERE d.statut = 'ACTIVE'

ORDER BY d.id_demande;


-- =============================================================================
-- QUERY 3
-- Mandate with all targeted sectors
-- =============================================================================

SELECT
    m.id_mandat,
    m.reference_mandat,
    m.statut,

    s.id_secteur,
    s.pays,
    s.ville,
    s.quartier,
    s.code_postal

FROM real_estate.mandat m

JOIN real_estate.mandat_secteur ms
  ON ms.id_mandat = m.id_mandat

JOIN real_estate.secteur s
  ON s.id_secteur = ms.id_secteur

WHERE m.id_mandat = 1

ORDER BY
    s.pays,
    s.ville,
    s.quartier;


-- =============================================================================
-- QUERY 4
-- Search candidates for one active demand version
--
-- Deterministic first-pass filter:
--   - city
--   - property type
--   - maximum budget
--   - minimum surface
--   - minimum number of rooms
--   - minimum number of bedrooms
--   - DPE threshold
--
-- NULL criteria mean:
--   no restriction for that criterion.
-- =============================================================================

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
    b.titre,
    b.ville,
    b.code_postal,
    b.prix,
    b.surface,
    b.nb_pieces,
    b.nb_chambres,
    b.dpe,
    b.statut,

    cr.id_demande_version

FROM current_request cr

JOIN real_estate.bien b
  ON b.statut = 'ACTIF'

 AND (
        cr.ville IS NULL
        OR b.ville = cr.ville
     )

 AND (
        cr.code_postal IS NULL
        OR b.code_postal = cr.code_postal
     )

 AND (
        cr.type_bien IS NULL
        OR b.type_bien = cr.type_bien
     )

 AND (
        cr.budget_max IS NULL
        OR b.prix IS NULL
        OR b.prix <= cr.budget_max
     )

 AND (
        cr.surface_min IS NULL
        OR b.surface IS NULL
        OR b.surface >= cr.surface_min
     )

 AND (
        cr.nb_pieces_min IS NULL
        OR b.nb_pieces IS NULL
        OR b.nb_pieces >= cr.nb_pieces_min
     )

 AND (
        cr.nb_chambres_min IS NULL
        OR b.nb_chambres IS NULL
        OR b.nb_chambres >= cr.nb_chambres_min
     )

 AND (
        cr.dpe_max IS NULL
        OR b.dpe IS NULL
        OR b.dpe <= cr.dpe_max
     )

ORDER BY
    b.prix NULLS LAST,
    b.surface DESC NULLS LAST;


-- =============================================================================
-- QUERY 5
-- Presentations for one demand version
-- =============================================================================

SELECT
    p.id_presentation,
    p.date_selection,
    p.date_presentation,
    p.score_matching,
    p.statut,

    b.id_bien,
    b.reference_externe,
    b.titre,
    b.ville,
    b.prix,
    b.surface,
    b.dpe

FROM real_estate.presentation p

JOIN real_estate.bien b
  ON b.id_bien = p.id_bien

WHERE p.id_demande_version = 1

ORDER BY
    p.score_matching DESC NULLS LAST,
    p.date_selection DESC;


-- =============================================================================
-- QUERY 6
-- Comments / feedback for one demand version and property
-- =============================================================================

SELECT
    c.id_commentaire,
    c.date_commentaire,
    c.contenu,
    c.priorite,
    c.decision,

    CASE
        WHEN c.auteur_client_id IS NOT NULL
            THEN 'CLIENT'
        WHEN c.auteur_chasseur_id IS NOT NULL
            THEN 'CHASSEUR'
        ELSE 'UNKNOWN'
    END AS auteur_type,

    COALESCE(
        client.nom || ' ' || COALESCE(client.prenom, ''),
        chasseur.nom || ' ' || COALESCE(chasseur.prenom, '')
    ) AS auteur

FROM real_estate.commentaire c

LEFT JOIN real_estate.client client
  ON client.id_client = c.auteur_client_id

LEFT JOIN real_estate.chasseur chasseur
  ON chasseur.id_chasseur = c.auteur_chasseur_id

WHERE c.id_demande_version = 1
  AND c.id_bien = 1

ORDER BY c.date_commentaire;


-- =============================================================================
-- QUERY 7
-- Active commission scales by chasseur
-- =============================================================================

SELECT
    h.id_chasseur,
    h.nom,
    h.prenom,

    bc.id_bareme,
    bc.montant_min,
    bc.montant_max,
    bc.taux_commission,
    bc.montant_fixe,
    bc.date_debut_validite,
    bc.date_fin_validite,
    bc.actif

FROM real_estate.chasseur h

JOIN real_estate.bareme_commission bc
  ON bc.id_chasseur = h.id_chasseur

WHERE bc.actif = TRUE
  AND bc.date_debut_validite <= CURRENT_DATE
  AND (
        bc.date_fin_validite IS NULL
        OR bc.date_fin_validite >= CURRENT_DATE
      )

ORDER BY
    h.id_chasseur,
    bc.montant_min;


-- =============================================================================
-- QUERY 8
-- Payment follow-up
-- =============================================================================

SELECT
    p.id_paiement,
    p.statut,

    p.date_acte_authentique,
    p.montant_achat,
    p.montant_honoraires,
    p.montant_chasseur,

    p.date_reception_honoraires,
    p.date_paiement_chasseur,

    m.reference_mandat,

    c.nom AS client_nom,
    c.prenom AS client_prenom,

    h.nom AS chasseur_nom,
    h.prenom AS chasseur_prenom,

    bc.taux_commission,
    bc.montant_fixe

FROM real_estate.paiement p

JOIN real_estate.mandat m
  ON m.id_mandat = p.id_mandat

JOIN real_estate.client c
  ON c.id_client = m.id_client

JOIN real_estate.chasseur h
  ON h.id_chasseur = m.id_chasseur

LEFT JOIN real_estate.bareme_commission bc
  ON bc.id_bareme = p.id_bareme

WHERE p.statut <> 'PAYE'

ORDER BY
    p.date_acte_authentique NULLS LAST,
    p.id_paiement;


-- =============================================================================
-- QUERY 9
-- Full operational view of a demand
-- =============================================================================

SELECT
    d.id_demande,
    d.reference_demande,
    d.statut AS demande_statut,

    m.id_mandat,
    m.reference_mandat,
    m.type_mandat,
    m.statut AS mandat_statut,
    m.date_debut,
    m.date_fin,

    client.id_client,
    client.nom AS client_nom,
    client.prenom AS client_prenom,

    hunter.id_chasseur,
    hunter.nom AS chasseur_nom,
    hunter.prenom AS chasseur_prenom,

    dv.id_demande_version,
    dv.numero_version,
    dv.date_version,
    dv.ville,
    dv.code_postal,
    dv.type_bien,
    dv.budget_min,
    dv.budget_max,
    dv.surface_min,
    dv.nb_pieces_min,
    dv.nb_chambres_min,
    dv.dpe_max

FROM real_estate.demande d

JOIN real_estate.mandat m
  ON m.id_mandat = d.id_mandat

JOIN real_estate.client client
  ON client.id_client = m.id_client

JOIN real_estate.chasseur hunter
  ON hunter.id_chasseur = m.id_chasseur

JOIN real_estate.demande_version dv
  ON dv.id_demande = d.id_demande
 AND dv.active = TRUE

WHERE d.id_demande = 1;


-- =============================================================================
-- QUERY 10
-- Current workload by chasseur
--
-- Operational workload, not analytical performance reporting.
-- =============================================================================

SELECT
    h.id_chasseur,
    h.nom,
    h.prenom,

    COUNT(m.id_mandat)
        FILTER (
            WHERE m.statut = 'ACTIF'
        ) AS mandats_actifs,

    COUNT(d.id_demande)
        FILTER (
            WHERE d.statut = 'ACTIVE'
        ) AS demandes_actives

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
-- END
-- =============================================================================