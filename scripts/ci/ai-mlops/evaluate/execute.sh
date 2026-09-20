#!/bin/sh
# ai-mlops:evaluate / execute. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "CLEANING PREVIOUS AI / MLOPS EVALUATION"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  delete job \
  "$MATCHING_EVALUATION_JOB_NAME" \
  --ignore-not-found=true \
  --wait=true
echo
echo "============================================================"
echo "CREATING AI / MLOPS EVALUATION JOB"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  apply \
  -f "$MATCHING_EVALUATION_RENDERED_PATH"
kubectl \
  -n "$K8S_NAMESPACE" \
  get job \
  "$MATCHING_EVALUATION_JOB_NAME" \
  -o wide
echo
echo "Waiting for evaluation Pod..."

POD_NAME=""

for i in $(seq 1 60); do

  POD_NAME="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get pods \
      -l app.kubernetes.io/name="$MATCHING_EVALUATION_JOB_NAME" \
      -o jsonpath='{.items[0].metadata.name}' \
      2>/dev/null || true
  )"

  if [ -n "$POD_NAME" ]; then
    echo "Evaluation Pod:"
    echo "$POD_NAME"
    break
  fi

  sleep 2
done

if [ -z "${POD_NAME:-}" ]; then
  echo
  echo "ERROR:"
  echo "Evaluation Pod was not created."

  kubectl \
    -n "$K8S_NAMESPACE" \
    get job \
    "$MATCHING_EVALUATION_JOB_NAME" \
    -o wide || true

  exit 1
fi
echo
echo "============================================================"
echo "WAITING FOR AI / MLOPS EVALUATION"
echo "============================================================"

SUCCESS="false"

for i in $(seq 1 150); do

  COMPLETE="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get job \
      "$MATCHING_EVALUATION_JOB_NAME" \
      -o jsonpath='{.status.succeeded}' \
      2>/dev/null || true
  )"

  FAILED="$(
    kubectl \
      -n "$K8S_NAMESPACE" \
      get job \
      "$MATCHING_EVALUATION_JOB_NAME" \
      -o jsonpath='{.status.failed}' \
      2>/dev/null || true
  )"

  if [ "${COMPLETE:-0}" -ge 1 ] 2>/dev/null; then
    SUCCESS="true"
    echo "Evaluation Job completed successfully."
    break
  fi

  if [ "${FAILED:-0}" -ge 1 ] 2>/dev/null; then
    echo "Evaluation Job reported a failed Pod."
    break
  fi

  echo "Evaluation still running..."
  sleep 2
done

if [ "$SUCCESS" != "true" ]; then

  echo
  echo "ERROR:"
  echo "AI / MLOps evaluation did not complete successfully."

  echo
  echo "Job status:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    get job \
    "$MATCHING_EVALUATION_JOB_NAME" \
    -o wide || true

  echo
  echo "Pod status:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    get pods \
    -l app.kubernetes.io/name="$MATCHING_EVALUATION_JOB_NAME" \
    -o wide || true

  echo
  echo "Evaluation logs:"

  kubectl \
    -n "$K8S_NAMESPACE" \
    logs \
    job/"$MATCHING_EVALUATION_JOB_NAME" \
    --all-containers=true || true

  exit 1
fi
echo
echo "============================================================"
echo "AI / MLOPS EVALUATION LOGS"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  logs \
  job/"$MATCHING_EVALUATION_JOB_NAME" \
  --all-containers=true
echo
echo "============================================================"
echo "AI / MLOPS FINAL KUBERNETES STATUS"
echo "============================================================"

kubectl \
  -n "$K8S_NAMESPACE" \
  get job \
  "$MATCHING_EVALUATION_JOB_NAME" \
  -o wide

kubectl \
  -n "$K8S_NAMESPACE" \
  get pods \
  -l app.kubernetes.io/name="$MATCHING_EVALUATION_JOB_NAME" \
  -o wide
