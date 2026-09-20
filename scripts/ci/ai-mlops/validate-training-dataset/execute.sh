#!/bin/sh
# ai-mlops:validate-training-dataset / execute. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "CLEANING PREVIOUS TRAINING DATASET VALIDATION"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  delete job \
  "$DATASET_VALIDATION_JOB_NAME" \
  --ignore-not-found=true \
  --wait=true
echo
echo "============================================================"
echo "CREATING TRAINING DATASET VALIDATION JOB"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  apply \
  -f "$DATASET_VALIDATION_RENDERED_PATH"
kubectl \
  -n "$K8S_NAMESPACE" \
  get job \
  "$DATASET_VALIDATION_JOB_NAME" \
  -o wide
echo
echo "Waiting for dataset validation Pod..."

POD_NAME=""

for i in $(seq 1 60); do

  POD_NAME="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get pods \
      -l app.kubernetes.io/name="$DATASET_VALIDATION_JOB_NAME" \
      -o jsonpath='{.items[0].metadata.name}' \
      2>/dev/null || true
  )"

  if [ -n "$POD_NAME" ]; then
    echo
    echo "Dataset validation Pod:"
    echo "$POD_NAME"
    break
  fi

  sleep 2
done

if [ -z "${POD_NAME:-}" ]; then
  echo
  echo "ERROR:"
  echo "Dataset validation Pod was not created."

  kubectl \
    -n "$K8S_NAMESPACE" \
    get job \
    "$DATASET_VALIDATION_JOB_NAME" \
    -o wide || true

  exit 1
fi
echo
echo "============================================================"
echo "WAITING FOR TRAINING DATASET VALIDATION"
echo "============================================================"

SUCCESS="false"

for i in $(seq 1 300); do

  COMPLETE="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get job \
      "$DATASET_VALIDATION_JOB_NAME" \
      -o jsonpath='{.status.succeeded}' \
      2>/dev/null || true
  )"

  FAILED="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get job \
      "$DATASET_VALIDATION_JOB_NAME" \
      -o jsonpath='{.status.failed}' \
      2>/dev/null || true
  )"

  if [ "${COMPLETE:-0}" -ge 1 ] 2>/dev/null; then
    SUCCESS="true"
    echo "Training dataset validation completed successfully."
    break
  fi

  if [ "${FAILED:-0}" -ge 1 ] 2>/dev/null; then
    echo "Training dataset validation reported a failed Pod."
    break
  fi

  echo "Dataset validation still running..."
  sleep 2
done

if [ "$SUCCESS" != "true" ]; then

  echo
  echo "ERROR:"
  echo "Training dataset validation did not complete successfully."

  echo
  echo "Job status:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    get job \
    "$DATASET_VALIDATION_JOB_NAME" \
    -o wide || true

  echo
  echo "Pod status:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    get pods \
    -l app.kubernetes.io/name="$DATASET_VALIDATION_JOB_NAME" \
    -o wide || true

  echo
  echo "Dataset validation logs:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    logs \
    job/"$DATASET_VALIDATION_JOB_NAME" \
    --all-containers=true || true

  exit 1
fi
echo
echo "============================================================"
echo "TRAINING DATASET VALIDATION LOGS"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  logs \
  job/"$DATASET_VALIDATION_JOB_NAME" \
  --all-containers=true
echo
echo "============================================================"
echo "TRAINING DATASET VALIDATION FINAL KUBERNETES STATUS"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  get job \
  "$DATASET_VALIDATION_JOB_NAME" \
  -o wide

kubectl \
  -n "$K8S_NAMESPACE" \
  get pods \
  -l app.kubernetes.io/name="$DATASET_VALIDATION_JOB_NAME" \
  -o wide
