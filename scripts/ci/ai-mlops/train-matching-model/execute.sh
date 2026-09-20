#!/bin/sh
# ai-mlops:train-matching-model / execute. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "CLEANING PREVIOUS MATCHING MODEL TRAINING"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  delete job \
  "$MODEL_TRAINING_JOB_NAME" \
  --ignore-not-found=true \
  --wait=true
echo
echo "============================================================"
echo "CREATING MATCHING MODEL TRAINING JOB"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  apply \
  -f "$MODEL_TRAINING_RENDERED_PATH"
kubectl \
  -n "$K8S_NAMESPACE" \
  get job \
  "$MODEL_TRAINING_JOB_NAME" \
  -o wide
echo
echo "Waiting for model training Pod..."

POD_NAME=""

for i in $(seq 1 60); do

  POD_NAME="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get pods \
      -l app.kubernetes.io/name="$MODEL_TRAINING_JOB_NAME" \
      -o jsonpath='{.items[0].metadata.name}' \
      2>/dev/null || true
  )"

  if [ -n "$POD_NAME" ]; then
    echo
    echo "Model training Pod:"
    echo "$POD_NAME"
    break
  fi

  sleep 2
done

if [ -z "${POD_NAME:-}" ]; then
  echo
  echo "ERROR:"
  echo "Model training Pod was not created."

  kubectl \
    -n "$K8S_NAMESPACE" \
    get job \
    "$MODEL_TRAINING_JOB_NAME" \
    -o wide || true

  exit 1
fi
echo
echo "============================================================"
echo "WAITING FOR MATCHING MODEL TRAINING"
echo "============================================================"

SUCCESS="false"

for i in $(seq 1 300); do

  COMPLETE="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get job \
      "$MODEL_TRAINING_JOB_NAME" \
      -o jsonpath='{.status.succeeded}' \
      2>/dev/null || true
  )"

  FAILED="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get job \
      "$MODEL_TRAINING_JOB_NAME" \
      -o jsonpath='{.status.failed}' \
      2>/dev/null || true
  )"

  if [ "${COMPLETE:-0}" -ge 1 ] 2>/dev/null; then
    SUCCESS="true"
    echo "Matching model training completed successfully."
    break
  fi

  if [ "${FAILED:-0}" -ge 1 ] 2>/dev/null; then
    echo "Matching model training reported a failed Pod."
    break
  fi

  echo "Model training still running..."
  sleep 2
done

if [ "$SUCCESS" != "true" ]; then

  echo
  echo "ERROR:"
  echo "Matching model training did not complete successfully."

  echo
  echo "Job status:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    get job \
    "$MODEL_TRAINING_JOB_NAME" \
    -o wide || true

  echo
  echo "Pod status:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    get pods \
    -l app.kubernetes.io/name="$MODEL_TRAINING_JOB_NAME" \
    -o wide || true

  echo
  echo "Model training logs:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    logs \
    job/"$MODEL_TRAINING_JOB_NAME" \
    --all-containers=true || true

  exit 1
fi
echo
echo "============================================================"
echo "MATCHING MODEL TRAINING LOGS"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  logs \
  job/"$MODEL_TRAINING_JOB_NAME" \
  --all-containers=true
echo
echo "============================================================"
echo "MATCHING MODEL TRAINING FINAL KUBERNETES STATUS"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  get job \
  "$MODEL_TRAINING_JOB_NAME" \
  -o wide

kubectl \
  -n "$K8S_NAMESPACE" \
  get pods \
  -l app.kubernetes.io/name="$MODEL_TRAINING_JOB_NAME" \
  -o wide
