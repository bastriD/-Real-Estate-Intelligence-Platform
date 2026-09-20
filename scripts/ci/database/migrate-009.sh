#!/bin/sh
# database:migrate-009 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql
echo "Checking migration 009 prerequisites..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.mandat_periode') AS mandat_periode,
        to_regclass('warehouse.fact_mandat') AS fact_mandat,
        to_regclass('warehouse.dim_date') AS dim_date,
        to_regclass('migration_control.schema_version') AS schema_version;
    "
MIGRATION_008_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '008'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_008_APPLIED" != "yes" ]; then
  echo "ERROR: migration 008 must be applied before migration 009."
  exit 1
fi
MIGRATION_009_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '009'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_009_APPLIED" = "yes" ]; then
  echo "Migration 009 already applied - skipping safely."
  exit 0
fi
echo "Applying migration 009..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/009_mandat_lifecycle_warehouse.sql
echo "Verifying Mandat period warehouse schema..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('warehouse.fact_mandat_periode') AS fact_mandat_periode;

      SELECT
        conname AS constraint_name,
        pg_get_constraintdef(oid) AS definition
      FROM pg_constraint
      WHERE conrelid = 'warehouse.fact_mandat_periode'::regclass
      ORDER BY conname;
    "
echo "Checking Mandat period warehouse backfill..."

BACKFILL_MISMATCH_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM real_estate.mandat_periode mp
       LEFT JOIN warehouse.fact_mandat_periode fmp
         ON fmp.id_mandat_periode_source = mp.id_mandat_periode
       LEFT JOIN warehouse.fact_mandat fm
         ON fm.mandat_fact_key = fmp.mandat_fact_key
       WHERE fmp.id_mandat_periode_source IS NULL
          OR fm.id_mandat_source <> mp.id_mandat
          OR fmp.numero_periode <> mp.numero_periode
          OR fmp.type_periode <> mp.type_periode
          OR fmp.date_debut_key <> TO_CHAR(mp.date_debut, 'YYYYMMDD')::integer
          OR fmp.date_fin_key <> TO_CHAR(mp.date_fin, 'YYYYMMDD')::integer
          OR fmp.date_renouvellement_key IS DISTINCT FROM
             CASE
               WHEN mp.date_renouvellement IS NULL THEN NULL
               ELSE TO_CHAR(mp.date_renouvellement, 'YYYYMMDD')::integer
             END;"
)"

echo "Mandat warehouse backfill mismatches: ${BACKFILL_MISMATCH_COUNT}"

if [ "${BACKFILL_MISMATCH_COUNT}" != "0" ]; then
  echo "ERROR: Mandat lifecycle warehouse backfill verification failed."
  exit 1
fi
echo "Checking Mandat period warehouse cardinality..."

SOURCE_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*) FROM real_estate.mandat_periode;"
)"

WAREHOUSE_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -tAc \
      "SELECT COUNT(*) FROM warehouse.fact_mandat_periode;"
)"

echo "OLTP periods: ${SOURCE_COUNT}"
echo "Warehouse periods: ${WAREHOUSE_COUNT}"

if [ "${SOURCE_COUNT}" != "${WAREHOUSE_COUNT}" ]; then
  echo "ERROR: source and warehouse Mandat period counts differ."
  exit 1
fi
echo "Checking existing fact_mandat grain..."

FACT_MANDAT_DUPLICATES="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM (
         SELECT id_mandat_source
         FROM warehouse.fact_mandat
         GROUP BY id_mandat_source
         HAVING COUNT(*) <> 1
       ) invalid;"
)"

echo "fact_mandat duplicate source keys: ${FACT_MANDAT_DUPLICATES}"

if [ "${FACT_MANDAT_DUPLICATES}" != "0" ]; then
  echo "ERROR: fact_mandat grain changed unexpectedly."
  exit 1
fi
echo "Verifying migration 009 registry and warehouse state..."

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
      WHERE version = '009';

      SELECT
        type_periode,
        est_historique_legacy,
        COUNT(*) AS periodes
      FROM warehouse.fact_mandat_periode
      GROUP BY
        type_periode,
        est_historique_legacy
      ORDER BY
        type_periode,
        est_historique_legacy;
    "
echo "============================================================"
echo "MIGRATION 009 SUCCESSFULLY APPLIED"
echo "============================================================"
