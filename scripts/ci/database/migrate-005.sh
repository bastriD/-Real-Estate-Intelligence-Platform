#!/bin/sh
# database:migrate-005 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql
echo "Checking migration 005 prerequisites..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.demande') AS demande,
        to_regclass('real_estate.demande_version') AS demande_version,
        to_regclass('migration_control.schema_version') AS schema_version;
    "
MIGRATION_005_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '005'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_005_APPLIED" = "yes" ]; then
  echo "Migration 005 already applied - skipping safely."
  exit 0
fi
echo "Applying migration 005..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/005_demande_pre_mandat.sql
echo "Verifying pre-mandate DEMANDE support..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        table_schema,
        table_name,
        column_name,
        is_nullable
      FROM information_schema.columns
      WHERE table_schema = 'real_estate'
        AND table_name = 'demande'
        AND column_name = 'id_mandat';
    "
echo "Verifying migration 005 columns..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        table_name,
        column_name,
        data_type,
        is_nullable
      FROM information_schema.columns
      WHERE table_schema = 'real_estate'
        AND (
          (
            table_name = 'demande'
            AND column_name = 'origine'
          )
          OR
          (
            table_name = 'demande_version'
            AND column_name IN (
              'source_recherche_ref',
              'ingestion_batch'
            )
          )
        )
      ORDER BY table_name, column_name;
    "
echo "Checking legacy demande integrity..."

LEGACY_WITHOUT_MANDATE="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM real_estate.demande
       WHERE origine = 'LEGACY'
         AND id_mandat IS NULL;"
)"

echo "Legacy demandes without mandate: ${LEGACY_WITHOUT_MANDATE}"

if [ "${LEGACY_WITHOUT_MANDATE}" != "0" ]; then
  echo "ERROR: legacy demandes lost their mandate relationship."
  exit 1
fi
echo "Verifying migration registry..."

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
      WHERE version = '005';
    "
echo "============================================================"
echo "MIGRATION 005 SUCCESSFULLY APPLIED"
echo "============================================================"

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        COUNT(*) AS demandes_total,
        COUNT(*) FILTER (
          WHERE origine = 'LEGACY'
        ) AS legacy_demandes,
        COUNT(*) FILTER (
          WHERE origine = 'GENERATED'
        ) AS generated_demandes,
        COUNT(*) FILTER (
          WHERE id_mandat IS NULL
        ) AS pre_mandate_demandes
      FROM real_estate.demande;
    "
