-- =============================================================================
-- Migration 008
-- Mandat contractual lifecycle and renewal history
--
-- Business rules:
--   - A Mandat is the contractual identity.
--   - A Mandat has one or more contractual periods.
--   - The first period is INITIAL.
--   - Following periods are RENOUVELLEMENT.
--   - New contractual periods last exactly six calendar months.
--   - A renewal must not overwrite previous contractual history.
--   - Existing historical Mandats are preserved exactly as stored.
--   - Renewal periods are contiguous:
--
--         new.date_debut = previous.date_fin
--
--   - Contractual periods are immutable once created.
--
-- Existing real_estate.mandat.date_debut/date_fin remain available as the
-- current/latest contractual period for backward compatibility with the
-- existing API, warehouse and application model.
-- =============================================================================

BEGIN;


-- =============================================================================
-- 1. MANDAT_PERIODE
-- =============================================================================

CREATE TABLE real_estate.mandat_periode (
    id_mandat_periode BIGINT GENERATED ALWAYS AS IDENTITY,

    id_mandat BIGINT NOT NULL,

    numero_periode INTEGER NOT NULL,

    type_periode VARCHAR(30) NOT NULL,

    date_debut DATE NOT NULL,

    date_fin DATE NOT NULL,

    date_renouvellement DATE,

    commentaire TEXT,

    -- Existing Mandats can contain historical durations which were created
    -- before the six-month lifecycle rule was implemented.
    --
    -- Those values must be preserved, not rewritten.
    est_historique_legacy BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_mandat_periode
        PRIMARY KEY (
            id_mandat_periode
        ),

    CONSTRAINT fk_mandat_periode_mandat
        FOREIGN KEY (
            id_mandat
        )
        REFERENCES real_estate.mandat (
            id_mandat
        )
        ON DELETE CASCADE,

    CONSTRAINT uq_mandat_periode_numero
        UNIQUE (
            id_mandat,
            numero_periode
        ),

    CONSTRAINT ck_mandat_periode_numero
        CHECK (
            numero_periode >= 1
        ),

    CONSTRAINT ck_mandat_periode_type
        CHECK (
            type_periode IN (
                'INITIAL',
                'RENOUVELLEMENT'
            )
        ),

    CONSTRAINT ck_mandat_periode_dates
        CHECK (
            date_fin >= date_debut
        ),

    -- All newly created periods must last exactly six calendar months.
    --
    -- Historical periods loaded during this migration are exempt because
    -- their original contractual values must remain unchanged.
    CONSTRAINT ck_mandat_periode_duree
        CHECK (
            est_historique_legacy = TRUE
            OR date_fin = (
                date_debut + INTERVAL '6 months'
            )::date
        ),

    CONSTRAINT ck_mandat_periode_renouvellement
        CHECK (
            (
                type_periode = 'INITIAL'
                AND date_renouvellement IS NULL
            )
            OR
            (
                type_periode = 'RENOUVELLEMENT'
                AND date_renouvellement IS NOT NULL
            )
        )
);


-- =============================================================================
-- 2. ONLY ONE INITIAL PERIOD PER MANDAT
-- =============================================================================

CREATE UNIQUE INDEX uq_mandat_periode_initial
    ON real_estate.mandat_periode (
        id_mandat
    )
    WHERE type_periode = 'INITIAL';


CREATE INDEX idx_mandat_periode_mandat
    ON real_estate.mandat_periode (
        id_mandat
    );


CREATE INDEX idx_mandat_periode_dates
    ON real_estate.mandat_periode (
        date_debut,
        date_fin
    );


-- =============================================================================
-- 3. BACKFILL EXISTING MANDATS
-- =============================================================================
--
-- Existing Mandats were created before renewal semantics were implemented.
--
-- Their current dates are copied exactly.
--
-- We intentionally DO NOT modify historical dates to force artificial
-- six-month compliance.
--
-- Example:
--
--     Mandat 11
--     date_debut = 2026-01-05
--     date_fin   = 2026-07-05
--
-- becomes:
--
--     periode #1
--     INITIAL
--     2026-01-05 -> 2026-07-05
--
-- with est_historique_legacy = TRUE.
-- =============================================================================

