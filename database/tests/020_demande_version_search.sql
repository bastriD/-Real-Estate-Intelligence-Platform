-- PostgreSQL assertions for migration 017. Run only through the manual CI job.
-- Fixture changes roll back; identity sequences can advance.
\set ON_ERROR_STOP on
BEGIN;
CREATE FUNCTION pg_temp.assert_search(ok BOOLEAN, message TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    IF ok IS DISTINCT FROM TRUE THEN RAISE EXCEPTION 'FAIL: %', message; END IF;
    RAISE NOTICE 'PASS: %', message;
END;
$$;
SELECT pg_temp.assert_search(
    (SELECT COUNT(*) = 1 FROM migration_control.schema_version WHERE version = '017'),
    'migration 017 registered');
SELECT pg_temp.assert_search(to_regclass('real_estate.demande_version_secteur') IS NOT NULL,
    'versioned search geography exists');
SELECT pg_temp.assert_search(
    (SELECT COUNT(*) = 17 FROM real_estate.demande d JOIN real_estate.demande_version dv USING(id_demande)
    WHERE d.origine = 'LEGACY' AND dv.numero_version = 1 AND dv.type_bien IS NOT NULL
        AND LENGTH(dv.description_recherche_legacy) > 0), 'all 17 legacy descriptions retained and enriched');
SELECT pg_temp.assert_search(
    (SELECT dv.surface_min IS NULL AND dv.nb_pieces_min = 4 FROM real_estate.demande d
    JOIN real_estate.demande_version dv USING(id_demande)
    WHERE d.reference_demande = 'LEGACY-DEMANDE-12' AND dv.numero_version = 1),
    'unspecified Nantes surface not invented');
SELECT pg_temp.assert_search(
    (SELECT dv.criteres_souhaites = '["terrasse ou jardin"]'::jsonb FROM real_estate.demande d
    JOIN real_estate.demande_version dv USING(id_demande)
    WHERE d.reference_demande = 'LEGACY-DEMANDE-2' AND dv.numero_version = 1),
    'alternative preference retained verbatim');
SELECT pg_temp.assert_search(
    (SELECT COUNT(*) = 13 FROM real_estate.demande d
    JOIN real_estate.demande_version dv USING(id_demande)
    JOIN real_estate.demande_version_secteur ds USING(id_demande_version)
    WHERE d.origine = 'LEGACY' AND dv.numero_version = 1), '13 explicit legacy sector associations');

CREATE TEMP TABLE search_sectors ON COMMIT DROP AS
SELECT ds.id_secteur FROM real_estate.demande d
JOIN real_estate.demande_version dv USING(id_demande)
JOIN real_estate.demande_version_secteur ds USING(id_demande_version)
WHERE d.reference_demande = 'LEGACY-DEMANDE-8' AND dv.numero_version = 1;
SELECT pg_temp.assert_search((SELECT COUNT(*) = 2 FROM search_sectors),
    'Ecusson OR Beaux-Arts provides two alternatives');

CREATE TEMP TABLE search_test_versions(id_demande_version BIGINT) ON COMMIT DROP;
WITH inserted AS (
    INSERT INTO real_estate.demande_version(id_demande, numero_version, motif_modification, active, auteur_systeme)
    SELECT d.id_demande, (SELECT MAX(numero_version) + 1 FROM real_estate.demande_version v
        WHERE v.id_demande = d.id_demande), 'Test 020 version isolation', FALSE, TRUE
    FROM real_estate.demande d WHERE d.reference_demande = 'LEGACY-DEMANDE-8'
    RETURNING id_demande_version
) INSERT INTO search_test_versions SELECT id_demande_version FROM inserted;
INSERT INTO real_estate.demande_version_secteur(id_demande_version, id_secteur)
SELECT id_demande_version, MIN(id_secteur) FROM search_test_versions CROSS JOIN search_sectors
GROUP BY id_demande_version;
SELECT pg_temp.assert_search(
    (SELECT COUNT(*) = 1 FROM real_estate.demande_version_secteur
    WHERE id_demande_version IN (SELECT id_demande_version FROM search_test_versions)),
    'new version has its own sector set');
SELECT pg_temp.assert_search(
    (SELECT COUNT(*) = 2 FROM real_estate.demande d JOIN real_estate.demande_version dv USING(id_demande)
    JOIN real_estate.demande_version_secteur ds USING(id_demande_version)
    WHERE d.reference_demande = 'LEGACY-DEMANDE-8' AND dv.numero_version = 1),
    'earlier version retains both alternatives');

DO $$
DECLARE actual_constraint TEXT;
BEGIN
    BEGIN
        INSERT INTO real_estate.demande_version_secteur
        SELECT ds.* FROM real_estate.demande_version_secteur ds
        JOIN search_test_versions v USING(id_demande_version);
        RAISE EXCEPTION 'FAIL: duplicate version sector accepted';
    EXCEPTION WHEN unique_violation THEN
        GET STACKED DIAGNOSTICS actual_constraint = CONSTRAINT_NAME;
        IF actual_constraint <> 'pk_demande_version_secteur' THEN RAISE; END IF;
    END;
    BEGIN
        INSERT INTO real_estate.demande_version_secteur
        SELECT id_demande_version, (SELECT MAX(id_secteur) + 1 FROM real_estate.secteur)
        FROM search_test_versions;
        RAISE EXCEPTION 'FAIL: missing sector accepted';
    EXCEPTION WHEN foreign_key_violation THEN
        GET STACKED DIAGNOSTICS actual_constraint = CONSTRAINT_NAME;
        IF actual_constraint <> 'fk_demande_version_secteur_secteur' THEN RAISE; END IF;
    END;
END;
$$;

CREATE TEMP TABLE search_test_biens(id_bien BIGINT) ON COMMIT DROP;
SELECT pg_temp.assert_search(EXISTS(SELECT 1 FROM real_estate.source), 'source reference available for property fixture');
WITH inserted AS (
    INSERT INTO real_estate.bien(reference_externe, type_bien, ville, prix, surface, statut, id_source, id_secteur)
    SELECT 'TEST-020-' || txid_current() || '-' || COALESCE(s.id_secteur::TEXT, 'unknown'),
        'Appartement', 'Montpellier', 250000, 70, 'ACTIF',
        (SELECT MIN(id_source) FROM real_estate.source), s.id_secteur
    FROM (SELECT id_secteur FROM search_sectors UNION ALL SELECT NULL::BIGINT) s
    RETURNING id_bien
) INSERT INTO search_test_biens SELECT id_bien FROM inserted;
SELECT pg_temp.assert_search(
    (SELECT COUNT(*) = 2 FROM real_estate.bien b JOIN search_test_biens t USING(id_bien)
    WHERE b.id_secteur = ANY(ARRAY(SELECT id_secteur FROM search_sectors))),
    'alternative matching accepts both sectors and excludes unknown geography');
SELECT pg_temp.assert_search(
    (SELECT COUNT(*) = 3 FROM real_estate.bien b JOIN search_test_biens t USING(id_bien)
    WHERE b.ville = 'Montpellier'), 'city-only search retains unmapped properties');
DO $$
DECLARE actual_constraint TEXT;
BEGIN
    BEGIN
        UPDATE real_estate.bien SET id_secteur = (SELECT MAX(id_secteur) + 1 FROM real_estate.secteur)
        WHERE id_bien IN (SELECT id_bien FROM search_test_biens);
        RAISE EXCEPTION 'FAIL: missing property sector accepted';
    EXCEPTION WHEN foreign_key_violation THEN
        GET STACKED DIAGNOSTICS actual_constraint = CONSTRAINT_NAME;
        IF actual_constraint <> 'fk_bien_secteur' THEN RAISE; END IF;
    END;
END;
$$;
UPDATE real_estate.bien SET prix = prix + 1, ville = ville WHERE id_bien IN (SELECT id_bien FROM search_test_biens);
SELECT pg_temp.assert_search(
    (SELECT COUNT(id_secteur) = 2 FROM real_estate.bien WHERE id_bien IN (SELECT id_bien FROM search_test_biens)),
    'price refresh preserves reviewed sector');
UPDATE real_estate.bien SET adresse = 'Changed location fixture'
WHERE id_bien IN (SELECT id_bien FROM search_test_biens);
SELECT pg_temp.assert_search(
    (SELECT COUNT(id_secteur) = 0 FROM real_estate.bien WHERE id_bien IN (SELECT id_bien FROM search_test_biens)),
    'location change invalidates reviewed sector');
SELECT pg_temp.assert_search(
    (SELECT COUNT(*) = 2 FROM real_estate.audit_log WHERE table_name = 'bien'
    AND record_id IN (SELECT id_bien::TEXT FROM search_test_biens)
    AND contexte->>'action' = 'invalidate_bien_secteur'), 'geography invalidation audited');
DELETE FROM real_estate.demande_version WHERE id_demande_version IN (SELECT id_demande_version FROM search_test_versions);
SELECT pg_temp.assert_search(
    NOT EXISTS (SELECT 1 FROM real_estate.demande_version_secteur
        WHERE id_demande_version IN (SELECT id_demande_version FROM search_test_versions)),
    'version deletion cascades only its own geography links');
ROLLBACK;
