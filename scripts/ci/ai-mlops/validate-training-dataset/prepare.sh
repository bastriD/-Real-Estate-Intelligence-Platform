#!/bin/sh
# ai-mlops:validate-training-dataset / prepare. Sourced by GitLab; run from the project checkout.

kubectl version --client
echo
echo "============================================================"
echo "TRAINING DATASET VALIDATION SOURCE CHECK"
echo "============================================================"

echo
echo "Job source:"
echo "$DATASET_VALIDATION_SOURCE_PATH"

test -f "$DATASET_VALIDATION_SOURCE_PATH"
kubectl get namespace \
  "$K8S_NAMESPACE"
kubectl \
  -n "$K8S_NAMESPACE" \
  get secret \
  "$POSTGRES_SECRET"
kubectl \
  -n "$K8S_NAMESPACE" \
  get secret \
  "$REGISTRY_PULL_SECRET"
rm -f "$DATASET_VALIDATION_RENDERED_PATH"
echo
echo "============================================================"
echo "RENDERING TRAINING DATASET VALIDATION JOB"
echo "============================================================"

EXPECTED_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo
echo "Expected image:"
echo "$EXPECTED_IMAGE"

echo
echo "Expected Kubernetes Job:"
echo "$DATASET_VALIDATION_JOB_NAME"

grep \
  "__AI_MLOPS_IMAGE__" \
  "$DATASET_VALIDATION_SOURCE_PATH"

sed \
  -e "s|__AI_MLOPS_IMAGE__|${EXPECTED_IMAGE}|g" \
  -e "s|__CI_COMMIT_SHA__|${CI_COMMIT_SHA}|g" \
  -e "s|__CI_COMMIT_SHORT_SHA__|${CI_COMMIT_SHORT_SHA}|g" \
  -e "s|__CI_COMMIT_BRANCH__|${CI_COMMIT_BRANCH}|g" \
  -e "s|__CI_COMMIT_REF_NAME__|${CI_COMMIT_REF_NAME}|g" \
  -e "s|__CI_PROJECT_URL__|${CI_PROJECT_URL}|g" \
  -e "s|__CI_PROJECT_PATH__|${CI_PROJECT_PATH}|g" \
  -e "s|__CI_PIPELINE_ID__|${CI_PIPELINE_ID}|g" \
  -e "s|__CI_PIPELINE_URL__|${CI_PIPELINE_URL}|g" \
  -e "s|__CI_JOB_ID__|${CI_JOB_ID}|g" \
  -e "s|__CI_JOB_NAME__|${CI_JOB_NAME}|g" \
  -e "s|__CI_JOB_URL__|${CI_JOB_URL}|g" \
  "$DATASET_VALIDATION_SOURCE_PATH" \
  > "$DATASET_VALIDATION_RENDERED_PATH"

test -s "$DATASET_VALIDATION_RENDERED_PATH"
if grep -E -q \
  "__AI_MLOPS_IMAGE__|__CI_[A-Z0-9_]+__" \
  "$DATASET_VALIDATION_RENDERED_PATH"; then

  echo
  echo "ERROR:"
  echo "Unresolved placeholder remains in rendered dataset validation Job:"
  echo

  grep -E \
    "__AI_MLOPS_IMAGE__|__CI_[A-Z0-9_]+__" \
    "$DATASET_VALIDATION_RENDERED_PATH" || true

  exit 1
fi

echo "All dataset validation placeholders replaced successfully."
EXPECTED_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo
echo "Validating rendered immutable image..."

grep \
  "image: ${EXPECTED_IMAGE}" \
  "$DATASET_VALIDATION_RENDERED_PATH"

echo "Immutable image validated successfully."
echo
echo "Expected Kubernetes Job:"
echo "$DATASET_VALIDATION_JOB_NAME"

echo
echo "Rendered Kubernetes names:"

grep \
  "name:" \
  "$DATASET_VALIDATION_RENDERED_PATH" || true

grep \
  "name: ${DATASET_VALIDATION_JOB_NAME}" \
  "$DATASET_VALIDATION_RENDERED_PATH"

echo "Dataset validation Kubernetes Job name validated successfully."
echo
echo "Validating dataset validation entrypoint..."

grep \
  "src.ai.matching.run_training_dataset_validation" \
  "$DATASET_VALIDATION_RENDERED_PATH"

echo "Dataset validation entrypoint validated successfully."
echo
echo "Validating Registry pull Secret reference..."

grep \
  "name: ${REGISTRY_PULL_SECRET}" \
  "$DATASET_VALIDATION_RENDERED_PATH"

echo "Registry pull Secret reference validated successfully."
kubectl apply \
  --dry-run=client \
  -f "$DATASET_VALIDATION_RENDERED_PATH" \
  > /dev/null

echo
echo "Dataset validation Kubernetes Job manifest is valid."
