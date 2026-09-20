#!/bin/sh
# database:migrate-013 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql
MIGRATION_012_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '012'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_012_APPLIED" != "yes" ]; then
  echo "ERROR: migration 012 must be applied before migration 013."
  exit 1
fi
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

if [ "$MIGRATION_013_APPLIED" = "yes" ]; then
  echo "Migration 013 already applied - skipping safely."
  exit 0
fi
echo "Checking migration 013 runtime prerequisites..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        origine,
        COUNT(*) AS total,
        COUNT(*) FILTER (WHERE id_mandat IS NOT NULL) AS avec_mandat,
        COUNT(*) FILTER (WHERE id_mandat IS NULL) AS sans_mandat
      FROM real_estate.demande
      GROUP BY origine
      ORDER BY origine;
    "
LEGACY_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*)
       FROM real_estate.demande
       WHERE origine = 'LEGACY';"
)"

echo "Legacy demandes before migration: ${LEGACY_COUNT}"

if [ "${LEGACY_COUNT}" != "17" ]; then
  echo "ERROR: migration 013 expects exactly 17 legacy demandes."
  exit 1
fi
LEGACY_CLIENT_SOURCE_ERRORS="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*)
       FROM real_estate.demande d
       LEFT JOIN real_estate.mandat m
         ON m.id_mandat = d.id_mandat
       WHERE d.origine = 'LEGACY'
         AND (
           d.id_mandat IS NULL
           OR m.id_mandat IS NULL
           OR m.id_client IS NULL
         );"
)"

echo "Legacy ownership-source errors: ${LEGACY_CLIENT_SOURCE_ERRORS}"

if [ "${LEGACY_CLIENT_SOURCE_ERRORS}" != "0" ]; then
  echo "ERROR: legacy ownership cannot be reconstructed safely."
  exit 1
fi
echo "Applying migration 013..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/013_demande_client_ownership.sql
echo "Verifying DEMANDE client ownership..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        origine,
        COUNT(*) AS total,
        COUNT(id_client) AS avec_client,
        COUNT(*) - COUNT(id_client) AS sans_client,
        COUNT(id_mandat) AS avec_mandat
      FROM real_estate.demande
      GROUP BY origine
      ORDER BY origine;
    "
OWNERSHIP_ERRORS="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*)
       FROM real_estate.demande d
       LEFT JOIN real_estate.mandat m
         ON m.id_mandat = d.id_mandat
       WHERE
         (d.origine <> 'GENERATED' AND d.id_client IS NULL)
         OR
         (
           d.id_mandat IS NOT NULL
           AND d.id_client IS DISTINCT FROM m.id_client
         );"
)"

echo "Ownership consistency errors: ${OWNERSHIP_ERRORS}"

if [ "${OWNERSHIP_ERRORS}" != "0" ]; then
  echo "ERROR: DEMANDE client ownership verification failed."
  exit 1
fi
echo "Verifying migration 013 database objects..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.idx_demande_client') AS client_index;

      SELECT
        conname,
        contype,
        condeferrable,
        condeferred
      FROM pg_constraint
      WHERE conrelid = 'real_estate.demande'::regclass
        AND conname IN (
          'fk_demande_client',
          'ck_demande_client_owner'
        )
      ORDER BY conname;

      SELECT
        tgname,
        tgdeferrable,
        tginitdeferred
      FROM pg_trigger
      WHERE tgrelid = 'real_estate.demande'::regclass
        AND tgname = 'trg_demande_mandat_client'
        AND NOT tgisinternal;
    "
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
      WHERE version = '013';
    "
echo "============================================================"
echo "MIGRATION 013 SUCCESSFULLY APPLIED"
echo "============================================================"
