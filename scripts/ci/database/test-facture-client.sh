#!/bin/sh
# database:test-facture-client. SQL test enforces registry prerequisites and rolls back.

kubectl -n real-estate get deploy real-estate-postgresql
kubectl -n real-estate exec deploy/real-estate-postgresql -i -- \
  psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 \
  < database/tests/018_facture_client.sql

echo "Client invoice database tests successful (test business data rolled back)."
