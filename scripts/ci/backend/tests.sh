#!/bin/sh
# backend:tests / script. Sourced by GitLab; run from the project checkout.

. "$CI_PROJECT_DIR/scripts/ci/backend/tests/files.sh"
. "$CI_PROJECT_DIR/scripts/ci/backend/tests/imports-and-openapi.sh"
. "$CI_PROJECT_DIR/scripts/ci/backend/tests/regression-suite.sh"
