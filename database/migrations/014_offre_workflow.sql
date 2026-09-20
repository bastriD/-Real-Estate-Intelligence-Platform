-- =============================================================================
-- 014_offre_workflow.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Introduce the commercial offer workflow between property presentation
--   and completed sale.
--
-- Business lifecycle:
--   Presentation
--       -> Offre SOUMISE
--       -> ACCEPTEE / REFUSEE / RETIREE / EXPIREE
--       -> REVISEE creates a new offer version
--       -> Vente remains the completed transaction at authentic deed
--
-- Design decisions:
--   - A presentation is the stable parent of an offer.
--   - A presentation may have several historical offer versions.
--   - Each revision is preserved as a separate row.
--   - An offer is not linked to a specific visit.
--   - Vente is not modified by this migration.
--   - Existing CLIENT_SEUL / AUTRE_AGENCE sale paths remain valid.
--   - At most one accepted offer may exist per presentation.
--
-- Historical treatment:
--   No historical offers are invented or backfilled because no legacy
--   offer entity exists.
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;


-- =============================================================================
-- 1. PRECONDITIONS
-- =============================================================================

DO $$
BEGIN
    IF to_regclass('real_estate.presentation') IS NULL THEN
        RAISE EXCEPTION
            'Migration 014 aborted: real_estate.presentation does not exist';
    END IF;

    IF to_regclass('migration_control.schema_version') IS NULL THEN
        RAISE EXCEPTION
            'Migration 014 aborted: migration_control.schema_version does not exist';
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
        WHERE version = '014'
    ) THEN
        RAISE EXCEPTION
            'Migration 014 has already been applied';
    END IF;
END
$$;


-- =============================================================================
-- 3. OFFRE
--
-- One row represents one commercial proposal version.
--
-- numero_version orders proposals within one presentation.
--
-- REVISEE means that a proposal was superseded by a newer version.
-- Historical proposal amounts remain preserved.
--
-- date_decision represents an explicit commercial decision or action:
--   - ACCEPTEE
--   - REFUSEE
--   - RETIREE
--   - REVISEE
--
-- SOUMISE has not yet received a decision.
--
-- EXPIREE is a temporal outcome rather than an explicit commercial decision,
-- therefore date_decision remains NULL.
-- =============================================================================

CREATE TABLE real_estate.offre (
    id_offre BIGINT GENERATED ALWAYS AS IDENTITY,

    id_presentation BIGINT NOT NULL,

    numero_version INTEGER NOT NULL,

    montant NUMERIC(14, 2) NOT NULL,

    date_offre TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    date_expiration TIMESTAMPTZ,

    date_decision TIMESTAMPTZ,

    statut VARCHAR(20) NOT NULL DEFAULT 'SOUMISE',

    commentaire TEXT,

    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_offre
        PRIMARY KEY (id_offre),

    CONSTRAINT fk_offre_presentation
        FOREIGN KEY (id_presentation)
        REFERENCES real_estate.presentation(id_presentation)
        ON DELETE RESTRICT,

    CONSTRAINT uq_offre_presentation_version
        UNIQUE (
            id_presentation,
            numero_version
        ),

    CONSTRAINT ck_offre_numero_version
        CHECK (
            numero_version > 0
        ),

    CONSTRAINT ck_offre_montant
        CHECK (
            montant > 0
        ),

    CONSTRAINT ck_offre_statut
        CHECK (
            statut IN (
                'SOUMISE',
                'ACCEPTEE',
                'REFUSEE',
                'RETIREE',
                'EXPIREE',
                'REVISEE'
            )
        ),

    CONSTRAINT ck_offre_expiration
        CHECK (
            date_expiration IS NULL
            OR date_expiration > date_offre
        ),

    CONSTRAINT ck_offre_decision
        CHECK (
            (
                statut IN (
                    'SOUMISE',
                    'EXPIREE'
                )
                AND date_decision IS NULL
            )
            OR
            (
                statut IN (
                    'ACCEPTEE',
                    'REFUSEE',
                    'RETIREE',
                    'REVISEE'
                )
                AND date_decision IS NOT NULL
            )
        )
);


-- =============================================================================
-- 4. INDEXES AND BUSINESS UNIQUENESS
-- =============================================================================

CREATE INDEX idx_offre_presentation
    ON real_estate.offre(id_presentation);


CREATE INDEX idx_offre_statut
    ON real_estate.offre(statut);


CREATE INDEX idx_offre_date_offre
    ON real_estate.offre(date_offre);


-- A presentation may have many historical offer versions, but only one
-- accepted commercial proposal.
CREATE UNIQUE INDEX uq_offre_presentation_acceptee
    ON real_estate.offre(id_presentation)
    WHERE statut = 'ACCEPTEE';


-- =============================================================================
-- 5. VALIDATION
-- =============================================================================

DO $$
DECLARE
    invalid_offres INTEGER;
    duplicate_versions INTEGER;
    duplicate_accepted INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO invalid_offres
    FROM real_estate.offre
    WHERE numero_version <= 0
       OR montant <= 0
       OR (
            date_expiration IS NOT NULL
            AND date_expiration <= date_offre
       )
       OR (
            statut IN (
                'SOUMISE',
                'EXPIREE'
            )
            AND date_decision IS NOT NULL
       )
       OR (
            statut IN (
                'ACCEPTEE',
                'REFUSEE',
                'RETIREE',
                'REVISEE'
            )
            AND date_decision IS NULL
       );

    IF invalid_offres <> 0 THEN
        RAISE EXCEPTION
            'Migration 014 validation failed: % invalid offers found',
            invalid_offres;
    END IF;


    SELECT COUNT(*)
    INTO duplicate_versions
    FROM (
        SELECT
            id_presentation,
            numero_version
        FROM real_estate.offre
        GROUP BY
            id_presentation,
            numero_version
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicate_versions <> 0 THEN
        RAISE EXCEPTION
            'Migration 014 validation failed: % duplicate offer versions found',
            duplicate_versions;
    END IF;


    SELECT COUNT(*)
    INTO duplicate_accepted
    FROM (
        SELECT id_presentation
        FROM real_estate.offre
        WHERE statut = 'ACCEPTEE'
        GROUP BY id_presentation
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicate_accepted <> 0 THEN
        RAISE EXCEPTION
            'Migration 014 validation failed: % presentations have multiple accepted offers',
            duplicate_accepted;
    END IF;


    RAISE NOTICE
        'PASS: real_estate.offre created with versioned commercial workflow';

    RAISE NOTICE
        'PASS: offer amount, version, status and temporal constraints enabled';

    RAISE NOTICE
        'PASS: offer decision timestamp is consistent with business status';

    RAISE NOTICE
        'PASS: offer versions are unique within each presentation';

    RAISE NOTICE
        'PASS: at most one accepted offer is allowed per presentation';

    RAISE NOTICE
        'PASS: no historical offers were invented';
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
    '014',
    'Add versioned commercial offer workflow'
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
WHERE version = '014';


SELECT
    to_regclass('real_estate.offre')
        AS offre_table,

    to_regclass('real_estate.idx_offre_presentation')
        AS presentation_index,

    to_regclass('real_estate.idx_offre_statut')
        AS status_index,

    to_regclass('real_estate.idx_offre_date_offre')
        AS offer_date_index,

    to_regclass('real_estate.uq_offre_presentation_acceptee')
        AS accepted_unique_index;


SELECT
    conname,
    contype
FROM pg_constraint
WHERE conrelid = 'real_estate.offre'::regclass
ORDER BY conname;