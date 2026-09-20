#!/bin/sh
# observability:provision-grafana-datasource / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
test -f deploy/observability/grafana-datasource.yaml.template
export POSTGRES_DB="$(
  kubectl -n real-estate get secret \
    real-estate-postgresql-secret \
    -o jsonpath='{.data.POSTGRES_DB}' \
  | base64 -d
)"

export POSTGRES_HOST="$(
  kubectl -n real-estate get secret \
    real-estate-postgresql-secret \
    -o jsonpath='{.data.POSTGRES_HOST}' \
  | base64 -d
)"

export POSTGRES_PORT="$(
  kubectl -n real-estate get secret \
    real-estate-postgresql-secret \
    -o jsonpath='{.data.POSTGRES_PORT}' \
  | base64 -d
)"

export POSTGRES_USER="$(
  kubectl -n real-estate get secret \
    real-estate-postgresql-secret \
    -o jsonpath='{.data.POSTGRES_USER}' \
  | base64 -d
)"

export POSTGRES_PASSWORD="$(
  kubectl -n real-estate get secret \
    real-estate-postgresql-secret \
    -o jsonpath='{.data.POSTGRES_PASSWORD}' \
  | base64 -d
)"

test -n "${POSTGRES_DB}"
test -n "${POSTGRES_HOST}"
test -n "${POSTGRES_PORT}"
test -n "${POSTGRES_USER}"
test -n "${POSTGRES_PASSWORD}"

envsubst \
  < deploy/observability/grafana-datasource.yaml.template \
  > ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-grafana-datasource.yaml

echo "Grafana datasource template rendered successfully."
kubectl -n monitoring create secret generic \
  real-estate-grafana-datasource \
  --from-file=datasource.yaml=${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-grafana-datasource.yaml \
  --dry-run=client \
  -o yaml \
| kubectl apply -f -
kubectl -n monitoring label secret \
  real-estate-grafana-datasource \
  grafana_datasource=1 \
  --overwrite
kubectl -n monitoring get secret \
  real-estate-grafana-datasource \
  -o custom-columns='NAME:.metadata.name,LABEL:.metadata.labels.grafana_datasource,TYPE:.type'
