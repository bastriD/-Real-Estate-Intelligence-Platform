#!/bin/sh
# ai-mlops:train-matching-model / report. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "MATCHING MODEL TRAINING COMPLETED"
echo "============================================================"

echo
echo "Image:"
echo "${IMAGE_NAME}:${IMAGE_TAG}"

echo
echo "Namespace:"
echo "$K8S_NAMESPACE"

echo
echo "Kubernetes Job:"
echo "$MODEL_TRAINING_JOB_NAME"

echo
echo "Dataset source:"
echo "PostgreSQL runtime reconstruction"

echo
echo "Candidate engine:"
echo "Canonical matching repository"

echo
echo "Ground truth:"
echo "Explicit generated-search lineage"

echo
echo "Training dataset:"
echo "Informative demande_version groups only"

echo
echo "Split:"
echo "Reproducible runtime-group-v2 split with dataset fingerprint"

echo
echo "Model:"
echo "Logistic Regression baseline V1"

echo
echo "Hard eligibility:"
echo "Preserved outside ML ranking"

echo
echo "Ground-truth leakage:"
echo "Forbidden"

echo
echo "Model training:"
echo "PERFORMED"

echo
echo "Model persistence:"
echo "NOT performed yet"

echo
echo "MLflow:"
echo "NOT used by this training workload yet"

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
