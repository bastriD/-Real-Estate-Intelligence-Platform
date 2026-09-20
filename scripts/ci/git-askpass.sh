#!/bin/sh
# Git supplies the prompt; credentials stay in the job environment.
case "$1" in
  *Username*|*username*) printf '%s\n' "${LAB_GITOPS_GIT_USER:?}" ;;
  *Password*|*password*) printf '%s\n' "${LAB_GITOPS_GIT_TOKEN:?}" ;;
  *) exit 1 ;;
esac
