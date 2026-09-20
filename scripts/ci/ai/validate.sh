#!/bin/sh
# ai:validate / script. Sourced by GitLab; run from the project checkout.

test -f requirements-backend.txt
test -f requirements-ai.txt
test -f requirements-ai-training.txt
test -f src/ai/matching/features.py
test -f src/ai/matching/repository.py
test -f src/ai/matching/evaluate.py
test -f src/ai/matching/mlflow_tracking.py
test -f src/ai/matching/run_evaluation.py
test -f tests/ai/test_matching_features.py
python -m py_compile src/ai/matching/features.py
python -m py_compile src/ai/matching/repository.py
python -m py_compile src/ai/matching/evaluate.py
python -m py_compile src/ai/matching/mlflow_tracking.py
python -m py_compile src/ai/matching/run_evaluation.py
python -c "import numpy; print('NumPy', numpy.__version__)"
python -c "import pandas; print('Pandas', pandas.__version__)"
python -c "import psycopg; print('Psycopg', psycopg.__version__)"
python -c "
from src.ai.matching.features import (
    MatchingWeights,
    build_matching_features,
    compute_matching_score,
)
print('Matching feature modules import OK')
print(MatchingWeights())
"
python -c "
from src.ai.matching.repository import (
    load_candidate_biens,
    load_demande_version,
    load_ground_truth_references,
    load_matching_input,
)
print('Matching repository imports OK')
"
python -c "
from src.ai.matching.evaluate import evaluate_demande_version
print('Matching evaluation import OK')
"
echo
echo "============================================================"
echo "RUNNING PURE MATCHING UNIT TESTS"
echo "============================================================"
echo
echo "Unit tests use controlled fixtures; live integration runs in Kubernetes."
echo "Real repository integration is validated in Kubernetes."
echo

python -m pytest \
  tests/ai \
  --junitxml=ai-tests.xml \
  -v
echo
echo "============================================================"
echo "AI VALIDATION COMPLETED"
echo "============================================================"
echo
echo "Validated here:"
echo "- dependencies"
echo "- syntax"
echo "- imports"
echo "- deterministic matching functions"
echo
echo "Validated later by ai-mlops:evaluate:"
echo "- PostgreSQL connectivity"
echo "- real DemandeVersion extraction"
echo "- real candidate extraction"
echo "- matching orchestration"
echo "- MLflow integration"
echo "- Kubernetes execution"
