#!/bin/sh
# database:migrate-014 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql

MIGRATION_013_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '013'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_013_APPLIED" != "yes" ]; then
  echo "ERROR: migration 013 must be applied before migration 014."
  exit 1
fi

MIGRATION_014_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '014'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_014_APPLIED" = "yes" ]; then
  echo "Migration 014 already applied - skipping safely."
  exit 0
fi

echo "Checking migration 014 runtime prerequisites..."

PRESENTATION_EXISTS="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT CASE
         WHEN to_regclass('real_estate.presentation') IS NOT NULL
         THEN 'yes'
         ELSE 'no'
       END;"
)"

if [ "$PRESENTATION_EXISTS" != "yes" ]; then
  echo "ERROR: real_estate.presentation is required by migration 014."
  exit 1
fi

OFFRE_EXISTS="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT CASE
         WHEN to_regclass('real_estate.offre') IS NOT NULL
         THEN 'yes'
         ELSE 'no'
       END;"
)"

if [ "$OFFRE_EXISTS" = "yes" ]; then
  echo "ERROR: real_estate.offre exists but migration 014 is not registered."
  exit 1
fi

PRESENTATION_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*) FROM real_estate.presentation;"
)"

echo "Presentations before migration: ${PRESENTATION_COUNT}"
echo "No historical offers will be invented or backfilled."
echo "Applying migration 014..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/014_offre_workflow.sql

echo "Verifying OFFRE database objects..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.offre') AS offre_table,
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
    "

OFFRE_COLUMN_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*)
       FROM information_schema.columns
       WHERE table_schema = 'real_estate'
         AND table_name = 'offre'
         AND column_name IN (
           'id_offre',
           'id_presentation',
           'numero_version',
           'montant',
           'date_offre',
           'date_expiration',
           'date_decision',
           'statut',
           'commentaire',
           'date_creation'
         );"
)"

echo "Expected OFFRE columns found: ${OFFRE_COLUMN_COUNT}"

if [ "$OFFRE_COLUMN_COUNT" != "10" ]; then
  echo "ERROR: OFFRE physical structure verification failed."
  exit 1
fi

OFFRE_CONSTRAINT_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*)
       FROM pg_constraint
       WHERE conrelid = 'real_estate.offre'::regclass
         AND conname IN (
           'pk_offre',
           'fk_offre_presentation',
           'uq_offre_presentation_version',
           'ck_offre_numero_version',
           'ck_offre_montant',
           'ck_offre_statut',
           'ck_offre_expiration',
           'ck_offre_decision'
         );"
)"

echo "Required OFFRE constraints found: ${OFFRE_CONSTRAINT_COUNT}"

if [ "$OFFRE_CONSTRAINT_COUNT" != "8" ]; then
  echo "ERROR: OFFRE constraint verification failed."
  exit 1
fi

OFFRE_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*) FROM real_estate.offre;"
)"

echo "Offers after migration: ${OFFRE_COUNT}"

if [ "$OFFRE_COUNT" != "0" ]; then
  echo "ERROR: migration 014 unexpectedly created historical offers."
  exit 1
fi

MIGRATION_014_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*)
       FROM migration_control.schema_version
       WHERE version = '014';"
)"

if [ "$MIGRATION_014_COUNT" != "1" ]; then
  echo "ERROR: migration 014 registry verification failed."
  exit 1
fi

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        version,
        description,
        applied_at
      FROM migration_control.schema_version
      WHERE version = '014';
    "

echo "============================================================"
echo "MIGRATION 014 SUCCESSFULLY APPLIED"
echo "============================================================"