INSERT INTO real_estate.mandat_periode (
    id_mandat,
    numero_periode,
    type_periode,
    date_debut,
    date_fin,
    date_renouvellement,
    commentaire,
    est_historique_legacy
)
SELECT
    m.id_mandat,
    1,
    'INITIAL',
    m.date_debut,
    m.date_fin,
    NULL,
    'Initial contractual period backfilled by migration 008',
    TRUE
FROM real_estate.mandat m
WHERE NOT EXISTS (
    SELECT 1
    FROM real_estate.mandat_periode mp
    WHERE mp.id_mandat = m.id_mandat
);


-- =============================================================================
-- 4. INSERT VALIDATION
-- =============================================================================
--
-- Enforces the contractual sequence.
--
-- INITIAL:
--     numero_periode = 1
--
-- RENOUVELLEMENT:
--     previous period must exist
--     numero = previous.numero + 1
--     date_debut = previous.date_fin
--
-- Equal boundaries are intentional:
--
--     period 1: 2026-01-05 -> 2026-07-05
--     period 2: 2026-07-05 -> 2027-01-05
--
-- This follows the business convention documented by the project.
-- =============================================================================

CREATE OR REPLACE FUNCTION real_estate.validate_mandat_periode_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    previous_periode real_estate.mandat_periode%ROWTYPE;
    mandat_signature DATE;
BEGIN

    -- -------------------------------------------------------------------------
    -- INITIAL PERIOD
    -- -------------------------------------------------------------------------

    IF NEW.type_periode = 'INITIAL' THEN

        IF NEW.numero_periode <> 1 THEN
            RAISE EXCEPTION
                'Initial Mandat period must have numero_periode = 1';
        END IF;

        -- For newly created Mandats, the contractual period starts on the
        -- signature date.
        --
        -- Legacy historical rows are intentionally exempt.
        IF NEW.est_historique_legacy = FALSE THEN

            SELECT
                m.date_signature
            INTO mandat_signature
            FROM real_estate.mandat m
            WHERE m.id_mandat = NEW.id_mandat;

            IF mandat_signature IS NULL THEN
                RAISE EXCEPTION
                    'Mandat % does not exist',
                    NEW.id_mandat;
            END IF;

            IF NEW.date_debut <> mandat_signature THEN
                RAISE EXCEPTION
                    'Initial Mandat period must start on the Mandat signature date';
            END IF;

        END IF;

        RETURN NEW;

    END IF;


    -- -------------------------------------------------------------------------
    -- RENEWAL PERIOD
    -- -------------------------------------------------------------------------

    IF NEW.type_periode = 'RENOUVELLEMENT' THEN

        SELECT
            mp.*
        INTO previous_periode
        FROM real_estate.mandat_periode mp
        WHERE mp.id_mandat = NEW.id_mandat
        ORDER BY mp.numero_periode DESC
        LIMIT 1
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'Cannot renew Mandat % without an existing contractual period',
                NEW.id_mandat;
        END IF;


        IF NEW.numero_periode <> (
            previous_periode.numero_periode + 1
        ) THEN
            RAISE EXCEPTION
                'Invalid period number for Mandat %. Expected %, received %',
                NEW.id_mandat,
                previous_periode.numero_periode + 1,
                NEW.numero_periode;
        END IF;


        IF NEW.date_debut <> previous_periode.date_fin THEN
            RAISE EXCEPTION
                'Renewal period must start on previous period end date';
        END IF;


        IF NEW.est_historique_legacy = TRUE THEN
            RAISE EXCEPTION
                'A new renewal cannot be marked as historical legacy data';
        END IF;

        RETURN NEW;

    END IF;


    RETURN NEW;

END;
$$;


CREATE TRIGGER trg_validate_mandat_periode_insert
BEFORE INSERT
ON real_estate.mandat_periode
FOR EACH ROW
EXECUTE FUNCTION real_estate.validate_mandat_periode_insert();


