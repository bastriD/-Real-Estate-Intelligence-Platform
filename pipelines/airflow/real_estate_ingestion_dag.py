from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s


DAG_ID = "real_estate_ingestion"

DEFAULT_ARGS = {
    "owner": "real-estate",
    "depends_on_past": False,
    "retries": 1,
}


def validate_raw() -> None:
    """
    Placeholder.

    Later:
    - validate expected source counts
    - validate mandatory matching fields
    - detect duplicate references
    - record DQ metrics
    """
    print("validate_raw")


def transform_staging() -> None:
    """
    Placeholder.

    Later:
    - parse heterogeneous date formats
    - normalize price
    - normalize surface / surface_m2
    - normalize booleans
    - normalize DPE
    - normalize contact fields
    - preserve quality errors
    """
    print("transform_staging")


def validate_staging() -> None:
    """
    Placeholder.

    Later:
    - validate typed fields
    - check rejected/invalid rows
    - verify reconciliation RAW -> STAGING
    """
    print("validate_staging")


def load_oltp() -> None:
    """
    Placeholder.

    Later:
    - create/update source records
    - load clean staging announcements into real_estate.bien
    - preserve source/reference traceability
    """
    print("load_oltp")


def validate_oltp() -> None:
    """
    Placeholder.

    Later:
    - validate row counts
    - validate FK integrity
    - validate unique source/reference pairs
    - run matching-oriented DQ checks
    """
    print("validate_oltp")


with DAG(
    dag_id=DAG_ID,
    description="Real Estate RAW -> STAGING -> OLTP ingestion pipeline",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 8, 1),
    schedule=None,
    catchup=False,
    tags=[
        "real-estate",
        "data-engineering",
        "postgresql",
        "oltp",
    ],
) as dag:

    start = EmptyOperator(
        task_id="start",
    )

    generate_source_data_task = KubernetesPodOperator(
        task_id="generate_source_data",
        name="real-estate-generate-source-data",
        namespace="airflow",
        image="gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest",

        image_pull_secrets=[
            k8s.V1LocalObjectReference(
                name="gitlab-registry"
            )
        ],

        cmds=["/bin/sh", "-c"],

        arguments=[
            """
            set -e

            export INGESTION_BATCH="generated-{{ ts_nodash }}"

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

        env_from=[
            k8s.V1EnvFromSource(
                secret_ref=k8s.V1SecretEnvSource(
                    name="real-estate-s3"
                )
            )
        ],

        get_logs=True,
        is_delete_operator_pod=True,
    )

    load_raw_task = KubernetesPodOperator(
        task_id="load_raw",
        name="real-estate-load-raw",
        namespace="airflow",
        image="gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest",

        image_pull_secrets=[
            k8s.V1LocalObjectReference(
                name="gitlab-registry"
            )
        ],

        cmds=["/bin/sh", "-c"],

        arguments=[
            """
            set -e

            export INGESTION_BATCH="generated-{{ ts_nodash }}"

            echo "Downloading generated CSVs from MinIO..."

            python /app/database/seeds/download_generated_from_s3.py

            echo "Loading RAW PostgreSQL tables..."

            python /app/database/seeds/load_raw_generated_data.py

            echo "RAW load completed."
            """
        ],

        env_from=[
            k8s.V1EnvFromSource(
                secret_ref=k8s.V1SecretEnvSource(
                    name="real-estate-s3"
                )
            ),
            k8s.V1EnvFromSource(
                secret_ref=k8s.V1SecretEnvSource(
                    name="real-estate-postgresql-secret"
                )
            ),
        ],

        get_logs=True,
        is_delete_operator_pod=True,
    )

    validate_raw_task = KubernetesPodOperator(
    task_id="validate_raw",
    name="real-estate-validate-raw",
    namespace="airflow",
    image="gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest",

    image_pull_secrets=[
        k8s.V1LocalObjectReference(
            name="gitlab-registry"
        )
    ],

    cmds=["/bin/sh", "-c"],

    arguments=[
        """
        set -e

        export INGESTION_BATCH="generated-{{ ts_nodash }}"

        echo "Validating RAW batch: ${INGESTION_BATCH}"

        PGPASSWORD="${POSTGRES_PASSWORD}" \
        psql \
          -h "${POSTGRES_HOST}" \
          -p "${POSTGRES_PORT}" \
          -U "${POSTGRES_USER}" \
          -d "${POSTGRES_DB}" \
          -v ON_ERROR_STOP=1 \
          -v ingestion_batch="${INGESTION_BATCH}" \
          -f /app/database/tests/004_raw_data_quality.sql

        echo "RAW validation completed."
        """
    ],

    env_from=[
        k8s.V1EnvFromSource(
            secret_ref=k8s.V1SecretEnvSource(
                name="real-estate-postgresql-secret"
            )
        )
    ],

    get_logs=True,
    is_delete_operator_pod=True,
)

    transform_staging_task = KubernetesPodOperator(
    task_id="transform_staging",
    name="real-estate-transform-staging",
    namespace="airflow",
    image="gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest",

    image_pull_secrets=[
        k8s.V1LocalObjectReference(
            name="gitlab-registry"
        )
    ],

    cmds=["/bin/sh", "-c"],

    arguments=[
        """
        set -e

        export INGESTION_BATCH="generated-{{ ts_nodash }}"

        echo "Transforming RAW -> STAGING batch: ${INGESTION_BATCH}"

        python /app/database/seeds/transform_raw_to_staging.py

        echo "STAGING transformation completed."
        """
    ],

    env_from=[
        k8s.V1EnvFromSource(
            secret_ref=k8s.V1SecretEnvSource(
                name="real-estate-postgresql-secret"
            )
        )
    ],

    get_logs=True,
    is_delete_operator_pod=True,
)

    validate_staging_task = PythonOperator(
        task_id="validate_staging",
        python_callable=validate_staging,
    )

    load_oltp_task = PythonOperator(
        task_id="load_oltp",
        python_callable=load_oltp,
    )

    validate_oltp_task = PythonOperator(
        task_id="validate_oltp",
        python_callable=validate_oltp,
    )

    end = EmptyOperator(
        task_id="end",
    )

    (
        start
        >> generate_source_data_task
        >> load_raw_task
        >> validate_raw_task
        >> transform_staging_task
        >> validate_staging_task
        >> load_oltp_task
        >> validate_oltp_task
        >> end
    )