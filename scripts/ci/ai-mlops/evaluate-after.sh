#!/bin/sh
# ai-mlops:evaluate / after_script. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "AI / MLOPS AFTER-SCRIPT DIAGNOSTICS"
echo "============================================================"

kubectl \
  -n real-estate \
  get job \
  real-estate-matching-evaluation \
  -o wide || true

kubectl \
  -n real-estate \
  get pods \
  -l app.kubernetes.io/name=real-estate-matching-evaluation \
  -o wide || true
rm -f ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/real-estate-matching-evaluation.yaml
