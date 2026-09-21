#!/bin/sh
. "$CI_PROJECT_DIR/scripts/ci/database/check-search-schema.sh"
# ai-mlops:train-matching-model / script. Sourced by GitLab; run from the project checkout.

. "$CI_PROJECT_DIR/scripts/ci/ai-mlops/train-matching-model/prepare.sh"
. "$CI_PROJECT_DIR/scripts/ci/ai-mlops/train-matching-model/execute.sh"
. "$CI_PROJECT_DIR/scripts/ci/ai-mlops/train-matching-model/report.sh"
