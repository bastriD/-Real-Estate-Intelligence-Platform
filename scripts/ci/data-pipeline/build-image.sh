#!/bin/sh
# data-pipeline:build-image / script. Sourced by GitLab; run from the project checkout.

echo "============================================================"
echo "BUILDING REAL ESTATE DATA-PIPELINE IMAGE"
echo "============================================================"

echo "Image:"
echo "  $IMAGE_NAME:$IMAGE_TAG"
echo "  $IMAGE_NAME:latest"

docker build \
  -f deploy/docker/Dockerfile.data-pipeline \
  -t "$IMAGE_NAME:$IMAGE_TAG" \
  -t "$IMAGE_NAME:latest" \
  .
echo "============================================================"
echo "VALIDATING DATA-PIPELINE IMAGE CONTENT"
echo "============================================================"

docker run --rm \
  --entrypoint /bin/sh \
  "$IMAGE_NAME:$IMAGE_TAG" \
  -c '
    set -e

    echo "Checking BRONZE ingestion components..."

    test -f /app/database/seeds/generer_annonces.py
    test -f /app/database/seeds/upload_generated_to_s3.py
    test -f /app/database/seeds/download_generated_from_s3.py
    test -f /app/database/seeds/load_raw_generated_data.py

    echo "PASS: BRONZE ingestion components present."

    echo
    echo "Checking SILVER transformation components..."

    test -f /app/database/seeds/transform_raw_to_staging.py
    test -f /app/database/seeds/load_staging_recherches_to_oltp.py
    test -f /app/database/seeds/load_staging_to_oltp.py

    echo "PASS: SILVER transformation components present."

    echo
    echo "Checking data-quality SQL files..."

    test -f /app/database/tests/004_raw_data_quality.sql
    test -f /app/database/tests/005_staging_data_quality.sql
    test -f /app/database/tests/006_oltp_data_quality.sql
    test -f /app/database/tests/007_warehouse_data_quality.sql

    echo "PASS: data-quality SQL files present."

    echo
    echo "Checking GOLD warehouse components..."

    test -f /app/database/olap/load_warehouse.py

    echo "PASS: warehouse loader present."

    echo
    echo "Checking dbt project..."

    test -d /app/pipelines/dbt
    test -f /app/pipelines/dbt/dbt_project.yml
    test -f /app/pipelines/dbt/profiles.yml.example

    echo "PASS: dbt project present."

    echo
    echo "Checking observability components..."

    test -d /app/observability/metrics
    test -f /app/observability/metrics/dq_runner.py
    test -f /app/observability/metrics/collect_metrics.py

    echo "PASS: observability components present."

    echo
    echo "Checking generated fixture directory..."

    test -d /app/database/fixtures/annonces
    test -d /app/database/fixtures/annonces/json

    echo "PASS: generated fixture directories present."

    echo
    echo "Checking Python runtime dependencies..."

    python -c "import boto3; import psycopg; import prometheus_client; print(\"PASS: Python runtime dependencies import correctly.\")"

    echo
    echo "Checking dbt runtime..."

    dbt --version

    echo "PASS: dbt executable available."

    echo
    echo "============================================================"
    echo "PASS: DATA-PIPELINE IMAGE VALIDATION SUCCESSFUL"
    echo "============================================================"
  '
echo "============================================================"
echo "PUSHING COMMIT-TAGGED IMAGE"
echo "============================================================"

docker push "$IMAGE_NAME:$IMAGE_TAG"
echo "============================================================"
echo "PUSHING LATEST IMAGE"
echo "============================================================"

docker push "$IMAGE_NAME:latest"
echo "============================================================"
echo "DATA-PIPELINE IMAGE PUBLISHED"
echo "============================================================"

echo "Commit image:"
echo "$IMAGE_NAME:$IMAGE_TAG"

echo
echo "Latest image:"
echo "$IMAGE_NAME:latest"
mkdir -p airflow-dags
cp pipelines/airflow/*.py airflow-dags/
DATA_PIPELINE_IMAGE="$(docker image inspect --format '{{index .RepoDigests 0}}' "$IMAGE_NAME:$IMAGE_TAG")"
test -n "$DATA_PIPELINE_IMAGE"
python3 scripts/ci/pin_airflow_image.py \
  airflow-dags/real_estate_ingestion_dag.py "$DATA_PIPELINE_IMAGE"
printf 'DATA_PIPELINE_IMAGE=%s\n' "$DATA_PIPELINE_IMAGE" > data-pipeline-image.env
