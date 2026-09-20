#!/bin/sh
# database:migrate-010 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql
echo "Checking migration 010 prerequisites..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.mandat') AS mandat,
        to_regclass('real_estate.mandat_periode') AS mandat_periode,
        to_regclass('real_estate.presentation') AS presentation,
        to_regclass('real_estate.bien') AS bien,
        to_regclass('real_estate.chasseur') AS chasseur,
        to_regclass('real_estate.paiement') AS paiement,
        to_regclass('real_estate.bareme_commission') AS bareme_commission,
        to_regclass('migration_control.schema_version') AS schema_version;
    "
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

if [ "$MIGRATION_009_APPLIED" != "yes" ]; then
  echo "ERROR: migration 009 must be applied before migration 010."
  exit 1
fi
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

if [ "$MIGRATION_010_APPLIED" = "yes" ]; then
  echo "Migration 010 already applied - skipping safely."
  exit 0
fi
echo "Applying migration 010..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/010_transaction_remuneration.sql
echo "Verifying transaction/remuneration schema..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.vente') AS vente,
        to_regclass('real_estate.parametres_honoraires') AS parametres_honoraires,
        to_regclass('real_estate.parametres_remuneration') AS parametres_remuneration,
        to_regclass('real_estate.palier_performance') AS palier_performance;
    "
echo "Checking legacy commission-grid classification..."

NON_HISTORICAL_LEGACY_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM real_estate.bareme_commission
       WHERE statut_usage <> 'HISTORIQUE';"
)"

echo "Existing non-historical commission rows: ${NON_HISTORICAL_LEGACY_COUNT}"

if [ "${NON_HISTORICAL_LEGACY_COUNT}" != "0" ]; then
  echo "ERROR: existing legacy commission rows were not preserved as HISTORIQUE."
  exit 1
fi
echo "Verifying frozen remuneration calculation columns..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        column_name,
        data_type,
        is_nullable
      FROM information_schema.columns
      WHERE table_schema = 'real_estate'
        AND table_name = 'paiement'
        AND column_name IN (
          'id_vente',
          'id_chasseur_beneficiaire',
          'id_parametres_honoraires',
          'id_parametres_remuneration',
          'date_calcul',
          'droit_remuneration',
          'motif_refus',
          'semaines_mandat_acte',
          'nb_visites_calcul',
          'annees_anciennete_calcul',
          'nb_ventes_fenetre',
          'nb_mandats_fenetre',
          'note_delai',
          'note_exclusivite',
          'note_ventes',
          'note_mandats',
          'note_visites',
          'score_performance',
          'taux_base',
          'majoration_anciennete',
          'modulation_performance',
          'taux_final'
        )
      ORDER BY ordinal_position;
    "
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
      WHERE version = '010';
    "
echo "============================================================"
echo "MIGRATION 010 SUCCESSFULLY APPLIED"
echo "============================================================"
