#!/bin/sh
# database:migrate-011 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql
MIGRATION_010_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '010'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_010_APPLIED" != "yes" ]; then
  echo "ERROR: migration 010 must be applied before migration 011."
  exit 1
fi
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

if [ "$MIGRATION_011_APPLIED" = "yes" ]; then
  echo "Migration 011 already applied - skipping safely."
  exit 0
fi
echo "Applying migration 011..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/011_initial_remuneration_configuration.sql
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
      WHERE version = '011';
    "
echo "Verifying approved remuneration configuration..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        'parametres_honoraires' AS configuration,
        COUNT(*) AS total,
        COUNT(*) FILTER (WHERE actif = TRUE) AS actifs
      FROM real_estate.parametres_honoraires

      UNION ALL

      SELECT
        'parametres_remuneration',
        COUNT(*),
        COUNT(*) FILTER (WHERE actif = TRUE)
      FROM real_estate.parametres_remuneration

      UNION ALL

      SELECT
        'bareme_approved_default',
        COUNT(*),
        COUNT(*) FILTER (
          WHERE actif = TRUE
            AND statut_usage = 'APPROUVE'
            AND id_chasseur IS NULL
        )
      FROM real_estate.bareme_commission;
    "
INVALID_LEGACY_ROWS="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM real_estate.bareme_commission
       WHERE id_chasseur IS NOT NULL
         AND statut_usage <> 'HISTORIQUE';"
)"

echo "Invalid legacy commission rows: ${INVALID_LEGACY_ROWS}"

if [ "${INVALID_LEGACY_ROWS}" != "0" ]; then
  echo "ERROR: hunter-specific legacy commission rows changed operational status."
  exit 1
fi
echo "============================================================"
echo "MIGRATION 011 SUCCESSFULLY APPLIED"
echo "============================================================"
