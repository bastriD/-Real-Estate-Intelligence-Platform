#!/bin/sh
# backend:publish-gitops / prepare. Sourced by GitLab; run from the project checkout.

git --version
kubectl version --client
echo
echo "============================================================"
echo "BACKEND SOURCE VALIDATION"
echo "============================================================"

echo
echo "CI project directory:"
echo "$CI_PROJECT_DIR"

echo
echo "Backend source path:"
echo "$BACKEND_SOURCE_PATH"

test -d "$BACKEND_SOURCE_PATH"

test -f "$BACKEND_SOURCE_PATH/deployment.yaml"
test -f "$BACKEND_SOURCE_PATH/service.yaml"
test -f "$BACKEND_SOURCE_PATH/servicemonitor.yaml"
test -f "$BACKEND_SOURCE_PATH/kustomization.yaml"
test -f "$BACKEND_SOURCE_PATH/application.yaml"

echo
echo "Backend source manifests found."
kubectl get namespace \
  real-estate
kubectl \
  -n real-estate \
  get secret \
  real-estate-postgresql-secret
kubectl \
  -n openmetadata \
  get secret \
  lab-gitops-git-credentials
rm -rf "$GITOPS_WORKDIR"
rm -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-backend-rendered.yaml
export LAB_GITOPS_GIT_USER="$(
  kubectl \
    -n openmetadata \
    get secret \
    lab-gitops-git-credentials \
    -o jsonpath='{.data.GIT_USERNAME}' |
  base64 -d
)"

export LAB_GITOPS_GIT_TOKEN="$(
  kubectl \
    -n openmetadata \
    get secret \
    lab-gitops-git-credentials \
    -o jsonpath='{.data.GIT_TOKEN}' |
  base64 -d
)"

test -n "$LAB_GITOPS_GIT_USER"
test -n "$LAB_GITOPS_GIT_TOKEN"

echo "GitOps/PAT credentials loaded."
kubectl \
  -n real-estate \
  create secret docker-registry \
  "$REGISTRY_PULL_SECRET" \
  --docker-server="gitlab.local:4567" \
  --docker-username="$LAB_GITOPS_GIT_USER" \
  --docker-password="$LAB_GITOPS_GIT_TOKEN" \
  --dry-run=client \
  -o yaml |
kubectl apply -f -
kubectl \
  -n real-estate \
  get secret \
  "$REGISTRY_PULL_SECRET"
grep \
  "name: ${REGISTRY_PULL_SECRET}" \
  "$BACKEND_SOURCE_PATH/deployment.yaml"
chmod +x "$CI_PROJECT_DIR/scripts/ci/git-askpass.sh"
export GIT_ASKPASS="$CI_PROJECT_DIR/scripts/ci/git-askpass.sh"
export GIT_TERMINAL_PROMPT=0
echo
echo "============================================================"
echo "CLONING LAB-GITOPS"
echo "============================================================"

GIT_SSL_NO_VERIFY=true \
git clone \
  --branch "$GITOPS_BRANCH" \
  --single-branch \
  "$GITOPS_REPOSITORY" \
  "$GITOPS_WORKDIR"
echo
echo "============================================================"
echo "GITOPS REPOSITORY DIAGNOSTICS"
echo "============================================================"

echo
echo "Current branch:"
git -C "$GITOPS_WORKDIR" branch --show-current

echo
echo "Current revision:"
git -C "$GITOPS_WORKDIR" rev-parse --short HEAD

echo
echo "Repository root:"
ls -la "$GITOPS_WORKDIR"

echo
echo "Top-level directories:"

find "$GITOPS_WORKDIR" \
  -maxdepth 1 \
  -mindepth 1 \
  -type d \
  -print

test "$(
  git -C "$GITOPS_WORKDIR" branch --show-current
)" = "$GITOPS_BRANCH"
test -d "$GITOPS_WORKDIR/apps"
test -d "$GITOPS_WORKDIR/workloads"

echo
echo "GitOps structure validated:"
echo "  $GITOPS_WORKDIR/apps"
echo "  $GITOPS_WORKDIR/workloads"
