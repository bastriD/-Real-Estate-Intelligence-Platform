#!/usr/bin/env python3
"""
load_raw_generated_data.py

Load generated real-estate CSV fixtures into PostgreSQL RAW tables.

Inputs:
    database/fixtures/annonces/recherches.csv
    database/fixtures/annonces/annonces.csv

Targets:
    raw.recherches
    raw.annonces

Environment variables:
    POSTGRES_HOST
    POSTGRES_PORT
    POSTGRES_DB
    POSTGRES_USER
    POSTGRES_PASSWORD

Behavior:
    - Uses one ingestion_batch identifier for both files.
    - Maps flattened CSV names such as contact.nom -> contact_nom.
    - Preserves source values as TEXT.
    - Skips rows already loaded for the same source_file + ingestion_batch.
    - Uses transactions.
"""

#!/usr/bin/env python3

from __future__ import annotations

import csv
import os
import sys
import uuid
from pathlib import Path

import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


RECHERCHES_CSV = (
    PROJECT_ROOT / "database" / "fixtures" / "annonces" / "recherches.csv"
)

ANNONCES_CSV = (
    PROJECT_ROOT / "database" / "fixtures" / "annonces" / "annonces.csv"
)

RECHERCHES_COLUMNS = [
    "id",
    "reference",
    "date_creation",
    "ville",
    "code_postal",
    "type_bien",
    "budget_max",
    "surface_min",
    "criteres_souhaites",
    "nb_pieces_min",
    "nb_chambres_min",
    "dpe_max",
]


ANNONCES_MAPPING = {
    "id": "id",
    "reference": "reference",
    "recherche_ref": "recherche_ref",
    "type_bien": "type_bien",
    "titre": "titre",
    "ville": "ville",
    "code_postal": "code_postal",
    "date_publication": "date_publication",
    "prix": "prix",
    "surface": "surface",
    "nb_pieces": "nb_pieces",
    "nb_chambres": "nb_chambres",
    "meuble": "meuble",
    "dpe": "dpe",
    "description": "description",
    "terrasse": "terrasse",
    "calme": "calme",
    "contact.nom": "contact_nom",
    "contact.telephone": "contact_telephone",
    "contact.email": "contact_email",
    "contact.agence": "contact_agence",
    "photos": "photos",
    "exclusivite": "exclusivite",
    "particulier": "particulier",
    "surface_m2": "surface_m2",
    "annee_construction": "annee_construction",
    "adresse": "adresse",
    "latitude": "latitude",
    "longitude": "longitude",
    "etage": "etage",
    "charges_mensuelles": "charges_mensuelles",
    "vue": "vue",
    "jardin": "jardin",
}


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def connection_string() -> str:
    host = require_env("POSTGRES_HOST")
    port = require_env("POSTGRES_PORT")
    database = require_env("POSTGRES_DB")
    user = require_env("POSTGRES_USER")
    password = require_env("POSTGRES_PASSWORD")

    return (
        f"host={host} "
        f"port={port} "
        f"dbname={database} "
        f"user={user} "
        f"password={password}"
    )


def normalize_value(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    return value


def read_csv(path: Path) -> list[dict[str, str | None]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file_handle:
        reader = csv.DictReader(file_handle)

        rows: list[dict[str, str | None]] = []

        for raw_row in reader:
            rows.append(
                {
                    key: normalize_value(value)
                    for key, value in raw_row.items()
                }
            )

        return rows


def batch_already_loaded(
    connection: psycopg.Connection,
    table_name: str,
    source_file: str,
    ingestion_batch: str,
) -> bool:
    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM {table_name}
            WHERE source_file = %s
              AND ingestion_batch = %s
        )
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                source_file,
                ingestion_batch,
            ),
        )

        result = cursor.fetchone()

    return bool(result and result[0])


