-- =============================================================================
-- 007_demande_chasseur_affectation.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Persist the hunter assignment / acceptance lifecycle for a demande.
--
-- Business lifecycle:
--   1. A prospect submits a demande.
--   2. The demande exists before any mandate.
--   3. A hunter is assigned.
--   4. The hunter accepts or refuses.
--   5. After acceptance, matching and refinement may continue.
--   6. The mandate is signed afterwards.
--
-- Important:
--   - DEMANDE_VERSION.auteur_chasseur_id represents authorship, NOT ownership.
--   - MANDAT.id_chasseur represents the contractual hunter after signature.
--   - DEMANDE_AFFECTATION represents hunter assignment before and around
--     mandate signature.
--   - Assignment history must not be overwritten.
--
-- Historical data:
--   Existing legacy demandes already linked to a mandate are backfilled with
--   an accepted assignment derived from MANDAT.id_chasseur.
--
--   The historical authenticated actor is unknown and MUST NOT be invented.
--   For these migrated records, id_utilisateur_affectation and
--   id_utilisateur_decision therefore remain NULL.
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;


-- =============================================================================
-- 1. PRECONDITIONS
-- =============================================================================

DO $$
BEGIN
    IF to_regclass('real_estate.demande') IS NULL THEN
        RAISE EXCEPTION
            'Migration 007 aborted: real_estate.demande does not exist';
    END IF;

    IF to_regclass('real_estate.chasseur') IS NULL THEN
        RAISE EXCEPTION
            'Migration 007 aborted: real_estate.chasseur does not exist';
    END IF;

    IF to_regclass('real_estate.utilisateur') IS NULL THEN
        RAISE EXCEPTION
            'Migration 007 aborted: real_estate.utilisateur does not exist';
    END IF;

    IF to_regclass('migration_control.schema_version') IS NULL THEN
        RAISE EXCEPTION
            'Migration 007 aborted: migration_control.schema_version does not exist';
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
        WHERE version = '007'
    ) THEN
        RAISE EXCEPTION
            'Migration 007 has already been applied';
    END IF;
END
$$;


-- =============================================================================
-- 3. DEMANDE / CHASSEUR ASSIGNMENT HISTORY
--
-- One row represents one assignment attempt.
--
-- Supported states:
--
--   ASSIGNEE
--       The hunter has been assigned and has not decided yet.
--
--   ACCEPTEE
--       The hunter accepted the demande.
--       This assignment becomes the accepted business ownership link.
--
--   REFUSEE
--       The hunter refused the demande.
--       A new assignment may subsequently be created for another hunter.
--
-- We deliberately do not add additional states such as:
--
--   ANNULEE
--   REASSIGNEE
--   EXPIREE
--
-- because they are not currently supported by an authoritative business rule.
-- =============================================================================

