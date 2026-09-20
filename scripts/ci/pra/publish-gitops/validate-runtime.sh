#!/bin/sh
# pra:publish-gitops / validate-runtime. Sourced by GitLab; run from the project checkout.

git --version
kubectl version --client
echo
echo "============================================================"
echo "PRA SOURCE VALIDATION"
echo "============================================================"

echo
echo "CI project directory:"
echo "$CI_PROJECT_DIR"

echo
echo "PRA source path:"
echo "$PRA_SOURCE_PATH"

test -d "$PRA_SOURCE_PATH"

test -f "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"
test -f "$PRA_SOURCE_PATH/kustomization.yaml"
test -f "$PRA_SOURCE_PATH/application.yaml"

echo
echo "PRA source manifests found."

find "$PRA_SOURCE_PATH" \
  -maxdepth 1 \
  -type f \
  -print
echo
echo "============================================================"
echo "KUBERNETES DEPENDENCY VALIDATION"
echo "============================================================"

kubectl get namespace \
  "$K8S_NAMESPACE"
kubectl \
  -n "$K8S_NAMESPACE" \
  get secret \
  "$POSTGRES_SECRET"

echo
echo "PostgreSQL Secret exists."
kubectl \
  -n "$K8S_NAMESPACE" \
  get secret \
  "$BACKUP_S3_SECRET"

echo
echo "MinIO backup Secret exists."
echo
echo "Validating PostgreSQL Secret keys..."

for KEY in \
  POSTGRES_DB \
  POSTGRES_HOST \
  POSTGRES_PASSWORD \
  POSTGRES_PORT \
  POSTGRES_USER
do

  VALUE="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get secret \
      "$POSTGRES_SECRET" \
      -o "jsonpath={.data.${KEY}}" \
      2>/dev/null || true
  )"

  if [ -z "$VALUE" ]; then
    echo "ERROR: missing PostgreSQL Secret key: $KEY"
    exit 1
  fi

  echo " - $KEY: present"

done

echo
echo "PostgreSQL Secret key validation successful."
echo
echo "Validating backup S3 Secret keys..."

for KEY in \
  AWS_ACCESS_KEY_ID \
  AWS_ENDPOINT_URL \
  AWS_SECRET_ACCESS_KEY \
  S3_BUCKET
do

  VALUE="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get secret \
      "$BACKUP_S3_SECRET" \
      -o "jsonpath={.data.${KEY}}" \
      2>/dev/null || true
  )"

  if [ -z "$VALUE" ]; then
    echo "ERROR: missing backup S3 Secret key: $KEY"
    exit 1
  fi

  echo " - $KEY: present"

done

echo
echo "Backup S3 Secret key validation successful."
