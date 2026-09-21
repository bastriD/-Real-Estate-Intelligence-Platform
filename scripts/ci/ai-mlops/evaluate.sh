#!/bin/sh
. "$CI_PROJECT_DIR/scripts/ci/database/check-search-schema.sh"
# ai-mlops:evaluate / script. Sourced by GitLab; run from the project checkout.

. "$CI_PROJECT_DIR/scripts/ci/ai-mlops/evaluate/prepare.sh"
. "$CI_PROJECT_DIR/scripts/ci/ai-mlops/evaluate/execute.sh"
. "$CI_PROJECT_DIR/scripts/ci/ai-mlops/evaluate/report.sh"
