#!/bin/sh
# database:migrate-007 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql
echo "Checking migration 007 prerequisites..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.demande') AS demande,
        to_regclass('real_estate.chasseur') AS chasseur,
        to_regclass('real_estate.utilisateur') AS utilisateur,
        to_regclass('migration_control.schema_version') AS schema_version;
    "
MIGRATION_007_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '007'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_007_APPLIED" = "yes" ]; then
  echo "Migration 007 already applied - skipping safely."
  exit 0
fi
echo "Applying migration 007..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/007_demande_chasseur_affectation.sql
echo "Verifying demande assignment schema..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.demande_affectation') AS demande_affectation,
        to_regclass('real_estate.uq_demande_affectation_current') AS current_assignment_index;
    "
echo "Checking legacy assignment reconciliation..."

LEGACY_MISMATCH_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM real_estate.demande d
       LEFT JOIN real_estate.demande_affectation da
         ON da.id_demande = d.id_demande
        AND da.statut = 'ACCEPTEE'
       LEFT JOIN real_estate.mandat m
         ON m.id_mandat = d.id_mandat
       WHERE d.origine = 'LEGACY'
         AND (
           da.id_affectation IS NULL
           OR da.id_chasseur <> m.id_chasseur
         );"
)"

echo "Legacy assignment mismatches: ${LEGACY_MISMATCH_COUNT}"

if [ "${LEGACY_MISMATCH_COUNT}" != "0" ]; then
  echo "ERROR: legacy assignment reconciliation failed."
  exit 1
fi
echo "Checking current assignment uniqueness..."

CURRENT_DUPLICATES="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM (
         SELECT id_demande
         FROM real_estate.demande_affectation
         WHERE statut IN ('ASSIGNEE', 'ACCEPTEE')
         GROUP BY id_demande
         HAVING COUNT(*) > 1
       ) duplicate_rows;"
)"

echo "Demandes with multiple current assignments: ${CURRENT_DUPLICATES}"

if [ "${CURRENT_DUPLICATES}" != "0" ]; then
  echo "ERROR: multiple current assignments detected."
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
      WHERE version = '007';

      SELECT
        statut,
        COUNT(*) AS affectations
      FROM real_estate.demande_affectation
      GROUP BY statut
      ORDER BY statut;
    "
echo "============================================================"
echo "MIGRATION 007 SUCCESSFULLY APPLIED"
echo "============================================================"
