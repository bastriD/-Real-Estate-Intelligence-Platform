#!/bin/sh
# ai-mlops:split-training-dataset / execute. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "CLEANING PREVIOUS TRAINING DATASET SPLIT"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  delete job \
  "$DATASET_SPLIT_JOB_NAME" \
  --ignore-not-found=true \
  --wait=true
echo
echo "============================================================"
echo "CREATING TRAINING DATASET SPLIT JOB"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  apply \
  -f "$DATASET_SPLIT_RENDERED_PATH"
kubectl \
  -n "$K8S_NAMESPACE" \
  get job \
  "$DATASET_SPLIT_JOB_NAME" \
  -o wide
echo
echo "Waiting for dataset split Pod..."

POD_NAME=""

for i in $(seq 1 60); do

  POD_NAME="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get pods \
      -l app.kubernetes.io/name="$DATASET_SPLIT_JOB_NAME" \
      -o jsonpath='{.items[0].metadata.name}' \
      2>/dev/null || true
  )"

  if [ -n "$POD_NAME" ]; then
    echo
    echo "Dataset split Pod:"
    echo "$POD_NAME"
    break
  fi

  sleep 2
done

if [ -z "${POD_NAME:-}" ]; then
  echo
  echo "ERROR:"
  echo "Dataset split Pod was not created."

  kubectl \
    -n "$K8S_NAMESPACE" \
    get job \
    "$DATASET_SPLIT_JOB_NAME" \
    -o wide || true

  exit 1
fi
echo
echo "============================================================"
echo "WAITING FOR TRAINING DATASET SPLIT"
echo "============================================================"

SUCCESS="false"

for i in $(seq 1 300); do

  COMPLETE="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get job \
      "$DATASET_SPLIT_JOB_NAME" \
      -o jsonpath='{.status.succeeded}' \
      2>/dev/null || true
  )"

  FAILED="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get job \
      "$DATASET_SPLIT_JOB_NAME" \
      -o jsonpath='{.status.failed}' \
      2>/dev/null || true
  )"

  if [ "${COMPLETE:-0}" -ge 1 ] 2>/dev/null; then
    SUCCESS="true"
    echo "Training dataset split completed successfully."
    break
  fi

  if [ "${FAILED:-0}" -ge 1 ] 2>/dev/null; then
    echo "Training dataset split reported a failed Pod."
    break
  fi

  echo "Dataset split still running..."
  sleep 2
done

if [ "$SUCCESS" != "true" ]; then

  echo
  echo "ERROR:"
  echo "Training dataset split did not complete successfully."

  echo
  echo "Job status:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    get job \
    "$DATASET_SPLIT_JOB_NAME" \
    -o wide || true

  echo
  echo "Pod status:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    get pods \
    -l app.kubernetes.io/name="$DATASET_SPLIT_JOB_NAME" \
    -o wide || true

  echo
  echo "Dataset split logs:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    logs \
    job/"$DATASET_SPLIT_JOB_NAME" \
    --all-containers=true || true

  exit 1
fi
echo
echo "============================================================"
echo "TRAINING DATASET SPLIT LOGS"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  logs \
  job/"$DATASET_SPLIT_JOB_NAME" \
  --all-containers=true
echo
echo "============================================================"
echo "TRAINING DATASET SPLIT FINAL KUBERNETES STATUS"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  get job \
  "$DATASET_SPLIT_JOB_NAME" \
  -o wide

kubectl \
  -n "$K8S_NAMESPACE" \
  get pods \
  -l app.kubernetes.io/name="$DATASET_SPLIT_JOB_NAME" \
  -o wide
