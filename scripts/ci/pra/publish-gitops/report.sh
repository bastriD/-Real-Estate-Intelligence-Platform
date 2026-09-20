#!/bin/sh
# pra:publish-gitops / report. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "REAL ESTATE PCA / PRA GITOPS PUBLICATION SUMMARY"
echo "============================================================"

echo
echo "Application source repository:"
echo "$CI_PROJECT_DIR"

echo
echo "PRA source manifests:"
echo "$PRA_SOURCE_PATH"

echo
echo "GitOps repository:"
echo "$GITOPS_REPOSITORY"

echo
echo "GitOps branch:"
echo "$GITOPS_BRANCH"

echo
echo "GitOps workload:"
echo "$GITOPS_PRA_PATH"

echo
echo "Argo CD Application:"
echo "$GITOPS_APP_PATH"

echo
echo "CronJob:"
echo "$CRONJOB_NAME"

echo
echo "Backup schedule:"
echo "0 2 * * *"

echo
echo "Backup format:"
echo "PostgreSQL pg_dump custom format"

echo
echo "Backup target:"
echo "MinIO real-estate-backups/postgresql/"

echo
echo "Credential model:"
echo "Kubernetes Secrets - no credential values stored in Git"

echo
echo "Argo root discovery:"
echo "apps/ -> recursive directory discovery"

echo
echo "Deployment model:"
echo "GitLab CI -> lab-gitops -> Argo CD -> Kubernetes"

echo
echo "Argo CD reconciliation:"
echo "asynchronous - intentionally not awaited by this CI job"

echo
echo "PRA GitOps desired state published successfully."
