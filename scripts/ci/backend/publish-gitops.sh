#!/bin/sh
# backend:publish-gitops / script. Sourced by GitLab; run from the project checkout.

. "$CI_PROJECT_DIR/scripts/ci/backend/publish-gitops/prepare.sh"
. "$CI_PROJECT_DIR/scripts/ci/backend/publish-gitops/render-and-validate.sh"
. "$CI_PROJECT_DIR/scripts/ci/backend/publish-gitops/publish.sh"
