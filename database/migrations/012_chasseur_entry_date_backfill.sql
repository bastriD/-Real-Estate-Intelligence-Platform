BEGIN;

-- =============================================================================
-- Migration 012
-- Backfill hunter entry dates from the earliest known legacy business activity
--
-- Purpose:
--   Populate real_estate.chasseur.date_entree when the target value is NULL
--   and no certified HR/employment entry date exists in the legacy dataset.
--
-- Source:
--   Fil_Rouge_Depart.mandats
--
-- Reconstruction rule:
--
--   date_entree =
--       MIN(Fil_Rouge_Depart.mandats.date_debut)
--       GROUP BY chasseur_id
--
-- IMPORTANT SEMANTIC DISTINCTION:
--
--   The reconstructed value represents:
--
--       "earliest known business activity in the legacy information system"
--
--   It DOES NOT represent:
--
--       "certified HR employment/start date"
--
-- This distinction is persisted in real_estate.audit_log.contexte.
--
-- Safety principles:
--
--   - never overwrite an existing date_entree;
--   - only use a legacy chasseur_id matching an existing target hunter;
--   - only use non-NULL legacy mandate dates;
--   - preserve the reconstruction provenance in audit_log;
--   - fail the migration if a NULL date_entree remains for a hunter having
--     usable legacy mandate history.
--
-- Context:
--   The remuneration engine requires date_entree to calculate completed years
--   of seniority. Runtime validation showed that all six migrated hunters had
--   date_entree = NULL because the legacy system contains no explicit HR
--   employment/start-date field.
--
-- Known legacy observation:
--   Hunter 2 has four source mandates but three target mandates. This migration
--   deliberately derives the fallback directly from the legacy source and does
--   not attempt to repair or reinterpret mandate migration cardinality.
-- =============================================================================


-- =============================================================================
-- 1. Build the reconstruction set
--
-- This temporary table freezes the values used by this migration so that the
-- UPDATE, audit trail, and validation all operate on the same reconstruction
-- result.
-- =============================================================================

CREATE TEMP TABLE tmp_chasseur_date_entree_reconstruction
ON COMMIT DROP
AS
SELECT
    c.id_chasseur,
    c.date_entree AS ancienne_date_entree,
    MIN(m.date_debut) AS date_entree_reconstruite,
    COUNT(*) AS nb_mandats_source
FROM real_estate.chasseur c
JOIN "Fil_Rouge_Depart".mandats m
  ON m.chasseur_id = c.id_chasseur
WHERE c.date_entree IS NULL
  AND m.date_debut IS NOT NULL
GROUP BY
    c.id_chasseur,
    c.date_entree;


-- =============================================================================
-- 2. Pre-update safety validation
--
-- Every reconstruction candidate must have:
--   - a target hunter;
--   - a NULL current date_entree;
--   - a reconstructed source date;
--   - at least one legacy mandate supporting the reconstruction.
-- =============================================================================

DO $$
DECLARE
    v_invalid_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid_count
    FROM tmp_chasseur_date_entree_reconstruction
    WHERE ancienne_date_entree IS NOT NULL
       OR date_entree_reconstruite IS NULL
       OR nb_mandats_source <= 0;

    IF v_invalid_count <> 0 THEN
        RAISE EXCEPTION
            'Invalid hunter entry-date reconstruction candidates found: %',
            v_invalid_count;
    END IF;
END;
$$;


-- =============================================================================
-- 3. Backfill date_entree
--
-- Existing non-NULL values are never overwritten.
-- =============================================================================

UPDATE real_estate.chasseur c
SET date_entree = r.date_entree_reconstruite
FROM tmp_chasseur_date_entree_reconstruction r
WHERE c.id_chasseur = r.id_chasseur
  AND c.date_entree IS NULL;


-- =============================================================================
-- 4. Audit reconstructed values
--
-- The audit explicitly records that:
--
--   - the source is legacy mandate history;
--   - the rule is MIN(date_debut);
--   - the value is reconstructed;
--   - it is NOT a certified HR employment date.
--
-- This prevents the reconstructed value from later being interpreted as a
-- historically certified employment record.
-- =============================================================================

