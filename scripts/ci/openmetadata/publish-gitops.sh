#!/bin/sh
# openmetadata:publish-gitops / script. Sourced by GitLab; run from the project checkout.

git --version
kubectl version --client
test -d deploy/openmetadata
test -f deploy/openmetadata/configmap.yaml
test -f deploy/openmetadata/cronjob.yaml
test -f deploy/openmetadata/kustomization.yaml
test -f deploy/openmetadata/dbt/cronjob.yaml
test -f deploy/openmetadata/dbt/kustomization.yaml
test -f deploy/openmetadata/governance/governance-apply-job.yaml
test -f deploy/openmetadata/governance/kustomization.yaml
: "${GOVERNANCE_IMAGE_TAG:?Missing governance image build artifact}"
echo "Using governance image tag from build artifact: ${GOVERNANCE_IMAGE_TAG}"
kubectl -n openmetadata get secret \
  lab-gitops-git-credentials
rm -rf ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops
export LAB_GITOPS_GIT_USER="$(
  kubectl -n openmetadata get secret \
    lab-gitops-git-credentials \
    -o jsonpath='{.data.GIT_USERNAME}' \
  | base64 -d
)"

export LAB_GITOPS_GIT_TOKEN="$(
  kubectl -n openmetadata get secret \
    lab-gitops-git-credentials \
    -o jsonpath='{.data.GIT_TOKEN}' \
  | base64 -d
)"

test -n "${LAB_GITOPS_GIT_USER}"
test -n "${LAB_GITOPS_GIT_TOKEN}"

chmod +x "$CI_PROJECT_DIR/scripts/ci/git-askpass.sh"
export GIT_ASKPASS="$CI_PROJECT_DIR/scripts/ci/git-askpass.sh"
export GIT_TERMINAL_PROMPT=0
echo "Cloning lab-gitops repository..."

GIT_SSL_NO_VERIFY=true \
git clone \
  "https://gitlab.local/root/lab-gitops.git" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops
echo "Publishing Real Estate PostgreSQL OpenMetadata manifests..."

mkdir -p \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata/ingestions/real-estate-postgresql

cp \
  deploy/openmetadata/configmap.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata/ingestions/real-estate-postgresql/configmap.yaml

cp \
  deploy/openmetadata/cronjob.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata/ingestions/real-estate-postgresql/cronjob.yaml

cp \
  deploy/openmetadata/kustomization.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata/ingestions/real-estate-postgresql/kustomization.yaml
echo "Publishing Real Estate dbt OpenMetadata manifests..."

mkdir -p \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata/ingestions/real-estate-dbt

cp \
  deploy/openmetadata/dbt/cronjob.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata/ingestions/real-estate-dbt/cronjob.yaml

cp \
  deploy/openmetadata/dbt/kustomization.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata/ingestions/real-estate-dbt/kustomization.yaml
echo "Publishing Real Estate Governance manifests..."

mkdir -p \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata-governance/real-estate

cp \
  deploy/openmetadata/governance/governance-apply-job.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata-governance/real-estate/governance-apply-job.yaml

cp \
  deploy/openmetadata/governance/kustomization.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata-governance/real-estate/kustomization.yaml

echo "Injecting governance image tag: ${GOVERNANCE_IMAGE_TAG}"

sed -i \
  "s/__GOVERNANCE_IMAGE_TAG__/${GOVERNANCE_IMAGE_TAG}/g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata-governance/real-estate/governance-apply-job.yaml

if grep -q '__GOVERNANCE_IMAGE_TAG__' \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata-governance/real-estate/governance-apply-job.yaml; then
  echo "ERROR: governance image placeholder was not replaced."
  exit 1
fi

echo "Published governance image reference:"
grep \
  "image:" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops/workloads/openmetadata-governance/real-estate/governance-apply-job.yaml
cd ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-lab-gitops
if ! grep -qE \
  '^[[:space:]]*-[[:space:]]*real-estate-postgresql/?[[:space:]]*$' \
  workloads/openmetadata/ingestions/kustomization.yaml; then

  echo "Adding real-estate-postgresql to parent OpenMetadata kustomization."

  printf '\n  - real-estate-postgresql\n' \
    >> workloads/openmetadata/ingestions/kustomization.yaml
else
  echo "real-estate-postgresql already present."
fi
if ! grep -qE \
  '^[[:space:]]*-[[:space:]]*real-estate-dbt/?[[:space:]]*$' \
  workloads/openmetadata/ingestions/kustomization.yaml; then

  echo "Adding real-estate-dbt to parent OpenMetadata kustomization."

  printf '\n  - real-estate-dbt\n' \
    >> workloads/openmetadata/ingestions/kustomization.yaml
else
  echo "real-estate-dbt already present."
fi
test -f workloads/openmetadata-governance/kustomization.yaml

if ! grep -qE \
  '^[[:space:]]*-[[:space:]]*real-estate/?[[:space:]]*$' \
  workloads/openmetadata-governance/kustomization.yaml; then

  echo "Adding real-estate governance to parent kustomization."

  printf '\n  - real-estate\n' \
    >> workloads/openmetadata-governance/kustomization.yaml
else
  echo "real-estate governance already present."
fi
echo "OpenMetadata ingestion files:"

find workloads/openmetadata/ingestions \
  -maxdepth 2 \
  -type f \
  | sort
echo "OpenMetadata governance files:"

find workloads/openmetadata-governance \
  -maxdepth 2 \
  -type f \
  | sort
echo "OpenMetadata ingestion parent kustomization:"
cat workloads/openmetadata/ingestions/kustomization.yaml
echo "OpenMetadata governance parent kustomization:"
cat workloads/openmetadata-governance/kustomization.yaml
git config user.name "chasse-immobiliere-ci"
git config user.email "gitlab-ci@lab.local"
git add \
  workloads/openmetadata/ingestions \
  workloads/openmetadata-governance
echo "Git status:"
git status --short
if git diff --cached --quiet; then
  echo "No OpenMetadata GitOps changes to publish."
  exit 0
fi
git commit \
  -m "deploy: publish real-estate OpenMetadata configuration and governance"

GIT_SSL_NO_VERIFY=true \
git push origin main
