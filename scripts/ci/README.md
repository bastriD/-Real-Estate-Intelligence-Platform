# CI implementation scripts

GitLab job configuration lives in `.gitlab/ci/`. This directory contains the
commands, organized by component and job name:

```text
scripts/ci/
  backend/
    validate.sh
    validate/                 # Files, imports, authorization and OpenAPI checks
    build-image.sh
    publish-gitops.sh
    publish-gitops/            # Prepare, render/validate, publish
    tests.sh
    tests/                    # Files, imports/OpenAPI, regression suite
  database/
    validate.sh
    migrate-001.sh             # One entrypoint per existing database job
    ...
  ai-mlops/
    build-image.sh
    evaluate.sh
    evaluate/                 # Prepare, execute, report
    evaluate-after.sh         # Diagnostics in GitLab's separate after_script shell
    ...
  pra/
    publish-gitops.sh
    publish-gitops/            # Runtime/backup checks, preparation, publication
  ...                         # Airflow, AI, governance, observability, metadata, warehouse
  git-askpass.sh
  pin_airflow_image.py
```

The YAML sources each entrypoint in the runner's shell from the repository
checkout. Entrypoints may source named phases. This is intentional: invoking
each phase as a separate subprocess would lose variables and directory changes.
Do not add shell options, wrappers or conditional sourcing without checking
failure and early-exit behavior.

Implementation files stay below 250 lines; phases should represent a coherent
operation. Keep job rules, secrets configuration and runner selection in YAML.
Use `python -m pytest tests/ci -q` to check the wiring and shell syntax locally.
These checks never run deployment commands.
