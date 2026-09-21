#!/bin/sh
. "$CI_PROJECT_DIR/scripts/ci/database/check-search-schema.sh"
# ai-mlops:split-training-dataset / script. Sourced by GitLab; run from the project checkout.

. "$CI_PROJECT_DIR/scripts/ci/ai-mlops/split-training-dataset/prepare.sh"
. "$CI_PROJECT_DIR/scripts/ci/ai-mlops/split-training-dataset/execute.sh"
. "$CI_PROJECT_DIR/scripts/ci/ai-mlops/split-training-dataset/report.sh"