INSERT INTO real_estate.audit_log (
    date_evenement,
    schema_name,
    table_name,
    operation,
    record_id,
    utilisateur,
    ancienne_valeur,
    nouvelle_valeur,
    contexte
)
SELECT
    CURRENT_TIMESTAMP,
    'real_estate',
    'chasseur',
    'UPDATE',
    r.id_chasseur::text,
    'migration_012',
    jsonb_build_object(
        'date_entree',
        r.ancienne_date_entree
    ),
    jsonb_build_object(
        'date_entree',
        r.date_entree_reconstruite
    ),
    jsonb_build_object(
        'migration', '012',
        'source_schema', 'Fil_Rouge_Depart',
        'source_table', 'mandats',
        'source_column', 'date_debut',
        'source_join_key', 'chasseur_id',
        'reconstruction_rule', 'MIN(date_debut) GROUP BY chasseur_id',
        'nb_mandats_source', r.nb_mandats_source,
        'value_nature', 'EARLIEST_KNOWN_LEGACY_BUSINESS_ACTIVITY',
        'certified_hr_entry_date', false,
        'reason',
            'Legacy system contains no explicit hunter employment/start-date field; reconstructed from earliest known mandate activity for remuneration seniority calculation.'
    )
FROM tmp_chasseur_date_entree_reconstruction r;


-- =============================================================================
-- 5. Post-update validation
--
-- Every reconstruction candidate must now contain exactly the reconstructed
-- value.
-- =============================================================================

DO $$
DECLARE
    v_mismatch_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_mismatch_count
    FROM tmp_chasseur_date_entree_reconstruction r
    JOIN real_estate.chasseur c
      ON c.id_chasseur = r.id_chasseur
    WHERE c.date_entree IS DISTINCT FROM r.date_entree_reconstruite;

    IF v_mismatch_count <> 0 THEN
        RAISE EXCEPTION
            'Hunter entry-date backfill validation failed for % hunters',
            v_mismatch_count;
    END IF;
END;
$$;


-- =============================================================================
-- 6. Completeness validation
--
-- A hunter with usable legacy mandate history must not remain without an entry
-- date after this migration.
--
-- Hunters having no usable legacy history are deliberately outside the scope
-- of this reconstruction rule.
-- =============================================================================

DO $$
DECLARE
    v_remaining_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_remaining_count
    FROM real_estate.chasseur c
    WHERE c.date_entree IS NULL
      AND EXISTS (
          SELECT 1
          FROM "Fil_Rouge_Depart".mandats m
          WHERE m.chasseur_id = c.id_chasseur
            AND m.date_debut IS NOT NULL
      );

    IF v_remaining_count <> 0 THEN
        RAISE EXCEPTION
            'Hunters with usable legacy history still missing date_entree: %',
            v_remaining_count;
    END IF;
END;
$$;


-- =============================================================================
-- 7. Audit completeness validation
--
-- Every hunter modified by this migration must have exactly one corresponding
-- migration_012 audit event.
-- =============================================================================

DO $$
DECLARE
    v_expected_count INTEGER;
    v_audit_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_expected_count
    FROM tmp_chasseur_date_entree_reconstruction;

    SELECT COUNT(*)
    INTO v_audit_count
    FROM real_estate.audit_log a
    JOIN tmp_chasseur_date_entree_reconstruction r
      ON a.record_id = r.id_chasseur::text
    WHERE a.schema_name = 'real_estate'
      AND a.table_name = 'chasseur'
      AND a.operation = 'UPDATE'
      AND a.utilisateur = 'migration_012'
      AND a.contexte ->> 'migration' = '012'
      AND a.contexte ->> 'value_nature'
          = 'EARLIEST_KNOWN_LEGACY_BUSINESS_ACTIVITY'
      AND (a.contexte ->> 'certified_hr_entry_date')::boolean = FALSE;

    IF v_audit_count <> v_expected_count THEN
        RAISE EXCEPTION
            'Expected % migration_012 hunter audit events, found %',
            v_expected_count,
            v_audit_count;
    END IF;
END;
$$;


-- =============================================================================
-- 8. Data documentation
-- =============================================================================

COMMENT ON COLUMN real_estate.chasseur.date_entree IS
    'Hunter entry/reference date used for seniority calculation. For migrated legacy hunters lacking a certified HR entry date, migration 012 reconstructs this value from the earliest known legacy mandate date (MIN Fil_Rouge_Depart.mandats.date_debut). Such reconstructed values represent earliest known business activity and are not certified HR employment dates; provenance is recorded in real_estate.audit_log.';


-- =============================================================================
-- 9. Migration registry
-- =============================================================================

INSERT INTO migration_control.schema_version (
    version,
    description
)
VALUES (
    '012',
    'Backfill hunter entry dates from earliest known legacy business activity with explicit audit provenance'
);


COMMIT;