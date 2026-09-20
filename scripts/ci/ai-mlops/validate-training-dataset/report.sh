#!/bin/sh
# ai-mlops:validate-training-dataset / report. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "TRAINING DATASET VALIDATION COMPLETED"
echo "============================================================"

echo
echo "Image:"
echo "${IMAGE_NAME}:${IMAGE_TAG}"

echo
echo "Namespace:"
echo "$K8S_NAMESPACE"

echo
echo "Kubernetes Job:"
echo "$DATASET_VALIDATION_JOB_NAME"

echo
echo "Dataset source:"
echo "PostgreSQL runtime data"

echo
echo "Ground truth:"
echo "Explicit recherche_ref lineage"

echo
echo "Candidate engine:"
echo "Canonical matching repository"

echo
echo "Model training:"
echo "NOT performed"

echo
echo "MLflow:"
echo "Not used by this validation workload"

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
