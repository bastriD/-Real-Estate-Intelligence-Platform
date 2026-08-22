-- =============================================================================
-- 003_oltp_constraints.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Prove that PostgreSQL actively enforces critical OLTP constraints.
--
-- Strategy:
--   - Create isolated valid test data inside one transaction.
--   - Attempt invalid operations.
--   - Each negative test PASSES only when PostgreSQL rejects the operation
--     with the expected constraint class.
--   - Roll back the entire transaction at the end.
--
-- Result:
--   No test data remains in the database.
-- =============================================================================

\set ON_ERROR_STOP on

BEGIN;


-- =============================================================================
-- 0. TEST CONTEXT
-- =============================================================================

CREATE TEMP TABLE test_context (
    key   TEXT PRIMARY KEY,
    value BIGINT NOT NULL
) ON COMMIT DROP;


-- =============================================================================
-- 1. CREATE VALID CLIENT
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.client (
        nom,
        prenom,
        email,
        telephone,
        ville,
        statut,
        consentement_contact
    )
    VALUES (
        'TEST',
        'Client',
        'constraint.client@test.local',
        NULL,
        'Montpellier',
        'ACTIF',
        FALSE
    )
    RETURNING id_client
)
INSERT INTO test_context (key, value)
SELECT 'client_id', id_client
FROM inserted;


-- =============================================================================
-- 2. CREATE VALID CHASSEUR
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.chasseur (
        nom,
        prenom,
        email,
        telephone,
        statut
    )
    VALUES (
        'TEST',
        'Chasseur',
        'constraint.chasseur@test.local',
        NULL,
        'ACTIF'
    )
    RETURNING id_chasseur
)
INSERT INTO test_context (key, value)
SELECT 'chasseur_id', id_chasseur
FROM inserted;


-- =============================================================================
-- 3. CREATE VALID SECTEUR
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.secteur (
        pays,
        ville,
        quartier,
        code_postal,
        actif
    )
    VALUES (
        'France',
        'Montpellier',
        'Constraint-Test',
        '34999',
        TRUE
    )
    RETURNING id_secteur
)
INSERT INTO test_context (key, value)
SELECT 'secteur_id', id_secteur
FROM inserted;


-- =============================================================================
-- 4. CREATE VALID MANDAT
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.mandat (
        reference_mandat,
        type_mandat,
        date_signature,
        mode_signature,
        date_debut,
        date_fin,
        statut,
        id_client,
        id_chasseur
    )
    SELECT
        'TEST-CONSTRAINT-MANDAT',
        'EXCLUSIF',
        DATE '2026-01-01',
        'PAPIER',
        DATE '2026-01-01',
        DATE '2026-07-01',
        'ACTIF',
        (
            SELECT value
            FROM test_context
            WHERE key = 'client_id'
        ),
        (
            SELECT value
            FROM test_context
            WHERE key = 'chasseur_id'
        )
    RETURNING id_mandat
)
INSERT INTO test_context (key, value)
SELECT 'mandat_id', id_mandat
FROM inserted;


-- =============================================================================
-- 5. CREATE MANDAT_SECTEUR
-- =============================================================================

INSERT INTO real_estate.mandat_secteur (
    id_mandat,
    id_secteur
)
SELECT
    (
        SELECT value
        FROM test_context
        WHERE key = 'mandat_id'
    ),
    (
        SELECT value
        FROM test_context
        WHERE key = 'secteur_id'
    );


-- =============================================================================
-- 6. CREATE VALID DEMANDE
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.demande (
        reference_demande,
        statut,
        id_mandat
    )
    SELECT
        'TEST-CONSTRAINT-DEMANDE',
        'ACTIVE',
        (
            SELECT value
            FROM test_context
            WHERE key = 'mandat_id'
        )
    RETURNING id_demande
)
INSERT INTO test_context (key, value)
SELECT 'demande_id', id_demande
FROM inserted;


-- =============================================================================
-- 7. CREATE VALID ACTIVE DEMANDE VERSION
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.demande_version (
        numero_version,
        motif_modification,
        ville,
        budget_min,
        budget_max,
        active,
        id_demande,
        auteur_systeme
    )
    SELECT
        1,
        'Initial constraint test version',
        'Montpellier',
        100000,
        300000,
        TRUE,
        (
            SELECT value
            FROM test_context
            WHERE key = 'demande_id'
        ),
        TRUE
    RETURNING id_demande_version
)
INSERT INTO test_context (key, value)
SELECT 'demande_version_id', id_demande_version
FROM inserted;


-- =============================================================================
-- 8. CREATE VALID SOURCE
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.source (
        nom,
        type_source,
        actif,
        niveau_confiance
    )
    VALUES (
        'Constraint Test Source',
        'MANUEL',
        TRUE,
        'ELEVE'
    )
    RETURNING id_source
)
INSERT INTO test_context (key, value)
SELECT 'source_id', id_source
FROM inserted;