CREATE TABLE real_estate.demande_affectation (
    id_affectation BIGINT GENERATED ALWAYS AS IDENTITY,

    id_demande BIGINT NOT NULL,

    id_chasseur BIGINT NOT NULL,

    statut VARCHAR(20) NOT NULL DEFAULT 'ASSIGNEE',

    date_affectation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    date_decision TIMESTAMPTZ,

    -- Authenticated user who performed the assignment.
    --
    -- NULL is allowed for migrated historical records where the original
    -- authenticated actor cannot be proven.
    id_utilisateur_affectation BIGINT,

    -- Authenticated user who recorded the accept/refuse decision.
    --
    -- NULL is allowed for migrated historical records where the original
    -- authenticated actor cannot be proven.
    --
    -- Future API/service logic must provide this value for authenticated
    -- application-driven decisions.
    id_utilisateur_decision BIGINT,

    motif_refus TEXT,

    CONSTRAINT pk_demande_affectation
        PRIMARY KEY (id_affectation),

    CONSTRAINT fk_demande_affectation_demande
        FOREIGN KEY (id_demande)
        REFERENCES real_estate.demande(id_demande)
        ON DELETE RESTRICT,

    CONSTRAINT fk_demande_affectation_chasseur
        FOREIGN KEY (id_chasseur)
        REFERENCES real_estate.chasseur(id_chasseur)
        ON DELETE RESTRICT,

    CONSTRAINT fk_demande_affectation_utilisateur_affectation
        FOREIGN KEY (id_utilisateur_affectation)
        REFERENCES real_estate.utilisateur(id_utilisateur)
        ON DELETE RESTRICT,

    CONSTRAINT fk_demande_affectation_utilisateur_decision
        FOREIGN KEY (id_utilisateur_decision)
        REFERENCES real_estate.utilisateur(id_utilisateur)
        ON DELETE RESTRICT,

    CONSTRAINT ck_demande_affectation_statut
        CHECK (
            statut IN (
                'ASSIGNEE',
                'ACCEPTEE',
                'REFUSEE'
            )
        ),

    -- Pending assignments must not already contain decision information.
    --
    -- Accepted/refused assignments must contain a decision timestamp.
    --
    -- id_utilisateur_decision is intentionally NOT mandatory at SQL level,
    -- because migrated legacy records have no provable authentication identity.
    -- Future application-driven decisions will enforce the actor at service/API
    -- level.
    CONSTRAINT ck_demande_affectation_decision
        CHECK (
            (
                statut = 'ASSIGNEE'
                AND date_decision IS NULL
                AND id_utilisateur_decision IS NULL
            )
            OR
            (
                statut IN (
                    'ACCEPTEE',
                    'REFUSEE'
                )
                AND date_decision IS NOT NULL
            )
        ),

    -- A refusal reason is meaningful only for a refused assignment.
    --
    -- The reason itself remains optional because the business specification
    -- does not currently require a mandatory refusal justification.
    CONSTRAINT ck_demande_affectation_motif_refus
        CHECK (
            statut = 'REFUSEE'
            OR motif_refus IS NULL
        ),

    CONSTRAINT ck_demande_affectation_dates
        CHECK (
            date_decision IS NULL
            OR date_decision >= date_affectation
        )
);


-- =============================================================================
-- 4. UNIQUENESS / CURRENT-STATE RULES
--
-- Assignment history is preserved.
--
-- A demande may therefore have several historical REFUSEE rows.
--
-- However, at most one current assignment relationship may exist:
--
--   - ASSIGNEE: waiting for the hunter decision;
--   - ACCEPTEE: accepted business ownership.
--
-- REFUSEE rows remain historical and may occur multiple times.
--
-- Reassignment after refusal is represented by creating another row.
-- =============================================================================

-- A demande may have many historical REFUSEE assignments.
--
-- However, only one current assignment relationship may exist:
-- either waiting for the hunter decision (ASSIGNEE),
-- or already accepted (ACCEPTEE).
--
-- This also prevents creating a new pending assignment while an
-- accepted hunter already owns the demande.
CREATE UNIQUE INDEX uq_demande_affectation_current
    ON real_estate.demande_affectation(id_demande)
    WHERE statut IN ('ASSIGNEE', 'ACCEPTEE');


-- =============================================================================
-- 5. OPERATIONAL INDEXES
-- =============================================================================

CREATE INDEX idx_demande_affectation_demande
    ON real_estate.demande_affectation(id_demande);


CREATE INDEX idx_demande_affectation_chasseur
    ON real_estate.demande_affectation(id_chasseur);


CREATE INDEX idx_demande_affectation_chasseur_statut
    ON real_estate.demande_affectation(
        id_chasseur,
        statut
    );


-- =============================================================================
-- 6. LEGACY BACKFILL
--
-- Legacy demandes already have a mandate.
--
-- For those records:
--
--   DEMANDE.id_mandat
--       ->
--   MANDAT.id_chasseur
--
-- gives us a reliable contractual hunter.
--
-- We therefore materialize one historical ACCEPTEE assignment so ownership
-- resolution can use the same relation for both historical and future data.
--
-- We know:
--
--   - which demande existed;
--   - which hunter was contractually responsible;
--   - approximately when the relation was already in effect.
--
-- We do NOT know:
--
--   - which authenticated user performed the assignment;
--   - which authenticated user recorded the acceptance;
--   - the exact original assignment/decision timestamps.
--
-- Those values must not be fabricated.
--
-- The demande creation timestamp is used as the historical migration timestamp
-- because it is the earliest persisted timestamp available for the demande.
-- This is migration provenance, not a claim that acceptance actually occurred
-- at that exact instant.
-- =============================================================================

