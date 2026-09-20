#!/bin/sh
# pra:publish-gitops / prepare-gitops. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "GITOPS CREDENTIAL VALIDATION"
echo "============================================================"

kubectl \
  -n openmetadata \
  get secret \
  lab-gitops-git-credentials
rm -rf "$GITOPS_WORKDIR"
rm -f "$PRA_RENDERED_PATH"
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

echo
echo "GitOps credentials loaded."
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

test "$(
  git -C "$GITOPS_WORKDIR" branch --show-current
)" = "$GITOPS_BRANCH"
test -d "$GITOPS_WORKDIR/apps"
test -d "$GITOPS_WORKDIR/workloads"

echo
echo "GitOps structure validated:"
echo "  $GITOPS_WORKDIR/apps"
echo "  $GITOPS_WORKDIR/workloads"