-- =============================================================================
-- 5. CONTRACTUAL PERIOD IMMUTABILITY
-- =============================================================================
--
-- A contractual period is historical business evidence.
--
-- Once inserted, it must not be silently rewritten.
--
-- Corrections requiring a business decision must be handled explicitly,
-- rather than editing historical contractual facts.
-- =============================================================================

CREATE OR REPLACE FUNCTION real_estate.prevent_mandat_periode_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    RAISE EXCEPTION
        'Mandat contractual periods are immutable';

END;
$$;


CREATE TRIGGER trg_prevent_mandat_periode_update
BEFORE UPDATE
ON real_estate.mandat_periode
FOR EACH ROW
EXECUTE FUNCTION real_estate.prevent_mandat_periode_update();


-- =============================================================================
-- 6. OVERLAP PROTECTION
-- =============================================================================
--
-- Period boundaries follow a half-open business convention:
--
--     [date_debut, date_fin)
--
-- Therefore:
--
--     old.date_fin = new.date_debut
--
-- is allowed.
--
-- Actual overlap is forbidden.
-- =============================================================================

CREATE OR REPLACE FUNCTION real_estate.prevent_mandat_periode_overlap()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF EXISTS (
        SELECT 1
        FROM real_estate.mandat_periode existing
        WHERE existing.id_mandat = NEW.id_mandat
          AND NEW.date_debut < existing.date_fin
          AND NEW.date_fin > existing.date_debut
    ) THEN

        RAISE EXCEPTION
            'Contractual period overlaps an existing period for Mandat %',
            NEW.id_mandat;

    END IF;

    RETURN NEW;

END;
$$;


CREATE TRIGGER trg_prevent_mandat_periode_overlap
BEFORE INSERT
ON real_estate.mandat_periode
FOR EACH ROW
EXECUTE FUNCTION real_estate.prevent_mandat_periode_overlap();


-- =============================================================================
-- 7. DOCUMENTATION COMMENTS
-- =============================================================================

COMMENT ON TABLE real_estate.mandat_periode IS
'Historical contractual periods of a Mandat. Initial period and renewals are preserved without overwriting previous contractual history.';


COMMENT ON COLUMN real_estate.mandat_periode.numero_periode IS
'Sequential contractual period number. Initial period is 1; renewals increment the value by one.';


COMMENT ON COLUMN real_estate.mandat_periode.type_periode IS
'INITIAL for the original contractual period, RENOUVELLEMENT for subsequent periods.';


COMMENT ON COLUMN real_estate.mandat_periode.date_renouvellement IS
'Date on which the renewal decision/signature was recorded. NULL for the initial period.';


COMMENT ON COLUMN real_estate.mandat_periode.est_historique_legacy IS
'TRUE only for historical Mandat periods existing before migration 008. Legacy dates are preserved exactly and are exempt from the new six-month duration constraint.';


-- =============================================================================
-- 8. MIGRATION REGISTRY
-- =============================================================================

INSERT INTO migration_control.schema_version (
    version,
    description
)
VALUES (
    '008',
    'Add Mandat six-month contractual lifecycle and renewal history'
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
WHERE version = '008';


SELECT
    COUNT(*) AS total_mandats
FROM real_estate.mandat;


SELECT
    COUNT(*) AS total_mandat_periodes
FROM real_estate.mandat_periode;


SELECT
    type_periode,
    est_historique_legacy,
    COUNT(*) AS periodes
FROM real_estate.mandat_periode
GROUP BY
    type_periode,
    est_historique_legacy
ORDER BY
    type_periode,
    est_historique_legacy;


SELECT
    m.id_mandat,
    m.reference_mandat,
    m.date_signature,
    m.date_debut AS mandat_date_debut,
    m.date_fin AS mandat_date_fin,
    mp.numero_periode,
    mp.type_periode,
    mp.date_debut AS periode_date_debut,
    mp.date_fin AS periode_date_fin,
    mp.est_historique_legacy
FROM real_estate.mandat m
JOIN real_estate.mandat_periode mp
    ON mp.id_mandat = m.id_mandat
ORDER BY
    m.id_mandat,
    mp.numero_periode;