-- =============================================================================
-- 9. CREATE VALID BIEN
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.bien (
        reference_externe,
        type_bien,
        titre,
        ville,
        prix,
        surface,
        nb_pieces,
        nb_chambres,
        dpe,
        statut,
        id_source
    )
    SELECT
        'TEST-CONSTRAINT-BIEN-1',
        'APPARTEMENT',
        'Constraint Test Property 1',
        'Montpellier',
        250000,
        70,
        3,
        2,
        'C',
        'ACTIF',
        (
            SELECT value
            FROM test_context
            WHERE key = 'source_id'
        )
    RETURNING id_bien
)
INSERT INTO test_context (key, value)
SELECT 'bien_id', id_bien
FROM inserted;


-- =============================================================================
-- 10. CREATE SECOND VALID BIEN
--
-- Used for score constraint testing so the presentation uniqueness
-- constraint cannot mask the score constraint.
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.bien (
        reference_externe,
        type_bien,
        titre,
        ville,
        prix,
        surface,
        nb_pieces,
        nb_chambres,
        dpe,
        statut,
        id_source
    )
    SELECT
        'TEST-CONSTRAINT-BIEN-2',
        'APPARTEMENT',
        'Constraint Test Property 2',
        'Montpellier',
        275000,
        75,
        3,
        2,
        'B',
        'ACTIF',
        (
            SELECT value
            FROM test_context
            WHERE key = 'source_id'
        )
    RETURNING id_bien
)
INSERT INTO test_context (key, value)
SELECT 'bien_2_id', id_bien
FROM inserted;


-- =============================================================================
-- 11. CREATE VALID PRESENTATION
-- =============================================================================

INSERT INTO real_estate.presentation (
    score_matching,
    statut,
    id_demande_version,
    id_bien
)
SELECT
    85,
    'IDENTIFIE',
    (
        SELECT value
        FROM test_context
        WHERE key = 'demande_version_id'
    ),
    (
        SELECT value
        FROM test_context
        WHERE key = 'bien_id'
    );


-- =============================================================================
-- 12. CREATE VALID COMMISSION SCALE
-- =============================================================================

WITH inserted AS (
    INSERT INTO real_estate.bareme_commission (
        montant_min,
        montant_max,
        taux_commission,
        montant_fixe,
        date_debut_validite,
        actif,
        id_chasseur
    )
    SELECT
        0,
        NULL,
        0.0250,
        0,
        DATE '2026-01-01',
        TRUE,
        (
            SELECT value
            FROM test_context
            WHERE key = 'chasseur_id'
        )
    RETURNING id_bareme
)
INSERT INTO test_context (key, value)
SELECT 'bareme_id', id_bareme
FROM inserted;


-- =============================================================================
-- TEST 1
-- DUPLICATE ACTIVE DEMANDE VERSION MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
BEGIN
    SELECT value
    INTO v_demande_id
    FROM test_context
    WHERE key = 'demande_id';

    BEGIN
        INSERT INTO real_estate.demande_version (
            numero_version,
            motif_modification,
            active,
            id_demande,
            auteur_systeme
        )
        VALUES (
            2,
            'Invalid second active version',
            TRUE,
            v_demande_id,
            TRUE
        );

        RAISE EXCEPTION
            'TEST FAILED: second active demande version was accepted';

    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'PASS: second active demande version rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 2
-- DEMANDE VERSION WITH MULTIPLE AUTHORS MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_id  BIGINT;
    v_client_id   BIGINT;
    v_chasseur_id BIGINT;
BEGIN
    SELECT value INTO v_demande_id
    FROM test_context
    WHERE key = 'demande_id';

    SELECT value INTO v_client_id
    FROM test_context
    WHERE key = 'client_id';

    SELECT value INTO v_chasseur_id
    FROM test_context
    WHERE key = 'chasseur_id';

    BEGIN
        INSERT INTO real_estate.demande_version (
            numero_version,
            motif_modification,
            active,
            id_demande,
            auteur_client_id,
            auteur_chasseur_id,
            auteur_systeme
        )
        VALUES (
            2,
            'Invalid multiple authors',
            FALSE,
            v_demande_id,
            v_client_id,
            v_chasseur_id,
            FALSE
        );

        RAISE EXCEPTION
            'TEST FAILED: demande version with multiple authors was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: demande version with multiple authors rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 3
