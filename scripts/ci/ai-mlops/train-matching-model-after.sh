#!/bin/sh
# ai-mlops:train-matching-model / after_script. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "MATCHING MODEL TRAINING AFTER-SCRIPT DIAGNOSTICS"
echo "============================================================"

kubectl \
  -n real-estate \
  get job \
  real-estate-matching-model-training \
  -o wide || true

kubectl \
  -n real-estate \
  get pods \
  -l app.kubernetes.io/name=real-estate-matching-model-training \
  -o wide || true

kubectl \
  -n real-estate \
  logs \
  job/real-estate-matching-model-training \
  --all-containers=true || true
rm -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-matching-model-training.yaml
