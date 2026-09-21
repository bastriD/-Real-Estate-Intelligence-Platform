#!/bin/sh
# Existing manual SQL validation path; all test business mutations roll back.
kubectl -n real-estate get deploy real-estate-postgresql
kubectl -n real-estate exec deploy/real-estate-postgresql -i -- \
  psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 \
  < database/tests/019_facture_chasseur.sql
echo "Hunter invoice database tests successful (test business data rolled back)."
