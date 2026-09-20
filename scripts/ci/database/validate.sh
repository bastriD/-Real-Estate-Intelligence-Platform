#!/bin/sh
# database:validate / script. Sourced by GitLab; run from the project checkout.

test -f database/migrations/001_initial_schema.sql
test -f database/migrations/002_migrate_legacy_data.sql
test -f database/migrations/004_add_visite_audit.sql
test -f database/migrations/005_demande_pre_mandat.sql
test -f database/migrations/006_auth_identity.sql
test -f database/migrations/007_demande_chasseur_affectation.sql
test -f database/migrations/008_mandat_lifecycle.sql
test -f database/migrations/009_mandat_lifecycle_warehouse.sql
test -f database/migrations/010_transaction_remuneration.sql
test -f database/migrations/011_initial_remuneration_configuration.sql
test -f database/migrations/012_chasseur_entry_date_backfill.sql
test -f database/migrations/013_demande_client_ownership.sql
test -f database/tests/001_schema_structure.sql
test -f database/tests/002_legacy_migration.sql
test -f database/tests/003_oltp_constraints.sql
test -f database/tests/008_visite_audit.sql
test -f database/tests/009_auth_identity.sql
test -f database/tests/010_demande_affectation.sql
test -f database/tests/011_mandat_lifecycle.sql
test -f database/tests/012_mandat_lifecycle_warehouse.sql
test -f database/tests/013_transaction_remuneration.sql
test -f database/tests/014_remuneration_configuration.sql
test -f database/tests/015_chasseur_entry_date_backfill.sql
test -f database/tests/016_demande_client_ownership.sql
test -f database/legacy/PgSQL.sql
test -f database/oltp/001_operational_queries.sql
test -f database/oltp/002_explain_analyze.sql
test -f database/oltp/003_raw_ingestion_schema.sql
test -f database/oltp/004_staging_schema.sql
test -f database/seeds/load_raw_generated_data.py
test -f database/seeds/load_staging_recherches_to_oltp.py
test -f database/seeds/load_staging_to_oltp.py
test -f requirements.txt
grep -q "CREATE SCHEMA IF NOT EXISTS real_estate;" database/migrations/001_initial_schema.sql
grep -q "CREATE TABLE real_estate.client" database/migrations/001_initial_schema.sql
grep -q "CREATE TABLE real_estate.paiement" database/migrations/001_initial_schema.sql
grep -q "^COMMIT;" database/migrations/001_initial_schema.sql
grep -q "CREATE SCHEMA IF NOT EXISTS migration_control;" database/migrations/002_migrate_legacy_data.sql
grep -q "Migration 002" database/migrations/002_migrate_legacy_data.sql
grep -q "^COMMIT;" database/migrations/002_migrate_legacy_data.sql
grep -q "CREATE TABLE IF NOT EXISTS real_estate.visite" database/migrations/004_add_visite_audit.sql
grep -q "CREATE TABLE IF NOT EXISTS real_estate.audit_log" database/migrations/004_add_visite_audit.sql
grep -q "fk_visite_presentation" database/migrations/004_add_visite_audit.sql
grep -q "ck_audit_log_operation" database/migrations/004_add_visite_audit.sql
grep -q "'004'" database/migrations/004_add_visite_audit.sql
grep -q "migration_control.schema_version" database/migrations/004_add_visite_audit.sql
grep -q "^COMMIT;" database/migrations/004_add_visite_audit.sql
grep -q "ALTER COLUMN id_mandat DROP NOT NULL" database/migrations/005_demande_pre_mandat.sql
grep -q "origine" database/migrations/005_demande_pre_mandat.sql
grep -q "source_recherche_ref" database/migrations/005_demande_pre_mandat.sql
grep -q "ingestion_batch" database/migrations/005_demande_pre_mandat.sql
grep -q "'005'" database/migrations/005_demande_pre_mandat.sql
grep -q "migration_control.schema_version" database/migrations/005_demande_pre_mandat.sql
grep -q "^COMMIT;" database/migrations/005_demande_pre_mandat.sql
grep -q "CREATE TABLE real_estate.utilisateur" database/migrations/006_auth_identity.sql
grep -q "password_hash" database/migrations/006_auth_identity.sql
grep -q "ck_utilisateur_role" database/migrations/006_auth_identity.sql
grep -q "ck_utilisateur_business_identity" database/migrations/006_auth_identity.sql
grep -q "ck_utilisateur_password_hash_non_empty" database/migrations/006_auth_identity.sql
grep -q "ck_utilisateur_email_basic" database/migrations/006_auth_identity.sql
grep -q "uq_utilisateur_email_lower" database/migrations/006_auth_identity.sql
grep -q "uq_utilisateur_client" database/migrations/006_auth_identity.sql
grep -q "uq_utilisateur_chasseur" database/migrations/006_auth_identity.sql
grep -q "'006'" database/migrations/006_auth_identity.sql
grep -q "migration_control.schema_version" database/migrations/006_auth_identity.sql
grep -q "^COMMIT;" database/migrations/006_auth_identity.sql
grep -q "CREATE TABLE real_estate.demande_affectation" database/migrations/007_demande_chasseur_affectation.sql
grep -q "ck_demande_affectation_statut" database/migrations/007_demande_chasseur_affectation.sql
grep -q "ck_demande_affectation_decision" database/migrations/007_demande_chasseur_affectation.sql
grep -q "ck_demande_affectation_motif_refus" database/migrations/007_demande_chasseur_affectation.sql
grep -q "ck_demande_affectation_dates" database/migrations/007_demande_chasseur_affectation.sql
grep -q "uq_demande_affectation_current" database/migrations/007_demande_chasseur_affectation.sql
grep -q "'ASSIGNEE'" database/migrations/007_demande_chasseur_affectation.sql
grep -q "'ACCEPTEE'" database/migrations/007_demande_chasseur_affectation.sql
grep -q "'REFUSEE'" database/migrations/007_demande_chasseur_affectation.sql
grep -q "'007'" database/migrations/007_demande_chasseur_affectation.sql
grep -q "migration_control.schema_version" database/migrations/007_demande_chasseur_affectation.sql
grep -q "^COMMIT;" database/migrations/007_demande_chasseur_affectation.sql
grep -q "CREATE TABLE real_estate.mandat_periode" database/migrations/008_mandat_lifecycle.sql
grep -q "ck_mandat_periode_duree" database/migrations/008_mandat_lifecycle.sql
grep -q "uq_mandat_periode_initial" database/migrations/008_mandat_lifecycle.sql
grep -q "trg_validate_mandat_periode_insert" database/migrations/008_mandat_lifecycle.sql
grep -q "trg_prevent_mandat_periode_update" database/migrations/008_mandat_lifecycle.sql
grep -q "trg_prevent_mandat_periode_overlap" database/migrations/008_mandat_lifecycle.sql
grep -q "'INITIAL'" database/migrations/008_mandat_lifecycle.sql
grep -q "'RENOUVELLEMENT'" database/migrations/008_mandat_lifecycle.sql
grep -q "'008'" database/migrations/008_mandat_lifecycle.sql
grep -q "migration_control.schema_version" database/migrations/008_mandat_lifecycle.sql
grep -q "^COMMIT;" database/migrations/008_mandat_lifecycle.sql
grep -q "CREATE TABLE warehouse.fact_mandat_periode" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "id_mandat_periode_source" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "mandat_fact_key" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "fk_fact_mandat_periode_mandat" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "fk_fact_mandat_periode_date_debut" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "fk_fact_mandat_periode_date_fin" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "fk_fact_mandat_periode_date_renouvellement" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "uq_fact_mandat_periode_source" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "uq_fact_mandat_periode_numero" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "ck_fact_mandat_periode_type" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "real_estate.mandat_periode" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "warehouse.fact_mandat" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "'009'" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "migration_control.schema_version" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "^COMMIT;" database/migrations/009_mandat_lifecycle_warehouse.sql
grep -q "CREATE TABLE real_estate.vente" database/migrations/010_transaction_remuneration.sql
grep -q "CREATE TABLE real_estate.parametres_honoraires" database/migrations/010_transaction_remuneration.sql
grep -q "CREATE TABLE real_estate.parametres_remuneration" database/migrations/010_transaction_remuneration.sql
grep -q "CREATE TABLE real_estate.palier_performance" database/migrations/010_transaction_remuneration.sql
grep -q "id_chasseur_beneficiaire" database/migrations/010_transaction_remuneration.sql
grep -q "origine_vente" database/migrations/010_transaction_remuneration.sql
grep -q "date_acte_authentique" database/migrations/010_transaction_remuneration.sql
grep -q "montant_achat" database/migrations/010_transaction_remuneration.sql
grep -q "statut_usage" database/migrations/010_transaction_remuneration.sql
grep -q "'HISTORIQUE'" database/migrations/010_transaction_remuneration.sql
grep -q "'APPROUVE'" database/migrations/010_transaction_remuneration.sql
grep -q "prevent_parametres_honoraires_overlap" database/migrations/010_transaction_remuneration.sql
grep -q "prevent_parametres_remuneration_overlap" database/migrations/010_transaction_remuneration.sql
grep -q "prevent_bareme_commission_overlap" database/migrations/010_transaction_remuneration.sql
grep -q "score_performance" database/migrations/010_transaction_remuneration.sql
grep -q "taux_base" database/migrations/010_transaction_remuneration.sql
grep -q "majoration_anciennete" database/migrations/010_transaction_remuneration.sql
grep -q "modulation_performance" database/migrations/010_transaction_remuneration.sql
grep -q "taux_final" database/migrations/010_transaction_remuneration.sql
grep -q "'010'" database/migrations/010_transaction_remuneration.sql
grep -q "migration_control.schema_version" database/migrations/010_transaction_remuneration.sql
grep -q "^COMMIT;" database/migrations/010_transaction_remuneration.sql
grep -q "Migration 011" database/migrations/011_initial_remuneration_configuration.sql
grep -q "3000.00" database/migrations/011_initial_remuneration_configuration.sql
grep -q "0.025000" database/migrations/011_initial_remuneration_configuration.sql
grep -q "DELAI_SEMAINES" database/migrations/011_initial_remuneration_configuration.sql
grep -q "VISITES" database/migrations/011_initial_remuneration_configuration.sql
grep -q "'APPROUVE'" database/migrations/011_initial_remuneration_configuration.sql
grep -q "'011'" database/migrations/011_initial_remuneration_configuration.sql
grep -q "migration_control.schema_version" database/migrations/011_initial_remuneration_configuration.sql
grep -q "^COMMIT;" database/migrations/011_initial_remuneration_configuration.sql
grep -q "Migration 012" database/migrations/012_chasseur_entry_date_backfill.sql
grep -q "Fil_Rouge_Depart" database/migrations/012_chasseur_entry_date_backfill.sql
grep -q "MIN(m.date_debut)" database/migrations/012_chasseur_entry_date_backfill.sql
grep -q "real_estate.audit_log" database/migrations/012_chasseur_entry_date_backfill.sql
grep -q "certified_hr_entry_date" database/migrations/012_chasseur_entry_date_backfill.sql
grep -q "EARLIEST_KNOWN_LEGACY_BUSINESS_ACTIVITY" database/migrations/012_chasseur_entry_date_backfill.sql
grep -q "'012'" database/migrations/012_chasseur_entry_date_backfill.sql
grep -q "migration_control.schema_version" database/migrations/012_chasseur_entry_date_backfill.sql
grep -q "^COMMIT;" database/migrations/012_chasseur_entry_date_backfill.sql
grep -q "ADD COLUMN id_client BIGINT" database/migrations/013_demande_client_ownership.sql
grep -q "fk_demande_client" database/migrations/013_demande_client_ownership.sql
grep -q "ck_demande_client_owner" database/migrations/013_demande_client_ownership.sql
grep -q "idx_demande_client" database/migrations/013_demande_client_ownership.sql
grep -q "validate_demande_mandat_client" database/migrations/013_demande_client_ownership.sql
grep -q "trg_demande_mandat_client" database/migrations/013_demande_client_ownership.sql
grep -q "d.origine = 'LEGACY'" database/migrations/013_demande_client_ownership.sql
grep -q "'GENERATED'" database/migrations/013_demande_client_ownership.sql
grep -q "'013'" database/migrations/013_demande_client_ownership.sql
grep -q "migration_control.schema_version" database/migrations/013_demande_client_ownership.sql
grep -q "^COMMIT;" database/migrations/013_demande_client_ownership.sql
grep -q '^DROP SCHEMA IF EXISTS "Fil_Rouge_Depart" CASCADE;' database/legacy/PgSQL.sql
grep -q "OLTP constraints enforced successfully" database/tests/003_oltp_constraints.sql
grep -q "real_estate.visite" database/tests/008_visite_audit.sql
grep -q "real_estate.audit_log" database/tests/008_visite_audit.sql
grep -q "authentication identity schema validation completed successfully" database/tests/009_auth_identity.sql
grep -q "real_estate.utilisateur" database/tests/009_auth_identity.sql
grep -q "Demande assignment constraints and lifecycle validated successfully" database/tests/010_demande_affectation.sql
grep -q "real_estate.demande_affectation" database/tests/010_demande_affectation.sql
grep -q "uq_demande_affectation_current" database/migrations/007_demande_chasseur_affectation.sql
grep -q "Mandat lifecycle constraints validated" database/tests/011_mandat_lifecycle.sql
grep -q "real_estate.mandat_periode" database/tests/011_mandat_lifecycle.sql
grep -q "RENOUVELLEMENT" database/tests/011_mandat_lifecycle.sql
grep -q "warehouse.fact_mandat_periode" database/tests/012_mandat_lifecycle_warehouse.sql
grep -q "migration 009 registered" database/tests/012_mandat_lifecycle_warehouse.sql
grep -q "id_mandat_periode_source" database/tests/012_mandat_lifecycle_warehouse.sql
grep -q "RENOUVELLEMENT" database/tests/012_mandat_lifecycle_warehouse.sql
grep -q "ROLLBACK;" database/tests/012_mandat_lifecycle_warehouse.sql
grep -q "real_estate.vente" database/tests/013_transaction_remuneration.sql
grep -q "real_estate.parametres_honoraires" database/tests/013_transaction_remuneration.sql
grep -q "real_estate.parametres_remuneration" database/tests/013_transaction_remuneration.sql
grep -q "real_estate.palier_performance" database/tests/013_transaction_remuneration.sql
grep -q "statut_usage" database/tests/013_transaction_remuneration.sql
grep -q "droit_remuneration" database/tests/013_transaction_remuneration.sql
grep -q "score_performance" database/tests/013_transaction_remuneration.sql
grep -q "ROLLBACK;" database/tests/013_transaction_remuneration.sql
grep -q "Migration 011" database/tests/014_remuneration_configuration.sql
grep -q "real_estate.parametres_honoraires" database/tests/014_remuneration_configuration.sql
grep -q "real_estate.parametres_remuneration" database/tests/014_remuneration_configuration.sql
grep -q "real_estate.palier_performance" database/tests/014_remuneration_configuration.sql
grep -q "13500.00" database/tests/014_remuneration_configuration.sql
grep -q "ROLLBACK;" database/tests/014_remuneration_configuration.sql
grep -q "Test 015" database/tests/015_chasseur_entry_date_backfill.sql
grep -q "Fil_Rouge_Depart" database/tests/015_chasseur_entry_date_backfill.sql
grep -q "date_entree" database/tests/015_chasseur_entry_date_backfill.sql
grep -q "migration_012" database/tests/015_chasseur_entry_date_backfill.sql
grep -q "certified_hr_entry_date" database/tests/015_chasseur_entry_date_backfill.sql
grep -q "PASS:" database/tests/015_chasseur_entry_date_backfill.sql
grep -q "Test 016" database/tests/016_demande_client_ownership.sql
grep -q "migration 013" database/tests/016_demande_client_ownership.sql
grep -q "fk_demande_client" database/tests/016_demande_client_ownership.sql
grep -q "ck_demande_client_owner" database/tests/016_demande_client_ownership.sql
grep -q "trg_demande_mandat_client" database/tests/016_demande_client_ownership.sql
grep -q "idx_demande_client" database/tests/016_demande_client_ownership.sql
grep -q "PASS:" database/tests/016_demande_client_ownership.sql
grep -q "Current workload by chasseur" database/oltp/001_operational_queries.sql
grep -q "EXPLAIN (" database/oltp/002_explain_analyze.sql
grep -q "CREATE SCHEMA IF NOT EXISTS raw;" database/oltp/003_raw_ingestion_schema.sql
grep -q "CREATE SCHEMA IF NOT EXISTS staging;" database/oltp/004_staging_schema.sql
grep -q "CREATE TABLE IF NOT EXISTS staging.annonces" database/oltp/004_staging_schema.sql
