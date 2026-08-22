#!/usr/bin/env python3

from __future__ import annotations

import os
from pathlib import Path

import boto3


PROJECT_ROOT = Path(__file__).resolve().parents[2]

GENERATED_ROOT = (
    PROJECT_ROOT
    / "database"
    / "fixtures"
    / "annonces"
)


def require_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


def main() -> int:
    endpoint = require_env("S3_ENDPOINT_URL")
    bucket = require_env("S3_BUCKET")

    access_key = require_env("AWS_ACCESS_KEY_ID")
    secret_key = require_env("AWS_SECRET_ACCESS_KEY")
    region = require_env("AWS_DEFAULT_REGION")

    batch = require_env("INGESTION_BATCH")

    if not GENERATED_ROOT.exists():
        raise FileNotFoundError(
            f"Generated data directory not found: {GENERATED_ROOT}"
        )

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )

    prefix = f"raw/generated/{batch}"

    uploaded = 0

    for path in GENERATED_ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(GENERATED_ROOT)

        object_key = (
            f"{prefix}/"
            f"{relative_path.as_posix()}"
        )

        client.upload_file(
            str(path),
            bucket,
            object_key,
        )

        print(
            f"UPLOADED: "
            f"s3://{bucket}/{object_key}"
        )

        uploaded += 1

    if uploaded == 0:
        raise RuntimeError(
            "No generated files were uploaded"
        )

    print(
        f"PASS: {uploaded} files uploaded "
        f"to s3://{bucket}/{prefix}/"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())