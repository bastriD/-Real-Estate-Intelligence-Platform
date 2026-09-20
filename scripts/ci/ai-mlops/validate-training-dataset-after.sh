#!/bin/sh
# ai-mlops:validate-training-dataset / after_script. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "TRAINING DATASET VALIDATION AFTER-SCRIPT DIAGNOSTICS"
echo "============================================================"

kubectl \
  -n real-estate \
  get job \
  real-estate-matching-training-dataset-validation \
  -o wide || true

kubectl \
  -n real-estate \
  get pods \
  -l app.kubernetes.io/name=real-estate-matching-training-dataset-validation \
  -o wide || true

kubectl \
  -n real-estate \
  logs \
  job/real-estate-matching-training-dataset-validation \
  --all-containers=true || true
rm -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-matching-training-dataset-validation.yaml
