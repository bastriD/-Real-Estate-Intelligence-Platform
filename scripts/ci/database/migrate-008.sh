#!/bin/sh
# database:migrate-008 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql
echo "Checking migration 008 prerequisites..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.mandat') AS mandat,
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

if [ "$MIGRATION_008_APPLIED" = "yes" ]; then
  echo "Migration 008 already applied - skipping safely."
  exit 0
fi
echo "Applying migration 008..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/008_mandat_lifecycle.sql
echo "Verifying Mandat lifecycle schema..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.mandat_periode') AS mandat_periode,
        to_regclass('real_estate.uq_mandat_periode_initial') AS initial_period_index;

      SELECT
        tgname AS trigger_name
      FROM pg_trigger
      WHERE tgrelid = 'real_estate.mandat_periode'::regclass
        AND NOT tgisinternal
      ORDER BY tgname;
    "
echo "Checking Mandat period backfill..."

BACKFILL_MISMATCH_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM real_estate.mandat m
       LEFT JOIN real_estate.mandat_periode mp
         ON mp.id_mandat = m.id_mandat
        AND mp.numero_periode = 1
        AND mp.type_periode = 'INITIAL'
       WHERE mp.id_mandat_periode IS NULL
          OR mp.date_debut <> m.date_debut
          OR mp.date_fin <> m.date_fin;"
)"

echo "Mandat lifecycle backfill mismatches: ${BACKFILL_MISMATCH_COUNT}"

if [ "${BACKFILL_MISMATCH_COUNT}" != "0" ]; then
  echo "ERROR: Mandat lifecycle backfill verification failed."
  exit 1
fi
echo "Checking INITIAL period cardinality..."

INITIAL_CARDINALITY_ERRORS="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM (
         SELECT
           m.id_mandat,
           COUNT(mp.id_mandat_periode) AS initial_count
         FROM real_estate.mandat m
         LEFT JOIN real_estate.mandat_periode mp
           ON mp.id_mandat = m.id_mandat
          AND mp.type_periode = 'INITIAL'
         GROUP BY m.id_mandat
         HAVING COUNT(mp.id_mandat_periode) <> 1
       ) invalid_mandats;"
)"

echo "Mandats with invalid INITIAL period count: ${INITIAL_CARDINALITY_ERRORS}"

if [ "${INITIAL_CARDINALITY_ERRORS}" != "0" ]; then
  echo "ERROR: invalid INITIAL period cardinality detected."
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
      WHERE version = '008';

      SELECT
        type_periode,
        est_historique_legacy,
        COUNT(*) AS periodes
      FROM real_estate.mandat_periode
      GROUP BY
        type_periode,
        est_historique_legacy
      ORDER BY
        type_periode,
        est_historique_legacy;
    "
echo "============================================================"
echo "MIGRATION 008 SUCCESSFULLY APPLIED"
echo "============================================================"
