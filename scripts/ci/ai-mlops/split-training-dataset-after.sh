#!/bin/sh
# ai-mlops:split-training-dataset / after_script. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "TRAINING DATASET SPLIT AFTER-SCRIPT DIAGNOSTICS"
echo "============================================================"

kubectl \
  -n real-estate \
  get job \
  real-estate-matching-training-dataset-split \
  -o wide || true

kubectl \
  -n real-estate \
  get pods \
  -l app.kubernetes.io/name=real-estate-matching-training-dataset-split \
  -o wide || true

kubectl \
  -n real-estate \
  logs \
  job/real-estate-matching-training-dataset-split \
  --all-containers=true || true
rm -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-matching-training-dataset-split.yaml
