#!/bin/sh
# backend:publish-gitops / publish. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "BACKEND GITOPS DESIRED STATE"
echo "============================================================"

echo
echo "Workload directory:"
echo "$GITOPS_BACKEND_PATH"

echo
echo "Application directory:"
echo "$GITOPS_APP_PATH"

echo
echo "Files:"

find "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH" \
  -maxdepth 1 \
  -type f \
  -print

find "$GITOPS_WORKDIR/$GITOPS_APP_PATH" \
  -maxdepth 1 \
  -type f \
  -print
echo
echo "Backend Deployment image:"

grep \
  "image:" \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/deployment.yaml"
git -C "$GITOPS_WORKDIR" config \
  user.name \
  "chasse-immobiliere-ci"

git -C "$GITOPS_WORKDIR" config \
  user.email \
  "gitlab-ci@lab.local"
git -C "$GITOPS_WORKDIR" add \
  "$GITOPS_BACKEND_PATH" \
  "$GITOPS_APP_PATH"

echo
echo "GitOps staged changes:"

git -C "$GITOPS_WORKDIR" status \
  --short
if git -C "$GITOPS_WORKDIR" diff --cached --quiet; then

  echo
  echo "No Backend GitOps changes detected."

else

  echo
  echo "Creating Backend GitOps commit..."

  git -C "$GITOPS_WORKDIR" commit \
    -m "deploy: publish real-estate backend ${CI_COMMIT_SHORT_SHA}"

  echo
  echo "Pushing Backend GitOps commit to main..."

  GIT_SSL_NO_VERIFY=true \
  git -C "$GITOPS_WORKDIR" push \
    origin \
    "$GITOPS_BRANCH"

  echo
  echo "Backend GitOps publication completed."

fi
echo
echo "============================================================"
echo "BACKEND + AI MATCHING PUBLICATION SUMMARY"
echo "============================================================"

echo
echo "Application source repository:"
echo "$CI_PROJECT_DIR"

echo
echo "Backend source manifests:"
echo "$BACKEND_SOURCE_PATH"

echo
echo "Container image:"
echo "${CI_REGISTRY_IMAGE}/backend:${CI_COMMIT_SHORT_SHA}"

echo
echo "Backend capabilities:"
echo "- Authentication / RBAC"
echo "- Ownership enforcement"
echo "- Mandat lifecycle"
echo "- Vente transaction lifecycle"
echo "- Remuneration calculation and persistence"
echo "- Remuneration API"
echo "- Payment lifecycle"
echo "- Payment transition API"

echo
echo "AI runtime:"
echo "src/ai deterministic matching packaged in Backend image"

echo
echo "Training runtime:"
echo "requirements-ai-training.txt intentionally excluded from Backend image"

echo
echo "Registry pull Secret:"
echo "real-estate/${REGISTRY_PULL_SECRET}"

echo
echo "GitOps repository:"
echo "$GITOPS_REPOSITORY"

echo
echo "GitOps branch:"
echo "$GITOPS_BRANCH"

echo
echo "GitOps workload:"
echo "$GITOPS_BACKEND_PATH"

echo
echo "Argo CD Application:"
echo "$GITOPS_APP_PATH"

echo
echo "Argo root discovery:"
echo "apps/ -> recursive directory discovery"

echo
echo "Permanent deployment:"
echo "GitOps / Argo CD"
