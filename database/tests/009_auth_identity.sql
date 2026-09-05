-- =============================================================================
-- 009_auth_identity.sql
-- Real Estate Intelligence Platform
--
-- Purpose:
--   Validate migration 006 authentication identity model.
--
-- This test verifies:
--   - real_estate.utilisateur exists;
--   - migration 006 is registered;
--   - no bootstrap/default account was created;
--   - required columns exist;
--   - role constraint exists;
--   - case-insensitive email uniqueness exists;
--   - client/chasseur uniqueness exists;
--   - business identity consistency constraint exists.
-- =============================================================================

\set ON_ERROR_STOP on

DO $$
DECLARE
    table_exists BOOLEAN;
    migration_registered INTEGER;
    utilisateur_count INTEGER;
    required_columns INTEGER;
    role_constraint_count INTEGER;
    business_constraint_count INTEGER;
    password_constraint_count INTEGER;
    email_constraint_count INTEGER;
    email_unique_index_count INTEGER;
    client_unique_index_count INTEGER;
    chasseur_unique_index_count INTEGER;
BEGIN

    -- =========================================================================
    -- 1. Table exists
    -- =========================================================================

    SELECT to_regclass('real_estate.utilisateur') IS NOT NULL
    INTO table_exists;

    IF NOT table_exists THEN
        RAISE EXCEPTION
            'FAIL: real_estate.utilisateur does not exist';
    END IF;

    RAISE NOTICE
        'PASS: real_estate.utilisateur exists';


    -- =========================================================================
    -- 2. Migration 006 registered
    -- =========================================================================

    SELECT COUNT(*)
    INTO migration_registered
    FROM migration_control.schema_version
    WHERE version = '006';

    IF migration_registered <> 1 THEN
        RAISE EXCEPTION
            'FAIL: migration 006 registration count expected 1, found %',
            migration_registered;
    END IF;

    RAISE NOTICE
        'PASS: migration 006 is registered';


    -- =========================================================================
    -- 3. No automatic/default account
    -- =========================================================================

    SELECT COUNT(*)
    INTO utilisateur_count
    FROM real_estate.utilisateur;

    IF utilisateur_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: expected 0 authentication identities after migration, found %',
            utilisateur_count;
    END IF;

    RAISE NOTICE
        'PASS: no default authentication account exists';


    -- =========================================================================
    -- 4. Required columns
    -- =========================================================================

    SELECT COUNT(*)
    INTO required_columns
    FROM information_schema.columns
    WHERE table_schema = 'real_estate'
      AND table_name = 'utilisateur'
      AND column_name IN (
          'id_utilisateur',
          'email',
          'password_hash',
          'role',
          'actif',
          'id_client',
          'id_chasseur',
          'derniere_connexion',
          'date_creation',
          'date_modification'
      );

    IF required_columns <> 10 THEN
        RAISE EXCEPTION
            'FAIL: expected 10 required utilisateur columns, found %',
            required_columns;
    END IF;

    RAISE NOTICE
        'PASS: utilisateur required columns exist';


    -- =========================================================================
    -- 5. Role constraint
    -- =========================================================================

    SELECT COUNT(*)
    INTO role_constraint_count
    FROM pg_constraint
    WHERE conname = 'ck_utilisateur_role';

    IF role_constraint_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: ck_utilisateur_role constraint missing';
    END IF;

    RAISE NOTICE
        'PASS: utilisateur role constraint exists';


    -- =========================================================================
    -- 6. Business identity consistency constraint
    -- =========================================================================

    SELECT COUNT(*)
    INTO business_constraint_count
    FROM pg_constraint
    WHERE conname = 'ck_utilisateur_business_identity';

    IF business_constraint_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: ck_utilisateur_business_identity constraint missing';
    END IF;

    RAISE NOTICE
        'PASS: utilisateur business identity constraint exists';


    -- =========================================================================
    -- 7. Password hash safety constraint
    -- =========================================================================

    SELECT COUNT(*)
    INTO password_constraint_count
    FROM pg_constraint
    WHERE conname = 'ck_utilisateur_password_hash_non_empty';

    IF password_constraint_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: ck_utilisateur_password_hash_non_empty constraint missing';
    END IF;

    RAISE NOTICE
        'PASS: utilisateur password hash constraint exists';


    -- =========================================================================
    -- 8. Email basic safety constraint
    -- =========================================================================

    SELECT COUNT(*)
    INTO email_constraint_count
    FROM pg_constraint
    WHERE conname = 'ck_utilisateur_email_basic';

    IF email_constraint_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: ck_utilisateur_email_basic constraint missing';
    END IF;

    RAISE NOTICE
        'PASS: utilisateur email constraint exists';


    -- =========================================================================
    -- 9. Case-insensitive email uniqueness
    -- =========================================================================

    SELECT COUNT(*)
    INTO email_unique_index_count
    FROM pg_indexes
    WHERE schemaname = 'real_estate'
      AND tablename = 'utilisateur'
      AND indexname = 'uq_utilisateur_email_lower';

    IF email_unique_index_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: uq_utilisateur_email_lower index missing';
    END IF;

    RAISE NOTICE
        'PASS: case-insensitive email uniqueness exists';


    -- =========================================================================
    -- 10. One identity per client
    -- =========================================================================

    SELECT COUNT(*)
    INTO client_unique_index_count
    FROM pg_indexes
    WHERE schemaname = 'real_estate'
      AND tablename = 'utilisateur'
      AND indexname = 'uq_utilisateur_client';

    IF client_unique_index_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: uq_utilisateur_client index missing';
    END IF;

    RAISE NOTICE
        'PASS: client authentication identity uniqueness exists';


    -- =========================================================================
    -- 11. One identity per hunter
    -- =========================================================================

    SELECT COUNT(*)
    INTO chasseur_unique_index_count
    FROM pg_indexes
    WHERE schemaname = 'real_estate'
      AND tablename = 'utilisateur'
      AND indexname = 'uq_utilisateur_chasseur';

    IF chasseur_unique_index_count <> 1 THEN
        RAISE EXCEPTION
            'FAIL: uq_utilisateur_chasseur index missing';
    END IF;

    RAISE NOTICE
        'PASS: chasseur authentication identity uniqueness exists';


    -- =========================================================================
    -- 12. Final result
    -- =========================================================================

    RAISE NOTICE
        'PASS: authentication identity schema validation completed successfully';

END
$$;