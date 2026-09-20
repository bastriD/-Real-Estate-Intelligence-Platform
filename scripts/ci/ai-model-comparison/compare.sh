#!/bin/sh
# ai-model-comparison:compare / script. Sourced by GitLab; run from the project checkout.

echo "=============================================="
echo "AI Model Comparison"
echo "=============================================="
echo
echo "Commit:   ${CI_COMMIT_SHA}"
echo "Pipeline: ${CI_PIPELINE_ID}"
echo "Job:      ${CI_JOB_ID}"
echo "Image:    ${AI_MLOPS_IMAGE}"
echo
test -f "${COMPARISON_MANIFEST}" || {
  echo "Missing Kubernetes manifest: ${COMPARISON_MANIFEST}"
  exit 1
}
test -f src/ai/matching/model_comparison.py || {
  echo "Missing model comparison module"
  exit 1
}
test -f src/ai/matching/run_model_comparison.py || {
  echo "Missing model comparison runtime runner"
  exit 1
}
kubectl -n "${KUBERNETES_NAMESPACE}" \
  get secret real-estate-postgresql-secret
kubectl -n "${KUBERNETES_NAMESPACE}" \
  get secret gitlab-registry-auth
cp "${COMPARISON_MANIFEST}" ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__AI_MLOPS_IMAGE__|${AI_MLOPS_IMAGE}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_COMMIT_SHA__|${CI_COMMIT_SHA}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_COMMIT_SHORT_SHA__|${CI_COMMIT_SHORT_SHA}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_COMMIT_BRANCH__|${CI_COMMIT_BRANCH:-}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_COMMIT_REF_NAME__|${CI_COMMIT_REF_NAME}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_PROJECT_URL__|${CI_PROJECT_URL}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_PROJECT_PATH__|${CI_PROJECT_PATH}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_PIPELINE_ID__|${CI_PIPELINE_ID}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_PIPELINE_URL__|${CI_PIPELINE_URL}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_JOB_ID__|${CI_JOB_ID}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_JOB_NAME__|${CI_JOB_NAME}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
sed -i \
  "s|__CI_JOB_URL__|${CI_JOB_URL}|g" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
kubectl apply \
  --dry-run=client \
  -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
kubectl -n "${KUBERNETES_NAMESPACE}" \
  delete job "${COMPARISON_JOB_NAME}" \
  --ignore-not-found=true
kubectl apply \
  -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/matching-model-comparison-job.yaml
kubectl -n "${KUBERNETES_NAMESPACE}" \
  wait \
  --for=condition=complete \
  "job/${COMPARISON_JOB_NAME}" \
  --timeout=300s
kubectl -n "${KUBERNETES_NAMESPACE}" \
  logs \
  "job/${COMPARISON_JOB_NAME}"
echo
echo "=============================================="
echo "Kubernetes Job Summary"
echo "=============================================="

kubectl -n "${KUBERNETES_NAMESPACE}" \
  get job "${COMPARISON_JOB_NAME}" \
  -o wide
