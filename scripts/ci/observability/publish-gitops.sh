#!/bin/sh
# observability:publish-gitops / script. Sourced by GitLab; run from the project checkout.

git --version
kubectl version --client
test -f deploy/observability/application.yaml
test -f observability/grafana/dashboards/real-estate-business-platform.json
test -f observability/grafana/dashboards/real-estate-data-quality.json
test -f observability/alerts/real-estate-prometheus-rules.yaml
kubectl -n openmetadata get secret \
  lab-gitops-git-credentials
rm -rf ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-observability-gitops
rm -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-grafana-dashboard.yaml
rm -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-grafana-dashboard-labeled.yaml
rm -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-kustomization.yaml
rm -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-observability-rendered.yaml
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
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-observability-gitops
echo "Generating Grafana dashboard ConfigMap from canonical JSON files..."

kubectl create configmap \
  real-estate-grafana-dashboard \
  --namespace monitoring \
  --from-file=real-estate-platform.json=observability/grafana/dashboards/real-estate-business-platform.json \
  --from-file=real-estate-data-quality.json=observability/grafana/dashboards/real-estate-data-quality.json \
  --dry-run=client \
  -o yaml \
  > ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-grafana-dashboard.yaml
kubectl label \
  --local \
  -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-grafana-dashboard.yaml \
  grafana_dashboard=1 \
  --overwrite \
  -o yaml \
  > ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-grafana-dashboard-labeled.yaml
test -s \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-grafana-dashboard-labeled.yaml

echo "Grafana dashboard ConfigMap generated successfully."
cat > ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-kustomization.yaml <<'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - grafana-dashboard-configmap.yaml
  - prometheus-rules.yaml
EOF
test -s \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-kustomization.yaml

echo "Kustomization generated successfully."
echo "Publishing Real Estate observability workload..."

mkdir -p \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-observability-gitops/workloads/monitoring/real-estate

cp \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-grafana-dashboard-labeled.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-observability-gitops/workloads/monitoring/real-estate/grafana-dashboard-configmap.yaml

cp \
  observability/alerts/real-estate-prometheus-rules.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-observability-gitops/workloads/monitoring/real-estate/prometheus-rules.yaml

cp \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-kustomization.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-observability-gitops/workloads/monitoring/real-estate/kustomization.yaml
echo "Publishing Real Estate observability Argo CD Application..."

mkdir -p \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-observability-gitops/apps/real-estate-observability

cp \
  deploy/observability/application.yaml \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-observability-gitops/apps/real-estate-observability/application.yaml
cd ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-observability-gitops
echo "Real Estate observability workload:"

find workloads/monitoring/real-estate \
  -maxdepth 2 \
  -type f \
  | sort
echo "Real Estate observability Argo Application:"

find apps/real-estate-observability \
  -maxdepth 2 \
  -type f \
  | sort
echo "Real Estate observability kustomization:"

cat \
  workloads/monitoring/real-estate/kustomization.yaml
echo "Validating PrometheusRule manifest..."

kubectl apply \
  --dry-run=client \
  -f workloads/monitoring/real-estate/prometheus-rules.yaml
echo "Validating Grafana dashboard ConfigMap..."

kubectl apply \
  --dry-run=client \
  -f workloads/monitoring/real-estate/grafana-dashboard-configmap.yaml
echo "Validating Kustomize workload..."

kubectl kustomize \
  workloads/monitoring/real-estate \
  > ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-observability-rendered.yaml

test -s \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-observability-rendered.yaml

echo "Kustomize workload validation passed."
git config user.name "chasse-immobiliere-ci"
git config user.email "gitlab-ci@lab.local"
git add \
  workloads/monitoring/real-estate \
  apps/real-estate-observability
echo "Git status:"
git status --short
if git diff --cached --quiet; then
  echo "No observability GitOps changes to publish."
  exit 0
fi
git commit \
  -m "deploy: publish real-estate observability configuration"

GIT_SSL_NO_VERIFY=true \
git push origin main
