#!/bin/sh
# ai-mlops:evaluate / report. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "AI / MLOPS EVALUATION COMPLETED"
echo "============================================================"

echo
echo "Image:"
echo "${IMAGE_NAME}:${IMAGE_TAG}"

echo
echo "Namespace:"
echo "$K8S_NAMESPACE"

echo
echo "Kubernetes Job:"
echo "$MATCHING_EVALUATION_JOB_NAME"

echo
echo "MLflow:"
echo "http://mlflow-tracking.mlflow.svc.cluster.local:5000"

echo
echo "Execution type:"
echo "GitLab-triggered ephemeral Kubernetes Job"

echo
echo "Deployment:"
echo "None"

echo
echo "Service:"
echo "None"

echo
echo "Argo CD:"
echo "Not used for this execution workload"
