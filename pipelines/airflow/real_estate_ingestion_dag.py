from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


DAG_ID = "real_estate_ingestion"

DEFAULT_ARGS = {
    "owner": "real-estate",
    "depends_on_past": False,
    "retries": 1,
}


def generate_source_data() -> None:
    """
    Placeholder.

    Later:
    - execute database/seeds/generer_annonces.py
    - or consume already-generated source data
    """
    print("generate_source_data")


def load_raw() -> None:
    """
    Placeholder.

    Later:
    - load recherches.csv into raw.recherches
    - load annonces.csv into raw.annonces
    """
    print("load_raw")


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

    generate_source_data_task = PythonOperator(
        task_id="generate_source_data",
        python_callable=generate_source_data,
    )

    load_raw_task = PythonOperator(
        task_id="load_raw",
        python_callable=load_raw,
    )

    validate_raw_task = PythonOperator(
        task_id="validate_raw",
        python_callable=validate_raw,
    )

    transform_staging_task = PythonOperator(
        task_id="transform_staging",
        python_callable=transform_staging,
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