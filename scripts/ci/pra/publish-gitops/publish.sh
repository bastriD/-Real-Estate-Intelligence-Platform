#!/bin/sh
# pra:publish-gitops / publish. Sourced by GitLab; run from the project checkout.

mkdir -p \
  "$GITOPS_WORKDIR/$GITOPS_PRA_PATH"

mkdir -p \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH"
cp \
  "$PRA_SOURCE_PATH/postgresql-backup-cronjob.yaml" \
  "$GITOPS_WORKDIR/$GITOPS_PRA_PATH/postgresql-backup-cronjob.yaml"
cp \
  "$PRA_SOURCE_PATH/kustomization.yaml" \
  "$GITOPS_WORKDIR/$GITOPS_PRA_PATH/kustomization.yaml"
cp \
  "$PRA_SOURCE_PATH/application.yaml" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"
echo
echo "============================================================"
echo "GITOPS PRA KUSTOMIZE VALIDATION"
echo "============================================================"

kubectl kustomize \
  "$GITOPS_WORKDIR/$GITOPS_PRA_PATH" \
  > "$PRA_RENDERED_PATH"

test -s "$PRA_RENDERED_PATH"

echo
echo "GitOps PRA Kustomize rendering successful."
grep \
  "kind: CronJob" \
  "$PRA_RENDERED_PATH"

grep \
  "name: ${CRONJOB_NAME}" \
  "$PRA_RENDERED_PATH"

grep \
  "name: ${POSTGRES_SECRET}" \
  "$PRA_RENDERED_PATH"

grep \
  "name: ${BACKUP_S3_SECRET}" \
  "$PRA_RENDERED_PATH"

echo
echo "Rendered GitOps PRA workload validated."
kubectl apply \
  --dry-run=client \
  -f "$PRA_RENDERED_PATH" \
  > /dev/null

echo
echo "GitOps PRA CronJob client validation successful."
grep \
  "name: real-estate-pra" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"
grep \
  "path: workloads/real-estate/pra" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"
grep \
  "repoURL: https://gitlab.local/root/lab-gitops.git" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"
grep \
  "targetRevision: main" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"

echo
echo "PRA Argo CD Application validated."
kubectl apply \
  --dry-run=client \
  -f "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml" \
  > /dev/null

echo
echo "PRA Argo CD Application client validation successful."
echo
echo "============================================================"
echo "PRA GITOPS DESIRED STATE"
echo "============================================================"

echo
echo "Workload directory:"
echo "$GITOPS_PRA_PATH"

echo
echo "Application directory:"
echo "$GITOPS_APP_PATH"

echo
echo "Files:"

find \
  "$GITOPS_WORKDIR/$GITOPS_PRA_PATH" \
  -maxdepth 1 \
  -type f \
  -print

find \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH" \
  -maxdepth 1 \
  -type f \
  -print
git -C "$GITOPS_WORKDIR" config \
  user.name \
  "chasse-immobiliere-ci"

git -C "$GITOPS_WORKDIR" config \
  user.email \
  "gitlab-ci@lab.local"
git -C "$GITOPS_WORKDIR" add \
  "$GITOPS_PRA_PATH" \
  "$GITOPS_APP_PATH"

echo
echo "GitOps staged PRA changes:"

git -C "$GITOPS_WORKDIR" status \
  --short
if git -C "$GITOPS_WORKDIR" diff --cached --quiet; then

  echo
  echo "No PRA GitOps changes detected."

else

  echo
  echo "Creating PRA GitOps commit..."

  git -C "$GITOPS_WORKDIR" commit \
    -m "deploy: publish real-estate postgresql PRA backup ${CI_COMMIT_SHORT_SHA}"

  echo
  echo "Pushing PRA GitOps desired state..."

  GIT_SSL_NO_VERIFY=true \
  git -C "$GITOPS_WORKDIR" push \
    origin \
    "$GITOPS_BRANCH"

  echo
  echo "PRA GitOps publication completed."

fi