-- DEMANDE VERSION WITHOUT AUTHOR MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
BEGIN
    SELECT value INTO v_demande_id
    FROM test_context
    WHERE key = 'demande_id';

    BEGIN
        INSERT INTO real_estate.demande_version (
            numero_version,
            motif_modification,
            active,
            id_demande,
            auteur_systeme
        )
        VALUES (
            2,
            'Invalid missing author',
            FALSE,
            v_demande_id,
            FALSE
        );

        RAISE EXCEPTION
            'TEST FAILED: demande version without author was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: demande version without author rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 4
-- INVALID BUDGET RANGE MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
BEGIN
    SELECT value INTO v_demande_id
    FROM test_context
    WHERE key = 'demande_id';

    BEGIN
        INSERT INTO real_estate.demande_version (
            numero_version,
            motif_modification,
            budget_min,
            budget_max,
            active,
            id_demande,
            auteur_systeme
        )
        VALUES (
            2,
            'Invalid budget range',
            500000,
            300000,
            FALSE,
            v_demande_id,
            TRUE
        );

        RAISE EXCEPTION
            'TEST FAILED: budget_min > budget_max was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: invalid budget range rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 5
-- INVALID DPE MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_source_id BIGINT;
BEGIN
    SELECT value INTO v_source_id
    FROM test_context
    WHERE key = 'source_id';

    BEGIN
        INSERT INTO real_estate.bien (
            reference_externe,
            type_bien,
            ville,
            dpe,
            statut,
            id_source
        )
        VALUES (
            'TEST-INVALID-DPE',
            'APPARTEMENT',
            'Montpellier',
            'Z',
            'ACTIF',
            v_source_id
        );

        RAISE EXCEPTION
            'TEST FAILED: invalid DPE Z was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: invalid DPE rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 6
-- DUPLICATE PRESENTATION MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_version_id BIGINT;
    v_bien_id            BIGINT;
BEGIN
    SELECT value INTO v_demande_version_id
    FROM test_context
    WHERE key = 'demande_version_id';

    SELECT value INTO v_bien_id
    FROM test_context
    WHERE key = 'bien_id';

    BEGIN
        INSERT INTO real_estate.presentation (
            score_matching,
            statut,
            id_demande_version,
            id_bien
        )
        VALUES (
            90,
            'QUALIFIE',
            v_demande_version_id,
            v_bien_id
        );

        RAISE EXCEPTION
            'TEST FAILED: duplicate presentation was accepted';

    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'PASS: duplicate presentation rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 7
-- COMMISSION RATE > 1 MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_chasseur_id BIGINT;
BEGIN
    SELECT value INTO v_chasseur_id
    FROM test_context
    WHERE key = 'chasseur_id';

    BEGIN
        INSERT INTO real_estate.bareme_commission (
            montant_min,
            montant_max,
            taux_commission,
            montant_fixe,
            date_debut_validite,
            actif,
            id_chasseur
        )
        VALUES (
            0,
            NULL,
            1.5000,
            0,
            DATE '2026-01-01',
            TRUE,
            v_chasseur_id
        );

        RAISE EXCEPTION
            'TEST FAILED: commission rate > 1 was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: commission rate > 1 rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 8
-- NEGATIVE PAYMENT AMOUNT MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_mandat_id BIGINT;
    v_bareme_id BIGINT;
BEGIN
    SELECT value INTO v_mandat_id
    FROM test_context
    WHERE key = 'mandat_id';

    SELECT value INTO v_bareme_id
    FROM test_context
    WHERE key = 'bareme_id';

    BEGIN
        INSERT INTO real_estate.paiement (
            montant_achat,
            montant_honoraires,
            montant_chasseur,
            statut,
            id_mandat,
            id_bareme
        )
        VALUES (
            -100,
            1000,
            500,
            'ATTENDU',
            v_mandat_id,
            v_bareme_id
        );

        RAISE EXCEPTION
            'TEST FAILED: negative payment amount was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: negative payment amount rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 9
-- INVALID FOREIGN KEY MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_chasseur_id BIGINT;
BEGIN
    SELECT value INTO v_chasseur_id
    FROM test_context
    WHERE key = 'chasseur_id';

    BEGIN
        INSERT INTO real_estate.mandat (
            reference_mandat,
            type_mandat,
            date_signature,
            mode_signature,
            date_debut,
            date_fin,
            statut,
            id_client,
            id_chasseur
        )
        VALUES (
            'TEST-INVALID-FK',
            'NON_EXCLUSIF',
            DATE '2026-01-01',
            'INCONNU',
            DATE '2026-01-01',
            DATE '2026-07-01',
            'ACTIF',
            999999999,
            v_chasseur_id
        );

        RAISE EXCEPTION
            'TEST FAILED: invalid client FK was accepted';

    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE
                'PASS: invalid foreign key rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 10
-- COMMENT WITH MULTIPLE AUTHORS MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_version_id BIGINT;
    v_bien_id            BIGINT;
    v_client_id          BIGINT;
    v_chasseur_id        BIGINT;
