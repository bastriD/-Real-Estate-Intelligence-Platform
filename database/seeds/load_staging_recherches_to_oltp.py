#!/usr/bin/env python3

"""
load_staging_recherches_to_oltp.py

Load validated generated STAGING searches into the normalized OLTP model.

Source:
    staging.recherches

Targets:
    real_estate.demande
    real_estate.demande_version

Required environment variables:
    POSTGRES_HOST
    POSTGRES_PORT
    POSTGRES_DB
    POSTGRES_USER
    POSTGRES_PASSWORD
    INGESTION_BATCH

Principles:
    - Only quality_valid = TRUE searches are loaded.
    - Generated searches are legitimate pre-mandate demandes.
    - No synthetic mandate is created.
    - Generator reference is preserved for lineage.
    - Loading is idempotent.
    - Existing generated searches are updated, not duplicated.
    - JSONB values are explicitly adapted through psycopg Jsonb.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


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


def fetch_staging_recherches(
    connection: psycopg.Connection,
    batch: str,
) -> list[dict[str, Any]]:

    query = """
        SELECT
            staging_id,
            raw_id,
            legacy_generated_id,
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
            ingestion_batch,
            source_file
        FROM staging.recherches
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


def normalize_jsonb(value: Any) -> Jsonb:
    """
    Explicitly adapt Python values to PostgreSQL JSONB.

    psycopg returns a PostgreSQL JSONB array as a Python list.
    Passing that list directly as a SQL parameter makes psycopg
    adapt it as a PostgreSQL ARRAY, for example:

        {lumineux,parking}

    That representation is not valid JSON.

    Jsonb forces the value to be serialized correctly as JSON:

        ["lumineux", "parking"]
    """

    if value is None:
        value = []

    return Jsonb(value)


def ensure_demande(
    connection: psycopg.Connection,
    row: dict[str, Any],
) -> int:

    reference = row["reference"]

    if not reference:
        raise RuntimeError(
            "Generated recherche has no reference"
        )

    reference_demande = (
        f"GENERATED-DEMANDE-{reference}"
    )

    select_query = """
        SELECT id_demande
        FROM real_estate.demande
        WHERE reference_demande = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(
            select_query,
            (reference_demande,),
        )

        result = cursor.fetchone()

        if result is not None:
            return int(result[0])

    insert_query = """
        INSERT INTO real_estate.demande (
            reference_demande,
            date_creation,
            statut,
            id_mandat,
            origine
        )
        VALUES (
            %s,
            COALESCE(%s::date, CURRENT_DATE),
            'ACTIVE',
            NULL,
            'GENERATED'
        )
        RETURNING id_demande
    """

    with connection.cursor() as cursor:
        cursor.execute(
            insert_query,
            (
                reference_demande,
                row["date_creation"],
            ),
        )

        result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            f"Unable to create demande for {reference}"
        )

    return int(result[0])


def upsert_demande_version(
    connection: psycopg.Connection,
    row: dict[str, Any],
    id_demande: int,
    batch: str,
) -> int:

    source_ref = row["reference"]

    criteres_souhaites = normalize_jsonb(
        row["criteres_souhaites"]
    )

    select_query = """
        SELECT
            id_demande_version
        FROM real_estate.demande_version
        WHERE source_recherche_ref = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(
            select_query,
            (source_ref,),
        )

        existing = cursor.fetchone()

    if existing is not None:
        id_demande_version = int(
            existing[0]
        )

        update_query = """
            UPDATE real_estate.demande_version
            SET
                ville = %s,
                code_postal = %s,
                type_bien = %s,
                budget_min = NULL,
                budget_max = %s,
                surface_min = %s,
                nb_pieces_min = %s,
                nb_chambres_min = %s,
                dpe_max = %s,
                criteres_souhaites = %s,
                ingestion_batch = %s,
                motif_modification =
                    'Mise à jour données synthétiques générées'
            WHERE id_demande_version = %s
        """

        with connection.cursor() as cursor:
            cursor.execute(
                update_query,
                (
                    row["ville"],
                    row["code_postal"],
                    row["type_bien"],
                    row["budget_max"],
                    row["surface_min"],
                    row["nb_pieces_min"],
                    row["nb_chambres_min"],
                    row["dpe_max"],
                    criteres_souhaites,
                    batch,
                    id_demande_version,
                ),
            )

        return id_demande_version

    insert_query = """
        INSERT INTO real_estate.demande_version (
            numero_version,
            date_version,
            motif_modification,

            ville,
            code_postal,
            type_bien,

            budget_min,
            budget_max,
            surface_min,

            nb_pieces_min,
            nb_chambres_min,

            dpe_max,
            criteres_souhaites,

            description_recherche_legacy,

            active,

            id_demande,

            auteur_client_id,
            auteur_chasseur_id,
            auteur_systeme,

            source_recherche_ref,
            ingestion_batch
        )
        VALUES (
            1,
            CURRENT_TIMESTAMP,
            'Création depuis données synthétiques générées',

            %s,
            %s,
            %s,

            NULL,
            %s,
            %s,

            %s,
            %s,

            %s,
            %s,

            NULL,

            TRUE,

            %s,

            NULL,
            NULL,
            TRUE,

            %s,
            %s
        )
        RETURNING id_demande_version
    """

    with connection.cursor() as cursor:
        cursor.execute(
            insert_query,
            (
                row["ville"],
                row["code_postal"],
                row["type_bien"],
                row["budget_max"],
                row["surface_min"],
                row["nb_pieces_min"],
                row["nb_chambres_min"],
                row["dpe_max"],
                criteres_souhaites,
                id_demande,
                source_ref,
                batch,
            ),
        )

        result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            f"Unable to create demande_version for {source_ref}"
        )

    return int(result[0])


