#!/bin/sh
# ai-mlops:build-image / script. Sourced by GitLab; run from the project checkout.

test -f requirements-backend.txt
test -f requirements-ai.txt
test -f requirements-ai-mlops.txt
test -f deploy/docker/Dockerfile.ai-mlops
test -f src/ai/matching/features.py
test -f src/ai/matching/repository.py
test -f src/ai/matching/evaluate.py
test -f src/ai/matching/mlflow_tracking.py
test -f src/ai/matching/run_evaluation.py
test -f src/ai/matching/training_dataset.py
test -f src/ai/matching/run_training_dataset_validation.py
test -f src/ai/matching/dataset_split.py
test -f src/ai/matching/run_training_dataset_split.py
test -f src/ai/matching/model_training.py
test -f src/ai/matching/run_model_training.py
test -f deploy/mlops/matching-evaluation-job.yaml
test -f deploy/mlops/matching-training-dataset-validation-job.yaml
test -f deploy/mlops/matching-training-dataset-split-job.yaml
test -f deploy/mlops/matching-model-training-job.yaml
echo
echo "============================================================"
echo "BUILDING REAL ESTATE AI / MLOPS IMAGE"
echo "============================================================"

echo
echo "Immutable image:"
echo "$IMAGE_NAME:$IMAGE_TAG"

docker build \
  -f deploy/docker/Dockerfile.ai-mlops \
  -t "$IMAGE_NAME:$IMAGE_TAG" \
  -t "$IMAGE_NAME:latest" \
  .
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python --version
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "import numpy; import pandas; import psycopg; import mlflow; print('NumPy:', numpy.__version__); print('Pandas:', pandas.__version__); print('psycopg:', psycopg.__version__); print('MLflow:', mlflow.__version__)"
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.ai.matching.features import MatchingWeights; from src.ai.matching.repository import load_matching_input; from src.ai.matching.evaluate import evaluate_demande_version; print('Matching modules imported successfully'); print(MatchingWeights())"
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.ai.matching.training_dataset import build_training_dataset, build_training_group, dataset_summary; print('Training dataset module imported successfully')"
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.ai.matching.mlflow_tracking import configure_mlflow, log_deterministic_evaluation; print('MLflow tracking module imported successfully')"
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "import src.ai.matching.run_evaluation; print('run_evaluation module imported successfully')"
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "import src.ai.matching.run_training_dataset_validation; print('run_training_dataset_validation module imported successfully')"
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.ai.matching.dataset_split import create_group_aware_split, split_summary; import src.ai.matching.run_training_dataset_split; print('Group-aware dataset split modules imported successfully')"


# -------------------------------------------------------------------------
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.ai.matching.model_training import train_logistic_regression, train_and_evaluate_logistic_regression; import src.ai.matching.run_model_training; print('Supervised model training modules imported successfully')"
echo
echo "Publishing immutable AI / MLOps image:"
echo "$IMAGE_NAME:$IMAGE_TAG"

docker push \
  "$IMAGE_NAME:$IMAGE_TAG"
docker push \
  "$IMAGE_NAME:latest"
echo
echo "============================================================"
echo "AI / MLOPS IMAGE PUBLISHED"
echo "============================================================"

echo
echo "Immutable image:"
echo "$IMAGE_NAME:$IMAGE_TAG"

echo
echo "Latest image:"
echo "$IMAGE_NAME:latest"

echo
echo "Runtime capabilities:"
echo "- deterministic matching evaluation"
echo "- MLflow tracking"
echo "- supervised dataset reconstruction"
echo "- supervised dataset validation"
echo "- group-aware train / validation / test split"
echo "- supervised Logistic Regression training"

echo
echo "Model training capability:"
echo "PACKAGED in the immutable AI / MLOps image"
