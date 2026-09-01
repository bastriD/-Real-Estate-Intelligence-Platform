from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.utils.task_group import TaskGroup
from kubernetes.client import models as k8s


# =============================================================================
# DAG CONFIGURATION
# =============================================================================

DAG_ID = "real_estate_ingestion"

DATA_PIPELINE_IMAGE = (
    "gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest"
)

AIRFLOW_NAMESPACE = "airflow"

POSTGRES_SECRET = "real-estate-postgresql-secret"
S3_SECRET = "real-estate-s3"
REGISTRY_SECRET = "gitlab-registry"

PUSHGATEWAY_URL = (
    "http://retail-pushgateway.monitoring.svc.cluster.local:9091"
)

DEFAULT_ARGS = {
    "owner": "real-estate",
    "depends_on_past": False,
    "retries": 1,
}


# =============================================================================
# COMMON KUBERNETES CONFIGURATION
# =============================================================================

IMAGE_PULL_SECRETS = [
    k8s.V1LocalObjectReference(
        name=REGISTRY_SECRET,
    )
]

POSTGRES_ENV = [
    k8s.V1EnvFromSource(
        secret_ref=k8s.V1SecretEnvSource(
            name=POSTGRES_SECRET,
        )
    )
]

S3_ENV = [
    k8s.V1EnvFromSource(
        secret_ref=k8s.V1SecretEnvSource(
            name=S3_SECRET,
        )
    )
]

S3_AND_POSTGRES_ENV = [
    k8s.V1EnvFromSource(
        secret_ref=k8s.V1SecretEnvSource(
            name=S3_SECRET,
        )
    ),
    k8s.V1EnvFromSource(
        secret_ref=k8s.V1SecretEnvSource(
            name=POSTGRES_SECRET,
        )
    ),
]


# =============================================================================
# DAG
# =============================================================================