def load_recherches(
    connection: psycopg.Connection,
    ingestion_batch: str,
) -> int:
    source_file = str(RECHERCHES_CSV.relative_to(PROJECT_ROOT))

    if batch_already_loaded(
        connection,
        "raw.recherches",
        source_file,
        ingestion_batch,
    ):
        print(
            f"SKIP: {source_file} already loaded "
            f"for batch {ingestion_batch}"
        )
        return 0

    rows = read_csv(RECHERCHES_CSV)

    insert_sql = """
        INSERT INTO raw.recherches (
            id,
            reference,
            date_creation,
            ville,
            code_postal,
            type_bien,
            budget_max,
            surface_min,
            criteres_souhaites,
            nb_pieces_min,
            nb_chambres_min,
            dpe_max,
            source_file,
            ingestion_batch
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s
        )
    """

    values = []

    for row in rows:
        values.append(
            tuple(row.get(column) for column in RECHERCHES_COLUMNS)
            + (
                source_file,
                ingestion_batch,
            )
        )

    with connection.cursor() as cursor:
        cursor.executemany(
            insert_sql,
            values,
        )

    print(
        f"LOADED: {len(rows)} rows into raw.recherches "
        f"for batch {ingestion_batch}"
    )

    return len(rows)


def load_annonces(
    connection: psycopg.Connection,
    ingestion_batch: str,
) -> int:
    source_file = str(ANNONCES_CSV.relative_to(PROJECT_ROOT))

    if batch_already_loaded(
        connection,
        "raw.annonces",
        source_file,
        ingestion_batch,
    ):
        print(
            f"SKIP: {source_file} already loaded "
            f"for batch {ingestion_batch}"
        )
        return 0

    rows = read_csv(ANNONCES_CSV)

    target_columns = list(ANNONCES_MAPPING.values())

    column_sql = ",\n            ".join(target_columns)

    placeholders = ", ".join(["%s"] * len(target_columns))

    insert_sql = f"""
        INSERT INTO raw.annonces (
            {column_sql},
            source_file,
            ingestion_batch
        )
        VALUES (
            {placeholders},
            %s,
            %s
        )
    """

    values = []

    for row in rows:
        mapped_values = tuple(
            row.get(source_column)
            for source_column in ANNONCES_MAPPING
        )

        values.append(
            mapped_values
            + (
                source_file,
                ingestion_batch,
            )
        )

    with connection.cursor() as cursor:
        cursor.executemany(
            insert_sql,
            values,
        )

    print(
        f"LOADED: {len(rows)} rows into raw.annonces "
        f"for batch {ingestion_batch}"
    )

    return len(rows)


def validate_loaded_counts(
    connection: psycopg.Connection,
    ingestion_batch: str,
) -> None:
    query = """
        SELECT
            (
                SELECT COUNT(*)
                FROM raw.recherches
                WHERE ingestion_batch = %s
            ) AS recherches_count,

            (
                SELECT COUNT(*)
                FROM raw.annonces
                WHERE ingestion_batch = %s
            ) AS annonces_count
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                ingestion_batch,
                ingestion_batch,
            ),
        )

        result = cursor.fetchone()

    if result is None:
        raise RuntimeError("Unable to validate RAW counts")

    recherches_count, annonces_count = result

    if recherches_count != 5:
        raise RuntimeError(
            f"Expected 5 RAW recherches, found {recherches_count}"
        )

    if annonces_count != 1000:
        raise RuntimeError(
            f"Expected 1000 RAW annonces, found {annonces_count}"
        )

    print("PASS: 5 RAW recherches loaded")
    print("PASS: 1000 RAW annonces loaded")


def main() -> int:
    ingestion_batch = os.getenv(
        "INGESTION_BATCH",
        f"generated-{uuid.uuid4()}",
    )

    print(f"Ingestion batch: {ingestion_batch}")
    print(f"Recherches source: {RECHERCHES_CSV}")
    print(f"Annonces source: {ANNONCES_CSV}")

    try:
        with psycopg.connect(connection_string()) as connection:
            load_recherches(
                connection,
                ingestion_batch,
            )

            load_annonces(
                connection,
                ingestion_batch,
            )

            validate_loaded_counts(
                connection,
                ingestion_batch,
            )

            connection.commit()

    except Exception as exc:
        print(
            f"ERROR: RAW ingestion failed: {exc}",
            file=sys.stderr,
        )
        return 1

    print("RAW ingestion completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())