#!/bin/sh
# ai-model-comparison:compare / after_script. Sourced by GitLab; run from the project checkout.

echo
echo "=============================================="
echo "Comparison Job Diagnostic"
echo "=============================================="

kubectl -n "${KUBERNETES_NAMESPACE:-real-estate}" \
  get job "${COMPARISON_JOB_NAME:-real-estate-matching-model-comparison}" \
  -o wide \
  2>/dev/null || true
kubectl -n "${KUBERNETES_NAMESPACE:-real-estate}" \
  get pods \
  -l app.kubernetes.io/name=real-estate-matching-model-comparison \
  -o wide \
  2>/dev/null || true
kubectl -n "${KUBERNETES_NAMESPACE:-real-estate}" \
  logs \
  "job/${COMPARISON_JOB_NAME:-real-estate-matching-model-comparison}" \
  2>/dev/null || true