with DAG(
    dag_id=DAG_ID,
    description=(
        "Real Estate Medallion pipeline: "
        "BRONZE -> SILVER -> GOLD -> OBSERVABILITY"
    ),
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 8, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=[
        "real-estate",
        "data-engineering",
        "medallion",
        "bronze",
        "silver",
        "gold",
        "postgresql",
        "dbt",
        "observability",
    ],
) as dag:

    # =========================================================================
    # START
    # =========================================================================

    start = EmptyOperator(
        task_id="start",
    )

    # =========================================================================
    # BRONZE
    #
    # Physical layer:
    #   - External/generated source
    #   - MinIO object storage
    #   - PostgreSQL RAW schema
    #
    # Responsibilities:
    #   - Generate heterogeneous source data
    #   - Persist source files in MinIO
    #   - Load immutable/raw records
    #   - Validate ingestion completeness and raw integrity
    # =========================================================================

    with TaskGroup(
        group_id="bronze",
        tooltip="BRONZE - Source ingestion and RAW data",
        prefix_group_id=False,
    ) as bronze_group:

        generate_source_data_task = KubernetesPodOperator(
            task_id="generate_source_data",
            name="real-estate-generate-source-data",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                """
                set -e

                export INGESTION_BATCH="generated-{{ ts_nodash }}"

                echo "============================================================"
                echo "BRONZE - GENERATE SOURCE DATA"
                echo "============================================================"
                echo "Ingestion batch: ${INGESTION_BATCH}"

                # -------------------------------------------------------------
                # IMPORTANT:
                # The official generator is intentionally cumulative.
                #
                # An Airflow ingestion batch must however represent one isolated
                # dataset. KubernetesPodOperator pods are normally ephemeral,
                # but explicitly clearing the generated directory guarantees
                # deterministic behaviour even if the image or runtime changes.
                # -------------------------------------------------------------

                echo "Resetting generated working dataset..."

                rm -rf /app/database/fixtures/annonces
                mkdir -p /app/database/fixtures/annonces

                echo "Generating source dataset..."

                python /app/database/seeds/generer_annonces.py \
                  -r 5 \
                  --min-annonces 200 \
                  --max-annonces 200

                echo "Uploading generated dataset to MinIO..."

                python /app/database/seeds/upload_generated_to_s3.py

                echo "Source generation and upload completed."
                """
            ],
            env_from=S3_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        load_raw_task = KubernetesPodOperator(
            task_id="load_raw",
            name="real-estate-load-raw",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                """
                set -e

                export INGESTION_BATCH="generated-{{ ts_nodash }}"

                echo "============================================================"
                echo "BRONZE - LOAD RAW"
                echo "============================================================"
                echo "Ingestion batch: ${INGESTION_BATCH}"

                echo "Downloading generated CSVs from MinIO..."

                python /app/database/seeds/download_generated_from_s3.py

                echo "Loading RAW PostgreSQL tables..."

                python /app/database/seeds/load_raw_generated_data.py

                echo "RAW load completed."
                """
            ],
            env_from=S3_AND_POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        validate_raw_task = KubernetesPodOperator(
            task_id="validate_raw",
            name="real-estate-validate-raw",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                f"""
                set -e

                export INGESTION_BATCH="generated-{{{{ ts_nodash }}}}"
                export PUSHGATEWAY_URL="{PUSHGATEWAY_URL}"
                export PUSHGATEWAY_JOB="real_estate_data_quality"

                echo "============================================================"
                echo "BRONZE - RAW DATA QUALITY"
                echo "============================================================"
                echo "Ingestion batch: ${{INGESTION_BATCH}}"

                python /app/observability/metrics/dq_runner.py \
                  --layer raw \
                  --sql-file /app/database/tests/004_raw_data_quality.sql \
                  --ingestion-batch "${{INGESTION_BATCH}}"

                echo "RAW validation completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        (
            generate_source_data_task
            >> load_raw_task
            >> validate_raw_task
        )

    # =========================================================================
    # SILVER
    #
    # Physical layers:
    #   - PostgreSQL STAGING schema
    #   - PostgreSQL real_estate OLTP schema
    #
    # Responsibilities:
    #   - Parse and normalize heterogeneous RAW values
    #   - Validate typed and normalized records
    #   - Load generated searches into DEMANDE / DEMANDE_VERSION
    #   - Load generated listings into BIEN
    #   - Validate OLTP integrity and reconciliation
    # =========================================================================

    with TaskGroup(
        group_id="silver",
        tooltip="SILVER - STAGING normalization and OLTP integration",
        prefix_group_id=False,
    ) as silver_group:

        transform_staging_task = KubernetesPodOperator(
            task_id="transform_staging",
            name="real-estate-transform-staging",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                """
                set -e

                export INGESTION_BATCH="generated-{{ ts_nodash }}"

                echo "============================================================"
                echo "SILVER - RAW -> STAGING"
                echo "============================================================"
                echo "Ingestion batch: ${INGESTION_BATCH}"

                python /app/database/seeds/transform_raw_to_staging.py

                echo "STAGING transformation completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        validate_staging_task = KubernetesPodOperator(
            task_id="validate_staging",
            name="real-estate-validate-staging",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                f"""
                set -e

                export INGESTION_BATCH="generated-{{{{ ts_nodash }}}}"
                export PUSHGATEWAY_URL="{PUSHGATEWAY_URL}"
                export PUSHGATEWAY_JOB="real_estate_data_quality"

                echo "============================================================"
                echo "SILVER - STAGING DATA QUALITY"
                echo "============================================================"
                echo "Ingestion batch: ${{INGESTION_BATCH}}"

                python /app/observability/metrics/dq_runner.py \
                  --layer staging \
                  --sql-file /app/database/tests/005_staging_data_quality.sql \
                  --ingestion-batch "${{INGESTION_BATCH}}"

                echo "STAGING validation completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        load_oltp_task = KubernetesPodOperator(
            task_id="load_oltp",
            name="real-estate-load-oltp",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                """
                set -e

                export INGESTION_BATCH="generated-{{ ts_nodash }}"

                echo "============================================================"
                echo "SILVER - STAGING -> OLTP"
                echo "============================================================"
                echo "Ingestion batch: ${INGESTION_BATCH}"

                echo ""
                echo "------------------------------------------------------------"
                echo "1/2 - Loading generated searches"
                echo "STAGING recherches -> DEMANDE / DEMANDE_VERSION"
                echo "------------------------------------------------------------"

                python /app/database/seeds/load_staging_recherches_to_oltp.py

                echo ""
                echo "------------------------------------------------------------"
                echo "2/2 - Loading generated listings"
                echo "STAGING annonces -> BIEN"
                echo "------------------------------------------------------------"

                python /app/database/seeds/load_staging_to_oltp.py

                echo ""
                echo "OLTP load completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        validate_oltp_task = KubernetesPodOperator(
            task_id="validate_oltp",
            name="real-estate-validate-oltp",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                f"""
                set -e

                export INGESTION_BATCH="generated-{{{{ ts_nodash }}}}"
                export PUSHGATEWAY_URL="{PUSHGATEWAY_URL}"
                export PUSHGATEWAY_JOB="real_estate_data_quality"

                echo "============================================================"
                echo "SILVER - OLTP DATA QUALITY"
                echo "============================================================"
                echo "Ingestion batch: ${{INGESTION_BATCH}}"

                python /app/observability/metrics/dq_runner.py \
                  --layer oltp \
                  --sql-file /app/database/tests/006_oltp_data_quality.sql \
                  --ingestion-batch "${{INGESTION_BATCH}}"

                echo "OLTP validation completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        (
            transform_staging_task
            >> validate_staging_task
            >> load_oltp_task
            >> validate_oltp_task
        )

    # =========================================================================
    # GOLD
    #
    # Physical layers:
    #   - PostgreSQL warehouse schema
    #   - PostgreSQL analytics schema
    #   - dbt staging/marts
    #
    # Responsibilities:
    #   - Populate analytical dimensions/facts
    #   - Validate OLTP -> Warehouse reconciliation
    #   - Execute dbt transformations
    #   - Validate analytical models
    # =========================================================================

    with TaskGroup(
        group_id="gold",
        tooltip="GOLD - Warehouse and dbt analytics",
        prefix_group_id=False,
    ) as gold_group:

        load_warehouse_task = KubernetesPodOperator(
            task_id="load_warehouse",
            name="real-estate-load-warehouse",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                """
                set -e

                export INGESTION_BATCH="generated-{{ ts_nodash }}"

                echo "============================================================"
                echo "GOLD - OLTP -> WAREHOUSE"
                echo "============================================================"
                echo "Ingestion batch: ${INGESTION_BATCH}"

                python /app/database/olap/load_warehouse.py

                echo "WAREHOUSE load completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        validate_warehouse_task = KubernetesPodOperator(
            task_id="validate_warehouse",
            name="real-estate-validate-warehouse",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                f"""
                set -e

                export PUSHGATEWAY_URL="{PUSHGATEWAY_URL}"
                export PUSHGATEWAY_JOB="real_estate_data_quality"

                echo "============================================================"
                echo "GOLD - WAREHOUSE DATA QUALITY"
                echo "============================================================"

                python /app/observability/metrics/dq_runner.py \
                  --layer warehouse \
                  --sql-file /app/database/tests/007_warehouse_data_quality.sql

                echo "WAREHOUSE validation completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        dbt_run_task = KubernetesPodOperator(
            task_id="dbt_run",
            name="real-estate-dbt-run",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                """
                set -e

                echo "============================================================"
                echo "GOLD - DBT RUN"
                echo "============================================================"

                echo "Preparing dbt profile..."

                cp /app/pipelines/dbt/profiles.yml.example \
                   /app/pipelines/dbt/profiles.yml

                cd /app/pipelines/dbt

                echo "Running dbt models..."

                dbt run \
                  --profiles-dir .

                echo "dbt run completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        dbt_test_task = KubernetesPodOperator(
            task_id="dbt_test",
            name="real-estate-dbt-test",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                """
                set -e

                echo "============================================================"
                echo "GOLD - DBT TEST"
                echo "============================================================"

                echo "Preparing dbt profile..."

                cp /app/pipelines/dbt/profiles.yml.example \
                   /app/pipelines/dbt/profiles.yml

                cd /app/pipelines/dbt

                echo "Running dbt tests..."

                dbt test \
                  --profiles-dir .

                echo "dbt tests completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

        (
            load_warehouse_task
            >> validate_warehouse_task
            >> dbt_run_task
            >> dbt_test_task
        )

    # =========================================================================
    # OBSERVABILITY
    #
    # Responsibilities:
    #   - Collect platform data volumes
    #   - Collect OLTP/business KPIs
    #   - Collect warehouse/analytics KPIs
    #   - Push metrics to Prometheus Pushgateway
    #
    # DQ status metrics themselves are pushed by dq_runner.py immediately
    # after each DQ validation, including when a validation fails.
    # =========================================================================

    with TaskGroup(
        group_id="observability",
        tooltip="Platform metrics and observability",
        prefix_group_id=False,
    ) as observability_group:

        collect_metrics_task = KubernetesPodOperator(
            task_id="collect_metrics",
            name="real-estate-collect-metrics",
            namespace=AIRFLOW_NAMESPACE,
            image=DATA_PIPELINE_IMAGE,
            image_pull_secrets=IMAGE_PULL_SECRETS,
            cmds=["/bin/sh", "-c"],
            arguments=[
                f"""
                set -e

                echo "============================================================"
                echo "OBSERVABILITY - COLLECT PLATFORM METRICS"
                echo "============================================================"

                export PUSHGATEWAY_URL="{PUSHGATEWAY_URL}"
                export PUSHGATEWAY_JOB="real_estate_data_platform"

                cd /app/observability/metrics

                python collect_metrics.py

                echo "Real Estate metrics collection completed."
                """
            ],
            env_from=POSTGRES_ENV,
            get_logs=True,
            is_delete_operator_pod=True,
        )

    # =========================================================================
    # END
    # =========================================================================

    end = EmptyOperator(
        task_id="end",
    )

    # =========================================================================
    # GLOBAL PIPELINE
    #
    # BRONZE
    #   Source -> MinIO -> RAW
    #
    # SILVER
    #   RAW -> STAGING
    #       -> DEMANDE / DEMANDE_VERSION
    #       -> BIEN
    #
    # GOLD
    #   OLTP -> WAREHOUSE -> DBT -> ANALYTICS
    #
    # OBSERVABILITY
    #   Prometheus / Pushgateway metrics
    # =========================================================================

    (
        start
        >> bronze_group
        >> silver_group
        >> gold_group
        >> observability_group
        >> end
    )