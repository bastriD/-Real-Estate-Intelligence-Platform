#!/bin/sh
# backend:publish-gitops / render-and-validate. Sourced by GitLab; run from the project checkout.

mkdir -p \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH"

mkdir -p \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH"
cp \
  "$BACKEND_SOURCE_PATH/deployment.yaml" \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/deployment.yaml"
cp \
  "$BACKEND_SOURCE_PATH/service.yaml" \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/service.yaml"
cp \
  "$BACKEND_SOURCE_PATH/servicemonitor.yaml" \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/servicemonitor.yaml"
cp \
  "$BACKEND_SOURCE_PATH/kustomization.yaml" \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/kustomization.yaml"
cp \
  "$BACKEND_SOURCE_PATH/application.yaml" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"
echo
echo "Injecting Backend image tag:"
echo "$CI_COMMIT_SHORT_SHA"

sed -i \
  "s/__BACKEND_IMAGE_TAG__/${CI_COMMIT_SHORT_SHA}/g" \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/deployment.yaml"
if grep -q \
  "__BACKEND_IMAGE_TAG__" \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/deployment.yaml"; then

  echo
  echo "ERROR:"
  echo "Backend image placeholder remains in deployment.yaml."

  exit 1

fi

echo "Image placeholder replaced successfully."
EXPECTED_IMAGE="${CI_REGISTRY_IMAGE}/backend:${CI_COMMIT_SHORT_SHA}"

echo
echo "Expected Backend image:"
echo "$EXPECTED_IMAGE"

grep \
  "image: ${EXPECTED_IMAGE}" \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/deployment.yaml"
grep \
  "name: ${REGISTRY_PULL_SECRET}" \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/deployment.yaml"
kubectl kustomize \
  "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH" \
  > ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-backend-rendered.yaml

test -s \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-backend-rendered.yaml

echo
echo "Backend Kustomize rendering successful."
grep \
  "kind: Deployment" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-backend-rendered.yaml
grep \
  "kind: Service" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-backend-rendered.yaml
grep \
  "kind: ServiceMonitor" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-backend-rendered.yaml
grep \
  "name: real-estate-backend" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-backend-rendered.yaml
grep \
  "${CI_REGISTRY_IMAGE}/backend:${CI_COMMIT_SHORT_SHA}" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-backend-rendered.yaml
grep \
  "$REGISTRY_PULL_SECRET" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-backend-rendered.yaml
grep \
  "name: real-estate-backend" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"
grep \
  "path: workloads/real-estate/backend" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"
grep \
  "repoURL: https://gitlab.local/root/lab-gitops.git" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"
grep \
  "targetRevision: main" \
  "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml"

echo
echo "Backend Argo CD Application validation successful."
kubectl apply \
  --dry-run=client \
  -f "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/deployment.yaml" \
  > /dev/null

kubectl apply \
  --dry-run=client \
  -f "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/service.yaml" \
  > /dev/null

kubectl apply \
  --dry-run=client \
  -f "$GITOPS_WORKDIR/$GITOPS_BACKEND_PATH/servicemonitor.yaml" \
  > /dev/null

kubectl apply \
  --dry-run=client \
  -f "$GITOPS_WORKDIR/$GITOPS_APP_PATH/application.yaml" \
  > /dev/null

echo
echo "Kubernetes client-side manifest validation successful."