BEGIN
    SELECT value INTO v_demande_version_id
    FROM test_context
    WHERE key = 'demande_version_id';

    SELECT value INTO v_bien_id
    FROM test_context
    WHERE key = 'bien_id';

    SELECT value INTO v_client_id
    FROM test_context
    WHERE key = 'client_id';

    SELECT value INTO v_chasseur_id
    FROM test_context
    WHERE key = 'chasseur_id';

    BEGIN
        INSERT INTO real_estate.commentaire (
            contenu,
            id_demande_version,
            id_bien,
            auteur_client_id,
            auteur_chasseur_id
        )
        VALUES (
            'Invalid comment with two authors',
            v_demande_version_id,
            v_bien_id,
            v_client_id,
            v_chasseur_id
        );

        RAISE EXCEPTION
            'TEST FAILED: comment with multiple authors was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: comment with multiple authors rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 11
-- PRESENTATION SCORE > 100 MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_version_id BIGINT;
    v_bien_2_id          BIGINT;
BEGIN
    SELECT value INTO v_demande_version_id
    FROM test_context
    WHERE key = 'demande_version_id';

    SELECT value INTO v_bien_2_id
    FROM test_context
    WHERE key = 'bien_2_id';

    BEGIN
        INSERT INTO real_estate.presentation (
            score_matching,
            statut,
            id_demande_version,
            id_bien
        )
        VALUES (
            150,
            'IDENTIFIE',
            v_demande_version_id,
            v_bien_2_id
        );

        RAISE EXCEPTION
            'TEST FAILED: matching score > 100 was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: matching score > 100 rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 12
-- NEGATIVE PROPERTY PRICE MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_source_id BIGINT;
BEGIN
    SELECT value INTO v_source_id
    FROM test_context
    WHERE key = 'source_id';

    BEGIN
        INSERT INTO real_estate.bien (
            reference_externe,
            type_bien,
            prix,
            statut,
            id_source
        )
        VALUES (
            'TEST-NEGATIVE-PRICE',
            'APPARTEMENT',
            -1,
            'ACTIF',
            v_source_id
        );

        RAISE EXCEPTION
            'TEST FAILED: negative property price was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: negative property price rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 13
-- INVALID MANDATE DATE RANGE MUST FAIL
--
-- Exact six-month enforcement is intentionally NOT tested because the
-- project has not activated that constraint. We test only the currently
-- implemented rule:
--
--     date_fin >= date_debut
-- =============================================================================

DO $$
DECLARE
    v_client_id   BIGINT;
    v_chasseur_id BIGINT;
BEGIN
    SELECT value INTO v_client_id
    FROM test_context
    WHERE key = 'client_id';

    SELECT value INTO v_chasseur_id
    FROM test_context
    WHERE key = 'chasseur_id';

    BEGIN
        INSERT INTO real_estate.mandat (
            reference_mandat,
            type_mandat,
            date_signature,
            mode_signature,
            date_debut,
            date_fin,
            statut,
            id_client,
            id_chasseur
        )
        VALUES (
            'TEST-INVALID-DATES',
            'EXCLUSIF',
            DATE '2026-01-01',
            'PAPIER',
            DATE '2026-07-01',
            DATE '2026-01-01',
            'ACTIF',
            v_client_id,
            v_chasseur_id
        );

        RAISE EXCEPTION
            'TEST FAILED: invalid mandate date range was accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: invalid mandate date range rejected';
    END;
END
$$;


-- =============================================================================
-- TEST 14
-- AUTHOR SYSTEM + CLIENT MUST FAIL
-- =============================================================================

DO $$
DECLARE
    v_demande_id BIGINT;
    v_client_id  BIGINT;
BEGIN
    SELECT value INTO v_demande_id
    FROM test_context
    WHERE key = 'demande_id';

    SELECT value INTO v_client_id
    FROM test_context
    WHERE key = 'client_id';

    BEGIN
        INSERT INTO real_estate.demande_version (
            numero_version,
            motif_modification,
            active,
            id_demande,
            auteur_client_id,
            auteur_systeme
        )
        VALUES (
            2,
            'Invalid system and client authors',
            FALSE,
            v_demande_id,
            v_client_id,
            TRUE
        );

        RAISE EXCEPTION
            'TEST FAILED: system + client authors were accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'PASS: system + client author combination rejected';
    END;
END
$$;


-- =============================================================================
-- FINAL RESULT
-- =============================================================================

SELECT
    'PASS' AS status,
    'OLTP constraints enforced successfully' AS result;


-- =============================================================================
-- CLEANUP
--
-- Every valid setup row created by this script is rolled back.
-- Each expected failing statement is already isolated by a PL/pgSQL
-- exception subtransaction.
-- =============================================================================

ROLLBACK;