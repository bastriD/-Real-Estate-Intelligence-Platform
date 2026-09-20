#!/bin/sh
# ai-mlops:split-training-dataset / report. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "TRAINING DATASET SPLIT COMPLETED"
echo "============================================================"

echo
echo "Image:"
echo "${IMAGE_NAME}:${IMAGE_TAG}"

echo
echo "Namespace:"
echo "$K8S_NAMESPACE"

echo
echo "Kubernetes Job:"
echo "$DATASET_SPLIT_JOB_NAME"

echo
echo "Dataset source:"
echo "PostgreSQL runtime reconstruction"

echo
echo "Training dataset:"
echo "Informative groups containing both relevance classes"

echo
echo "Split strategy:"
echo "Group-aware by id_demande_version"

echo
echo "Expected logical partition:"
echo "7 train / 2 validation / 2 test groups for the current 11-group dataset"

echo
echo "Leakage policy:"
echo "No id_demande_version may occur in more than one partition"

echo
echo "Model training:"
echo "NOT performed"

echo
echo "MLflow:"
echo "Not used by this split workload"

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
