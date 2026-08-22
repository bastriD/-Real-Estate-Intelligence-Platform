#!/usr/bin/env python3

from __future__ import annotations

import os
from pathlib import Path

import boto3


PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCAL_ROOT = (
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

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )

    LOCAL_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    files = [
        "recherches.csv",
        "annonces.csv",
    ]

    for filename in files:
        object_key = (
            f"raw/generated/"
            f"{batch}/"
            f"{filename}"
        )

        local_path = LOCAL_ROOT / filename

        print(
            f"Downloading "
            f"s3://{bucket}/{object_key}"
        )

        client.download_file(
            bucket,
            object_key,
            str(local_path),
        )

        if not local_path.exists():
            raise RuntimeError(
                f"Download failed: {local_path}"
            )

        print(
            f"DOWNLOADED: {local_path}"
        )

    print(
        f"PASS: generated CSV dataset "
        f"{batch} downloaded successfully"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())