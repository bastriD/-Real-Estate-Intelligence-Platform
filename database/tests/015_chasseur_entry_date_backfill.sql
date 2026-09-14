-- =============================================================================
-- Test 015
-- Validate migration 012: hunter entry-date reconstruction
--
-- Expectations:
--   - all hunters with usable legacy mandate history have date_entree populated;
--   - reconstructed value equals MIN(Fil_Rouge_Depart.mandats.date_debut);
--   - migration 012 audit provenance exists;
--   - audit explicitly marks values as non-certified HR dates.
-- =============================================================================


-- =============================================================================
-- 1. No hunter with usable legacy history may remain without date_entree
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.chasseur c
    WHERE c.date_entree IS NULL
      AND EXISTS (
          SELECT 1
          FROM "Fil_Rouge_Depart".mandats m
          WHERE m.chasseur_id = c.id_chasseur
            AND m.date_debut IS NOT NULL
      );

    IF v_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % hunters with usable legacy history still have NULL date_entree',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: all hunters with usable legacy history have date_entree populated';
END;
$$;


-- =============================================================================
-- 2. Reconstructed values must match the earliest known legacy mandate
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    WITH expected AS (
        SELECT
            chasseur_id,
            MIN(date_debut) AS expected_date_entree
        FROM "Fil_Rouge_Depart".mandats
        WHERE chasseur_id IS NOT NULL
          AND date_debut IS NOT NULL
        GROUP BY chasseur_id
    )
    SELECT COUNT(*)
    INTO v_count
    FROM expected e
    JOIN real_estate.chasseur c
      ON c.id_chasseur = e.chasseur_id
    WHERE c.date_entree IS DISTINCT FROM e.expected_date_entree;

    IF v_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % hunter entry dates differ from earliest known legacy mandate date',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: reconstructed hunter entry dates match legacy MIN(date_debut)';
END;
$$;


-- =============================================================================
-- 3. Validate the known reconstructed values
--
-- These assertions protect the current migrated dataset.
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM (
        VALUES
            (1::BIGINT, DATE '2025-02-01'),
            (2::BIGINT, DATE '2025-06-18'),
            (3::BIGINT, DATE '2025-03-10'),
            (4::BIGINT, DATE '2025-05-20'),
            (5::BIGINT, DATE '2025-07-22'),
            (6::BIGINT, DATE '2025-10-02')
    ) AS expected(id_chasseur, expected_date)
    JOIN real_estate.chasseur c
      ON c.id_chasseur = expected.id_chasseur
    WHERE c.date_entree = expected.expected_date;

    IF v_count <> 6 THEN
        RAISE EXCEPTION
            'FAIL: expected 6 known hunter entry-date values, matched %',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: all 6 known hunter entry-date values are correct';
END;
$$;


-- =============================================================================
-- 4. Every migrated hunter must have migration 012 audit provenance
-- =============================================================================

DO $$
DECLARE
    v_expected_count INTEGER;
    v_audit_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_expected_count
    FROM real_estate.chasseur c
    WHERE EXISTS (
        SELECT 1
        FROM "Fil_Rouge_Depart".mandats m
        WHERE m.chasseur_id = c.id_chasseur
          AND m.date_debut IS NOT NULL
    );

    SELECT COUNT(DISTINCT a.record_id)
    INTO v_audit_count
    FROM real_estate.audit_log a
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
            'FAIL: expected % migration 012 audited hunters, found %',
            v_expected_count,
            v_audit_count;
    END IF;

    RAISE NOTICE
        'PASS: migration 012 audit provenance exists for all reconstructed hunters';
END;
$$;


-- =============================================================================
-- 5. Audit old/new values must be coherent
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM real_estate.audit_log a
    JOIN real_estate.chasseur c
      ON c.id_chasseur::text = a.record_id
    WHERE a.schema_name = 'real_estate'
      AND a.table_name = 'chasseur'
      AND a.utilisateur = 'migration_012'
      AND a.contexte ->> 'migration' = '012'
      AND (
            a.ancienne_valeur ->> 'date_entree' IS NOT NULL
         OR a.nouvelle_valeur ->> 'date_entree' IS DISTINCT FROM c.date_entree::text
      );

    IF v_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: % migration 012 audit rows have incoherent old/new values',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: migration 012 audit old/new values are coherent';
END;
$$;


-- =============================================================================
-- 6. Migration registry must contain version 012 exactly once
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM migration_control.schema_version
    WHERE version = '012';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: expected migration_control version 012 exactly once, found %',
            v_count;
    END IF;

    RAISE NOTICE
        'PASS: migration 012 registered exactly once';
END;
$$;


-- =============================================================================
-- 7. Human-readable evidence
-- =============================================================================

SELECT
    c.id_chasseur,
    c.nom,
    c.prenom,
    c.date_entree,
    MIN(m.date_debut) AS premiere_activite_legacy,
    COUNT(*) AS nb_mandats_source
FROM real_estate.chasseur c
JOIN "Fil_Rouge_Depart".mandats m
  ON m.chasseur_id = c.id_chasseur
GROUP BY
    c.id_chasseur,
    c.nom,
    c.prenom,
    c.date_entree
ORDER BY c.id_chasseur;


SELECT
    a.record_id AS id_chasseur,
    a.ancienne_valeur,
    a.nouvelle_valeur,
    a.contexte
FROM real_estate.audit_log a
WHERE a.schema_name = 'real_estate'
  AND a.table_name = 'chasseur'
  AND a.utilisateur = 'migration_012'
  AND a.contexte ->> 'migration' = '012'
ORDER BY a.record_id::BIGINT;