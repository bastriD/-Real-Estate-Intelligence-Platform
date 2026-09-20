#!/bin/sh
# ai-mlops:train-matching-model / prepare. Sourced by GitLab; run from the project checkout.

kubectl version --client
echo
echo "============================================================"
echo "MATCHING MODEL TRAINING SOURCE CHECK"
echo "============================================================"

echo
echo "Job source:"
echo "$MODEL_TRAINING_SOURCE_PATH"

test -f "$MODEL_TRAINING_SOURCE_PATH"
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
rm -f "$MODEL_TRAINING_RENDERED_PATH"
echo
echo "============================================================"
echo "RENDERING MATCHING MODEL TRAINING JOB"
echo "============================================================"

EXPECTED_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo
echo "Expected image:"
echo "$EXPECTED_IMAGE"

echo
echo "Expected Kubernetes Job:"
echo "$MODEL_TRAINING_JOB_NAME"

grep \
  "__AI_MLOPS_IMAGE__" \
  "$MODEL_TRAINING_SOURCE_PATH"

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
  "$MODEL_TRAINING_SOURCE_PATH" \
  > "$MODEL_TRAINING_RENDERED_PATH"

test -s "$MODEL_TRAINING_RENDERED_PATH"
if grep -E -q \
  "__AI_MLOPS_IMAGE__|__CI_[A-Z0-9_]+__" \
  "$MODEL_TRAINING_RENDERED_PATH"; then

  echo
  echo "ERROR:"
  echo "Unresolved placeholder remains in rendered model training Job:"
  echo

  grep -E \
    "__AI_MLOPS_IMAGE__|__CI_[A-Z0-9_]+__" \
    "$MODEL_TRAINING_RENDERED_PATH" || true

  exit 1
fi

echo "All model training placeholders replaced successfully."
EXPECTED_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo
echo "Validating rendered immutable image..."

grep \
  "image: ${EXPECTED_IMAGE}" \
  "$MODEL_TRAINING_RENDERED_PATH"

echo "Immutable image validated successfully."
echo
echo "Expected Kubernetes Job:"
echo "$MODEL_TRAINING_JOB_NAME"

echo
echo "Rendered Kubernetes names:"

grep \
  "name:" \
  "$MODEL_TRAINING_RENDERED_PATH" || true

grep \
  "name: ${MODEL_TRAINING_JOB_NAME}" \
  "$MODEL_TRAINING_RENDERED_PATH"

echo "Model training Kubernetes Job name validated successfully."
echo
echo "Validating supervised model training entrypoint..."

grep \
  "src.ai.matching.run_model_training" \
  "$MODEL_TRAINING_RENDERED_PATH"

echo "Model training entrypoint validated successfully."
echo
echo "Validating Registry pull Secret reference..."

grep \
  "name: ${REGISTRY_PULL_SECRET}" \
  "$MODEL_TRAINING_RENDERED_PATH"

echo "Registry pull Secret reference validated successfully."
kubectl apply \
  --dry-run=client \
  -f "$MODEL_TRAINING_RENDERED_PATH" \
  > /dev/null

echo
echo "Model training Kubernetes Job manifest is valid."
