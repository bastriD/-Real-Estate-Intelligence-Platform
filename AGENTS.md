# Agent entrypoint

Read [the repository and CI map](docs/70-DEVOPS/REPOSITORY-AND-CI-MAP.md) first.
It describes the implemented layout, where changes belong, and how to verify
them. For product context and local setup, read [Readme.md](Readme.md).

## Working conventions

- Inspect `git status --short` before editing. Preserve unrelated user changes.
- Prefer implemented code and executable configuration when architecture
  documents describe capabilities that may still be planned.
- Keep CI configuration in `.gitlab/ci/` and implementation in `scripts/ci/`.
  Follow [the CI guide](.gitlab/ci/README.md) and
  [script conventions](scripts/ci/README.md).
- Keep existing job names, dependencies, manual controls, runner tags and
  deployment destinations stable during structural refactoring. A behavior
  change should be deliberate and explained separately.
- CI shell entrypoints are sourced in the runner shell. Preserve exports,
  working-directory changes, early exits and inherited error handling. Keep
  `after_script` independent because GitLab starts it in a fresh shell.
- When changing a script or moving a file, update the corresponding
  `rules:changes` filters and required producer/consumer selection together.
- The current structural checks cap component YAML at 200 lines and shell
  scripts at 250 lines. Split by responsibility, keeping complete commands and
  heredocs together. Do not bypass the checks to accommodate a monolithic file.
- Read and write text explicitly as UTF-8. The observability title regression
  described in the map is a real failure: syntax checks alone did not catch it.
- Run relevant executable validation as well as structural checks. Report what
  actually ran; local tests do not establish live GitLab/Kubernetes success.
- Do not execute database, publication or Kubernetes scripts simply to test
  syntax. They target real infrastructure. Use offline checks unless runtime
  operations are within the user's task.
- Keep credentials and local `.env` contents out of logs and documentation.
  `.venv-review/` is a local convenience, not a repository dependency.

## Verification entrypoints

From the repository root, using Python 3.12 and the appropriate dependencies:

```sh
python -m pytest tests/ci -q
python -m pytest tests/ai -q
python -m pytest tests/backend tests/data tests/ai/test_candidate_availability.py --cov=src/api --cov-fail-under=80
git diff --check
```

Backend tests require test-only `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` values.
See the map for dependency installation and Windows commands. Update the map
when moving entrypoints or changing the repository's organizational conventions.
