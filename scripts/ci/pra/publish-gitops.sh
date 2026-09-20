#!/bin/sh
# pra:publish-gitops / script. Sourced by GitLab; run from the project checkout.

. "$CI_PROJECT_DIR/scripts/ci/pra/publish-gitops/validate-runtime.sh"
. "$CI_PROJECT_DIR/scripts/ci/pra/publish-gitops/validate-backup.sh"
. "$CI_PROJECT_DIR/scripts/ci/pra/publish-gitops/prepare-gitops.sh"
. "$CI_PROJECT_DIR/scripts/ci/pra/publish-gitops/publish.sh"
. "$CI_PROJECT_DIR/scripts/ci/pra/publish-gitops/report.sh"