def validate_batch(
    connection: psycopg.Connection,
    batch: str,
) -> None:

    query = """
        SELECT
            (
                SELECT COUNT(*)
                FROM staging.recherches
                WHERE ingestion_batch = %s
                  AND quality_valid = TRUE
            ) AS staging_valid,

            (
                SELECT COUNT(*)
                FROM real_estate.demande_version
                WHERE ingestion_batch = %s
                  AND source_recherche_ref IS NOT NULL
            ) AS oltp_versions
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                batch,
                batch,
            ),
        )

        result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            "Unable to validate recherche OLTP load"
        )

    staging_valid, oltp_versions = result

    if staging_valid != oltp_versions:
        raise RuntimeError(
            "STAGING/OLTP recherche reconciliation failed: "
            f"{staging_valid} STAGING vs "
            f"{oltp_versions} OLTP"
        )

    orphan_query = """
        SELECT COUNT(*)
        FROM real_estate.demande_version dv
        JOIN real_estate.demande d
          ON d.id_demande = dv.id_demande
        WHERE dv.ingestion_batch = %s
          AND dv.source_recherche_ref IS NOT NULL
          AND d.origine <> 'GENERATED'
    """

    with connection.cursor() as cursor:
        cursor.execute(
            orphan_query,
            (batch,),
        )

        invalid_origin = int(
            cursor.fetchone()[0]
        )

    if invalid_origin != 0:
        raise RuntimeError(
            f"{invalid_origin} generated search versions "
            "are linked to non-generated demandes"
        )

    print(
        f"PASS: {staging_valid} generated recherches "
        "reconciled STAGING -> OLTP"
    )


def validate_matching_ground_truth(
    connection: psycopg.Connection,
    batch: str,
) -> None:

    query = """
        SELECT
            COUNT(*) AS total_recherches,

            COUNT(*) FILTER (
                WHERE matching_annonces > 0
            ) AS recherches_with_matches

        FROM (
            SELECT
                sr.reference,

                COUNT(sa.staging_id)
                FILTER (
                    WHERE sa.quality_valid = TRUE
                ) AS matching_annonces

            FROM staging.recherches sr

            LEFT JOIN staging.annonces sa
              ON sa.recherche_ref = sr.reference
             AND sa.ingestion_batch = sr.ingestion_batch

            WHERE sr.ingestion_batch = %s
              AND sr.quality_valid = TRUE

            GROUP BY sr.reference
        ) q
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (batch,),
        )

        result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            "Unable to validate generated matching ground truth"
        )

    total_recherches = int(result[0])
    recherches_with_matches = int(result[1])

    if total_recherches == 0:
        raise RuntimeError(
            "No generated recherches found"
        )

    if total_recherches != recherches_with_matches:
        raise RuntimeError(
            "Generated matching validation failed: "
            f"{recherches_with_matches}/{total_recherches} "
            "recherches have generated annonces"
        )

    print(
        "PASS: every generated recherche has "
        "at least one generated annonce"
    )


def main() -> int:

    batch = require_env(
        "INGESTION_BATCH"
    )

    print(
        f"Loading generated STAGING recherches -> OLTP: {batch}"
    )

    try:
        with psycopg.connect(
            connection_string()
        ) as connection:

            rows = fetch_staging_recherches(
                connection,
                batch,
            )

            if not rows:
                raise RuntimeError(
                    f"No valid staging recherches found "
                    f"for batch {batch}"
                )

            print(
                f"Valid staging recherches: {len(rows)}"
            )

            created_or_updated = 0

            for row in rows:

                id_demande = ensure_demande(
                    connection,
                    row,
                )

                id_demande_version = (
                    upsert_demande_version(
                        connection,
                        row,
                        id_demande,
                        batch,
                    )
                )

                print(
                    f"RECHERCHE {row['reference']} "
                    f"-> demande={id_demande} "
                    f"demande_version={id_demande_version}"
                )

                created_or_updated += 1

            validate_batch(
                connection,
                batch,
            )

            validate_matching_ground_truth(
                connection,
                batch,
            )

            connection.commit()

    except Exception as exc:
        print(
            f"ERROR: STAGING recherches -> OLTP failed: {exc}",
            file=sys.stderr,
        )

        return 1

    print(
        f"Processed generated recherches: "
        f"{created_or_updated}"
    )

    print(
        "STAGING recherches -> OLTP completed successfully."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())