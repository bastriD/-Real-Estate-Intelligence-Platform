#!/bin/sh
# pra:publish-gitops / validate-backup. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "PRA CRONJOB SOURCE CHECKS"
echo "============================================================"

grep \
  "name: ${POSTGRES_SECRET}" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

grep \
  "name: ${BACKUP_S3_SECRET}" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

echo
echo "Expected Secret references found."
grep \
  "name: ${CRONJOB_NAME}" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

echo
echo "CronJob name validated."
grep \
  "image: postgres:16" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

echo
echo "PostgreSQL image validated."
grep \
  "image: minio/mc:" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

echo
echo "MinIO client image validated."
echo
echo "Validating backup implementation..."

grep \
  "pg_dump" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

grep \
  "pg_restore" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

grep \
  "sha256sum" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

grep \
  "mc cp" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

grep \
  "mc stat" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

echo
echo "Backup implementation validation successful."
echo
echo "Validating CronJob schedule..."

grep \
  'schedule: "0 2 \* \* \*"' \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

echo
echo "CronJob schedule validated."
grep \
  "concurrencyPolicy: Forbid" \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml"

echo
echo "CronJob concurrency policy validated."
echo
echo "============================================================"
echo "SOURCE PRA KUSTOMIZE VALIDATION"
echo "============================================================"

rm -f "$PRA_RENDERED_PATH"

kubectl kustomize \
  "$PRA_SOURCE_PATH" \
  > "$PRA_RENDERED_PATH"

test -s "$PRA_RENDERED_PATH"

echo
echo "PRA source Kustomize rendering successful."
grep \
  "kind: CronJob" \
  "$PRA_RENDERED_PATH"

grep \
  "name: ${CRONJOB_NAME}" \
  "$PRA_RENDERED_PATH"

echo
echo "Rendered PRA CronJob validated."
kubectl apply \
  --dry-run=client \
  -f "$PRA_RENDERED_PATH" \
  > /dev/null

echo
echo "PRA workload Kubernetes validation successful."
kubectl apply \
  --dry-run=client \
  -f "$PRA_SOURCE_PATH/application.yaml" \
  > /dev/null

echo
echo "PRA Argo CD Application manifest validation successful."
