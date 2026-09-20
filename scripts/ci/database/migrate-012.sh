#!/bin/sh
# database:migrate-012 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql
MIGRATION_011_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '011'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_011_APPLIED" != "yes" ]; then
  echo "ERROR: migration 011 must be applied before migration 012."
  exit 1
fi
echo "Checking migration 012 prerequisites..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.chasseur') AS chasseur,
        to_regclass('real_estate.audit_log') AS audit_log,
        to_regclass('\"Fil_Rouge_Depart\".mandats') AS legacy_mandats,
        to_regclass('migration_control.schema_version') AS schema_version;
    "
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

if [ "$MIGRATION_012_APPLIED" = "yes" ]; then
  echo "Migration 012 already applied - skipping safely."
  exit 0
fi
echo "Previewing hunter entry-date reconstruction..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        c.id_chasseur,
        c.nom,
        c.prenom,
        c.date_entree AS current_date_entree,
        MIN(m.date_debut) AS reconstructed_date_entree,
        COUNT(*) AS legacy_mandates
      FROM real_estate.chasseur c
      JOIN \"Fil_Rouge_Depart\".mandats m
        ON m.chasseur_id = c.id_chasseur
      WHERE c.date_entree IS NULL
        AND m.date_debut IS NOT NULL
      GROUP BY
        c.id_chasseur,
        c.nom,
        c.prenom,
        c.date_entree
      ORDER BY c.id_chasseur;
    "
echo "Applying migration 012..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/012_chasseur_entry_date_backfill.sql
echo "Verifying hunter entry dates..."

REMAINING_NULLS="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM real_estate.chasseur c
       WHERE c.date_entree IS NULL
         AND EXISTS (
           SELECT 1
           FROM \"Fil_Rouge_Depart\".mandats m
           WHERE m.chasseur_id = c.id_chasseur
             AND m.date_debut IS NOT NULL
         );"
)"

echo "Hunters with usable legacy history still missing date_entree: ${REMAINING_NULLS}"

if [ "${REMAINING_NULLS}" != "0" ]; then
  echo "ERROR: hunter date_entree reconstruction incomplete."
  exit 1
fi
RECONSTRUCTION_MISMATCHES="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "WITH expected AS (
         SELECT
           chasseur_id,
           MIN(date_debut) AS expected_date
         FROM \"Fil_Rouge_Depart\".mandats
         WHERE chasseur_id IS NOT NULL
           AND date_debut IS NOT NULL
         GROUP BY chasseur_id
       )
       SELECT COUNT(*)
       FROM expected e
       JOIN real_estate.chasseur c
         ON c.id_chasseur = e.chasseur_id
       WHERE c.date_entree IS DISTINCT FROM e.expected_date;"
)"

echo "Hunter entry-date reconstruction mismatches: ${RECONSTRUCTION_MISMATCHES}"

if [ "${RECONSTRUCTION_MISMATCHES}" != "0" ]; then
  echo "ERROR: reconstructed hunter entry dates differ from legacy source."
  exit 1
fi
echo "Verifying migration 012 audit provenance..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        record_id AS id_chasseur,
        ancienne_valeur,
        nouvelle_valeur,
        contexte ->> 'value_nature' AS value_nature,
        contexte ->> 'certified_hr_entry_date' AS certified_hr_entry_date
      FROM real_estate.audit_log
      WHERE utilisateur = 'migration_012'
        AND schema_name = 'real_estate'
        AND table_name = 'chasseur'
        AND contexte ->> 'migration' = '012'
      ORDER BY record_id::BIGINT;
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
      WHERE version = '012';
    "
echo "============================================================"
echo "MIGRATION 012 SUCCESSFULLY APPLIED"
echo "============================================================"