INSERT INTO real_estate.demande_affectation (
    id_demande,
    id_chasseur,
    statut,
    date_affectation,
    date_decision,
    id_utilisateur_affectation,
    id_utilisateur_decision,
    motif_refus
)
SELECT
    d.id_demande,
    m.id_chasseur,
    'ACCEPTEE',
    d.date_creation,
    d.date_creation,
    NULL,
    NULL,
    NULL
FROM real_estate.demande d
JOIN real_estate.mandat m
    ON m.id_mandat = d.id_mandat
WHERE d.origine = 'LEGACY';


-- =============================================================================
-- 7. VALIDATION
-- =============================================================================

DO $$
DECLARE
    legacy_demande_count BIGINT;
    legacy_affectation_count BIGINT;
    invalid_accepted_count BIGINT;
    current_duplicate_count BIGINT;
BEGIN
    -- -------------------------------------------------------------------------
    -- Every LEGACY demande must receive exactly one accepted assignment.
    -- -------------------------------------------------------------------------

    SELECT COUNT(*)
    INTO legacy_demande_count
    FROM real_estate.demande
    WHERE origine = 'LEGACY';


    SELECT COUNT(*)
    INTO legacy_affectation_count
    FROM real_estate.demande d
    JOIN real_estate.demande_affectation da
        ON da.id_demande = d.id_demande
       AND da.statut = 'ACCEPTEE'
    WHERE d.origine = 'LEGACY';


    IF legacy_affectation_count <> legacy_demande_count THEN
        RAISE EXCEPTION
            'Migration 007 validation failed: expected % accepted legacy assignments, found %',
            legacy_demande_count,
            legacy_affectation_count;
    END IF;


    -- -------------------------------------------------------------------------
    -- The backfilled hunter must match MANDAT.id_chasseur.
    -- -------------------------------------------------------------------------

    SELECT COUNT(*)
    INTO invalid_accepted_count
    FROM real_estate.demande_affectation da
    JOIN real_estate.demande d
        ON d.id_demande = da.id_demande
    JOIN real_estate.mandat m
        ON m.id_mandat = d.id_mandat
    WHERE d.origine = 'LEGACY'
      AND da.statut = 'ACCEPTEE'
      AND da.id_chasseur <> m.id_chasseur;


    IF invalid_accepted_count <> 0 THEN
        RAISE EXCEPTION
            'Migration 007 validation failed: % legacy assignments disagree with mandate hunter',
            invalid_accepted_count;
    END IF;


    -- -------------------------------------------------------------------------
    -- A demande must have at most one current assignment relationship.
    --
    -- REFUSEE assignments are historical and may occur multiple times.
    -- -------------------------------------------------------------------------

    SELECT COUNT(*)
    INTO current_duplicate_count
    FROM (
        SELECT id_demande
        FROM real_estate.demande_affectation
        WHERE statut IN ('ASSIGNEE', 'ACCEPTEE')
        GROUP BY id_demande
        HAVING COUNT(*) > 1
    ) duplicates;


    IF current_duplicate_count <> 0 THEN
        RAISE EXCEPTION
            'Migration 007 validation failed: % demandes have multiple current assignments',
            current_duplicate_count;
    END IF;


    RAISE NOTICE
        'PASS: % legacy demandes received an accepted hunter assignment',
        legacy_affectation_count;

    RAISE NOTICE
        'PASS: legacy assignment hunter matches mandate hunter';

    RAISE NOTICE
        'PASS: no demande has multiple current assignments';
END
$$;


-- =============================================================================
-- 8. REGISTER MIGRATION
-- =============================================================================

INSERT INTO migration_control.schema_version (
    version,
    description
)
VALUES (
    '007',
    'Add demande hunter assignment and acceptance history'
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
WHERE version = '007';


SELECT
    statut,
    COUNT(*) AS affectations
FROM real_estate.demande_affectation
GROUP BY statut
ORDER BY statut;


SELECT
    COUNT(*) AS total_affectations,
    COUNT(*) FILTER (
        WHERE statut = 'ASSIGNEE'
    ) AS pending_affectations,
    COUNT(*) FILTER (
        WHERE statut = 'ACCEPTEE'
    ) AS accepted_affectations,
    COUNT(*) FILTER (
        WHERE statut = 'REFUSEE'
    ) AS refused_affectations
FROM real_estate.demande_affectation;