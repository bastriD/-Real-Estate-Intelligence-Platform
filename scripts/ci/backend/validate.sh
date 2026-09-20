#!/bin/sh
# backend:validate / script. Sourced by GitLab; run from the project checkout.

. "$CI_PROJECT_DIR/scripts/ci/backend/validate/files-and-syntax.sh"
. "$CI_PROJECT_DIR/scripts/ci/backend/validate/runtime-imports.sh"
. "$CI_PROJECT_DIR/scripts/ci/backend/validate/authorization-and-payments.sh"
. "$CI_PROJECT_DIR/scripts/ci/backend/validate/openapi-and-summary.sh"
