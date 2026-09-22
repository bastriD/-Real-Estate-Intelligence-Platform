#!/usr/bin/env python3

"""
load_staging_to_oltp.py

Load validated STAGING announcements into the normalized Real Estate OLTP model.

Source:
    staging.annonces

Target:
    real_estate.source
    real_estate.bien

Required environment variables:
    POSTGRES_HOST
    POSTGRES_PORT
    POSTGRES_DB
    POSTGRES_USER
    POSTGRES_PASSWORD
    INGESTION_BATCH

Principles:
    - Only quality_valid = TRUE staging rows are loaded.
    - A stable synthetic source is created/reused for generated fixtures.
    - Property identity is based on:
          (id_source, reference_externe)
    - Reruns update existing properties instead of creating duplicates.
    - No destructive delete is performed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv

if __package__:
    from .sector_contract import load_catalogue, resolve_sector, assign_property_sectors
else:
    from sector_contract import load_catalogue, resolve_sector, assign_property_sectors


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


SOURCE_NAME = "GENERATEUR_ANNONCES"
SOURCE_TYPE = "AUTRE"
SOURCE_CONFIDENCE = "MOYEN"


# =============================================================================
# ENVIRONMENT
# =============================================================================


def require_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


def connection_string() -> str:
    return (
        f"host={require_env('POSTGRES_HOST')} "
        f"port={require_env('POSTGRES_PORT')} "
        f"dbname={require_env('POSTGRES_DB')} "
        f"user={require_env('POSTGRES_USER')} "
        f"password={require_env('POSTGRES_PASSWORD')}"
    )


# =============================================================================
# SOURCE
# =============================================================================


def get_or_create_source(
    connection: psycopg.Connection,
    batch: str,
) -> int:
    """
    Return the id_source for the generated-announcement source.

    The source is stable across batches.
    """

    select_query = """
        SELECT id_source
        FROM real_estate.source
        WHERE nom = %s
          AND type_source = %s
        ORDER BY id_source
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(
            select_query,
            (
                SOURCE_NAME,
                SOURCE_TYPE,
            ),
        )

        row = cursor.fetchone()

        if row is not None:
            source_id = int(row[0])

            print(
                f"Source already exists: "
                f"id_source={source_id}"
            )

            return source_id

    insert_query = """
        INSERT INTO real_estate.source (
            nom,
            type_source,
            url_base,
            actif,
            niveau_confiance
        )
        VALUES (
            %s,
            %s,
            %s,
            TRUE,
            %s
        )
        RETURNING id_source
    """

    source_url = (
        "s3://real-estate/raw/generated/"
        f"{batch}/"
    )

    with connection.cursor() as cursor:
        cursor.execute(
            insert_query,
            (
                SOURCE_NAME,
                SOURCE_TYPE,
                source_url,
                SOURCE_CONFIDENCE,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Unable to create generated announcement source"
            )

        source_id = int(row[0])

    print(
        f"Created source: id_source={source_id}"
    )

    return source_id


# =============================================================================
# FETCH STAGING
# =============================================================================


def fetch_staging_annonces(
    connection: psycopg.Connection,
    batch: str,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            staging_id,
            secteur_code,
            raw_id,
            reference,
            type_bien,
            titre,
            adresse,
            code_postal,
            ville,
            latitude,
            longitude,
            prix,
            surface,
            nb_pieces,
            nb_chambres,
            dpe,
            description,
            date_publication
        FROM staging.annonces
        WHERE ingestion_batch = %s
          AND quality_valid = TRUE
        ORDER BY staging_id
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (batch,),
        )

        columns = [
            description.name
            for description in cursor.description
        ]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


# =============================================================================
# LOAD BIENS
# =============================================================================


def upsert_biens(
    connection: psycopg.Connection,
    rows: list[dict[str, Any]],
    source_id: int,
) -> tuple[int, int]:
    """
    Insert or update properties.

    Returns:
        (processed_rows, target_rows_for_source)
    """

    query = """
        INSERT INTO real_estate.bien (
            reference_externe,
            type_bien,
            titre,
            adresse,
            code_postal,
            ville,
            latitude,
            longitude,
            prix,
            surface,
            nb_pieces,
            nb_chambres,
            dpe,
            description,
            date_publication,
            date_collecte,
            statut,
            id_source
        )
        VALUES (
            %(reference)s,
            %(type_bien)s,
            %(titre)s,
            %(adresse)s,
            %(code_postal)s,
            %(ville)s,
            %(latitude)s,
            %(longitude)s,
            %(prix)s,
            %(surface)s,
            %(nb_pieces)s,
            %(nb_chambres)s,
            %(dpe)s,
            %(description)s,
            %(date_publication)s,
            CURRENT_TIMESTAMP,
            'ACTIF',
            %(id_source)s
        )

        ON CONFLICT (id_source, reference_externe)
        DO UPDATE SET
            type_bien = EXCLUDED.type_bien,
            titre = EXCLUDED.titre,
            adresse = EXCLUDED.adresse,
            code_postal = EXCLUDED.code_postal,
            ville = EXCLUDED.ville,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            prix = EXCLUDED.prix,
            surface = EXCLUDED.surface,
            nb_pieces = EXCLUDED.nb_pieces,
            nb_chambres = EXCLUDED.nb_chambres,
            dpe = EXCLUDED.dpe,
            description = EXCLUDED.description,
            date_publication = EXCLUDED.date_publication,
            date_collecte = CURRENT_TIMESTAMP,
            statut = 'ACTIF'
    """

    prepared_rows: list[dict[str, Any]] = []

    catalogue = load_catalogue(connection) if any(row.get("secteur_code") for row in rows) else {}

    for row in rows:
        prepared = dict(row)
        prepared["id_source"] = source_id
        prepared["id_secteur"] = resolve_sector(row, catalogue)

        prepared_rows.append(
            prepared
        )

    with connection.cursor() as cursor:
        cursor.executemany(
            query,
            prepared_rows,
        )

    assign_property_sectors(connection, prepared_rows, source_id)

    count_query = """
        SELECT COUNT(*)
        FROM real_estate.bien
        WHERE id_source = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            count_query,
            (source_id,),
        )

        target_count = int(
            cursor.fetchone()[0]
        )

    return (
        len(prepared_rows),
        target_count,
    )


# =============================================================================
# VALIDATION
# =============================================================================


def validate_batch_load(
    connection: psycopg.Connection,
    batch: str,
    source_id: int,
) -> None:
    """
    Validate that every valid staging reference exists in real_estate.bien.
    """

    query = """
        SELECT COUNT(*)
        FROM staging.annonces s
        LEFT JOIN real_estate.bien b
          ON b.reference_externe = s.reference
         AND b.id_source = %s
        WHERE s.ingestion_batch = %s
          AND s.quality_valid = TRUE
          AND b.id_bien IS NULL
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                source_id,
                batch,
            ),
        )

        missing = int(
            cursor.fetchone()[0]
        )

    if missing != 0:
        raise RuntimeError(
            f"OLTP load reconciliation failed: "
            f"{missing} staging annonces missing "
            f"from real_estate.bien"
        )

    duplicate_query = """
        SELECT COUNT(*)
        FROM (
            SELECT
                id_source,
                reference_externe
            FROM real_estate.bien
            WHERE id_source = %s
            GROUP BY
                id_source,
                reference_externe
            HAVING COUNT(*) > 1
        ) duplicates
    """

    with connection.cursor() as cursor:
        cursor.execute(
            duplicate_query,
            (source_id,),
        )

        duplicates = int(
            cursor.fetchone()[0]
        )

    if duplicates != 0:
        raise RuntimeError(
            f"OLTP validation failed: "
            f"{duplicates} duplicate property references found"
        )

    staging_count_query = """
        SELECT COUNT(*)
        FROM staging.annonces
        WHERE ingestion_batch = %s
          AND quality_valid = TRUE
    """

    with connection.cursor() as cursor:
        cursor.execute(
            staging_count_query,
            (batch,),
        )

        staging_count = int(
            cursor.fetchone()[0]
        )

    matched_count_query = """
        SELECT COUNT(*)
        FROM staging.annonces s
        JOIN real_estate.bien b
          ON b.reference_externe = s.reference
         AND b.id_source = %s
        WHERE s.ingestion_batch = %s
          AND s.quality_valid = TRUE
    """

    with connection.cursor() as cursor:
        cursor.execute(
            matched_count_query,
            (
                source_id,
                batch,
            ),
        )

        matched_count = int(
            cursor.fetchone()[0]
        )

    if staging_count != matched_count:
        raise RuntimeError(
            "STAGING/OLTP reconciliation failed: "
            f"{staging_count} STAGING vs "
            f"{matched_count} OLTP matches"
        )

    print(
        f"PASS: {staging_count} validated staging annonces "
        f"reconciled with real_estate.bien"
    )

    print(
        "PASS: no duplicate "
        "(id_source, reference_externe) pairs"
    )


# =============================================================================
# MAIN
# =============================================================================


def main() -> int:
    batch = require_env(
        "INGESTION_BATCH"
    )

    print(
        f"Loading STAGING -> OLTP batch: {batch}"
    )

    try:
        with psycopg.connect(
            connection_string()
        ) as connection:

            staging_rows = fetch_staging_annonces(
                connection,
                batch,
            )

            if not staging_rows:
                raise RuntimeError(
                    f"No valid staging annonces found "
                    f"for batch {batch}"
                )

            print(
                f"Valid staging annonces: "
                f"{len(staging_rows)}"
            )

            source_id = get_or_create_source(
                connection,
                batch,
            )

            processed_rows, target_count = upsert_biens(
                connection,
                staging_rows,
                source_id,
            )

            print(
                f"UPSERTED: {processed_rows} annonces "
                f"into real_estate.bien"
            )

            print(
                f"Current biens for source "
                f"{source_id}: {target_count}"
            )

            validate_batch_load(
                connection,
                batch,
                source_id,
            )

            connection.commit()

    except Exception as exc:
        print(
            f"ERROR: STAGING -> OLTP load failed: {exc}",
            file=sys.stderr,
        )

        return 1

    print(
        "STAGING -> OLTP load completed successfully."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
