from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

from prometheus_client import (
    CollectorRegistry,
    Gauge,
    push_to_gateway,
)


PUSHGATEWAY_URL = os.getenv(
    "PUSHGATEWAY_URL",
    "http://retail-pushgateway.monitoring.svc.cluster.local:9091",
)

PUSHGATEWAY_JOB = os.getenv(
    "PUSHGATEWAY_JOB",
    "real_estate_data_quality",
)


CHECK_COUNTS = {
    "raw": 10,
    "staging": 18,
    "oltp": 16,  # Includes the two sector reconciliation assertions in 021.
    "warehouse": 13,
}


MEDALLION_LAYERS = {
    "raw": "bronze",
    "staging": "silver",
    "oltp": "silver",
    "warehouse": "gold",
}


def publish_result(
    *,
    layer: str,
    success: bool,
) -> None:
    registry = CollectorRegistry()

    medallion = MEDALLION_LAYERS[layer]
    total = CHECK_COUNTS[layer]

    common_labels = [
        "medallion",
        "layer",
    ]

    layer_status = Gauge(
        "real_estate_dq_layer_status",
        "Status of the latest Data Quality validation by layer: 1=success, 0=failure",
        common_labels,
        registry=registry,
    )

    layer_checks_total = Gauge(
        "real_estate_dq_layer_checks_total",
        "Number of blocking Data Quality checks configured by layer",
        common_labels,
        registry=registry,
    )

    layer_checks_passed = Gauge(
        "real_estate_dq_layer_checks_passed",
        "Number of blocking Data Quality checks passed by layer",
        common_labels,
        registry=registry,
    )

    layer_checks_failed = Gauge(
        "real_estate_dq_layer_checks_failed",
        "Number of blocking Data Quality checks failed by layer",
        common_labels,
        registry=registry,
    )

    layer_last_run_timestamp = Gauge(
        "real_estate_dq_layer_last_run_timestamp",
        "Unix timestamp of the latest Data Quality validation by layer",
        common_labels,
        registry=registry,
    )

    labels = {
        "medallion": medallion,
        "layer": layer,
    }

    layer_status.labels(**labels).set(
        1 if success else 0
    )

    layer_checks_total.labels(**labels).set(total)

    if success:
        layer_checks_passed.labels(**labels).set(total)
        layer_checks_failed.labels(**labels).set(0)
    else:
        layer_checks_passed.labels(**labels).set(0)
        layer_checks_failed.labels(**labels).set(1)

    layer_last_run_timestamp.labels(
        **labels
    ).set(time.time())

    push_to_gateway(
        gateway=PUSHGATEWAY_URL,
        job=PUSHGATEWAY_JOB,
        grouping_key={
            "medallion": medallion,
            "layer": layer,
        },
        registry=registry,
    )


def build_command(
    *,
    sql_file: str,
    ingestion_batch: str | None,
) -> list[str]:
    command = [
        "psql",
        "-h",
        os.environ["POSTGRES_HOST"],
        "-p",
        os.environ["POSTGRES_PORT"],
        "-U",
        os.environ["POSTGRES_USER"],
        "-d",
        os.environ["POSTGRES_DB"],
        "-v",
        "ON_ERROR_STOP=1",
    ]

    if ingestion_batch:
        command.extend(
            [
                "-v",
                f"ingestion_batch={ingestion_batch}",
            ]
        )

    command.extend(
        [
            "-f",
            sql_file,
        ]
    )

    return command


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--layer",
        required=True,
        choices=CHECK_COUNTS.keys(),
    )

    parser.add_argument(
        "--sql-file",
        required=True,
    )

    parser.add_argument(
        "--ingestion-batch",
        required=False,
    )

    args = parser.parse_args()

    env = os.environ.copy()
    env["PGPASSWORD"] = os.environ["POSTGRES_PASSWORD"]

    command = build_command(
        sql_file=args.sql_file,
        ingestion_batch=args.ingestion_batch,
    )

    medallion = MEDALLION_LAYERS[args.layer]

    print(
        f"Running {medallion.upper()} / "
        f"{args.layer.upper()} Data Quality validation..."
    )

    result = subprocess.run(
        command,
        env=env,
        check=False,
    )

    success = result.returncode == 0

    try:
        publish_result(
            layer=args.layer,
            success=success,
        )

        print(
            f"{medallion.upper()} / "
            f"{args.layer.upper()} DQ metrics pushed successfully."
        )

    except Exception as exc:
        print(
            f"WARNING: unable to publish DQ metrics: {exc}",
            file=sys.stderr,
        )

    if success:
        print(
            f"{medallion.upper()} / "
            f"{args.layer.upper()} Data Quality validation PASSED."
        )
    else:
        print(
            f"{medallion.upper()} / "
            f"{args.layer.upper()} Data Quality validation FAILED.",
            file=sys.stderr,
        )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
