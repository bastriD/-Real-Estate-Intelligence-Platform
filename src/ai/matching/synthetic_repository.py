from __future__ import annotations

from typing import Any

import pandas as pd
import psycopg
from psycopg.rows import dict_row


SYNTHETIC_ANNONCE_COLUMNS = """
    staging_id,
    reference,
    recherche_ref,
    type_bien,
    ville,
    code_postal,
    prix,
    surface,
    nb_pieces,
    nb_chambres,
    dpe,
    latitude,
    longitude,
    quality_valid,
    ingestion_batch
"""


def load_generated_searches(
    connection: psycopg.Connection,
) -> pd.DataFrame:
    """
    Load all valid generated searches available in staging.

    These searches are synthetic validation data. They must not be
    interpreted as real customer DemandeVersion records.
    """
    sql = """
        SELECT
            staging_id,
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
            ingestion_batch
        FROM staging.recherches
        WHERE quality_valid = TRUE
        ORDER BY staging_id
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    return pd.DataFrame(rows)


def load_generated_search(
    connection: psycopg.Connection,
    reference: str,
) -> dict[str, Any]:
    """
    Load one valid generated search and adapt it to the canonical
    structure expected by the deterministic matching feature engine.
    """
    sql = """
        SELECT
            staging_id,
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
            ingestion_batch
        FROM staging.recherches
        WHERE reference = %s
          AND quality_valid = TRUE
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(sql, (reference,))
        row = cursor.fetchone()

    if row is None:
        raise ValueError(
            f"Generated search {reference!r} does not exist "
            "or is not quality-valid."
        )

    search = dict(row)

    # The generated search format currently defines only a maximum budget.
    # The matching engine supports a missing lower bound.
    search["budget_min"] = None

    return search


def load_linked_generated_annonces(
    connection: psycopg.Connection,
    reference: str,
) -> pd.DataFrame:
    """
    Load quality-valid generated announcements explicitly linked to a
    generated search through staging.annonces.recherche_ref.

    This provenance relationship comes directly from the generator and
    represents synthetic correspondence, not real customer feedback.
    """
    sql = f"""
        SELECT
            {SYNTHETIC_ANNONCE_COLUMNS}
        FROM staging.annonces
        WHERE recherche_ref = %s
          AND quality_valid = TRUE
        ORDER BY staging_id
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(sql, (reference,))
        rows = cursor.fetchall()

    return pd.DataFrame(rows)


def load_all_generated_annonces(
    connection: psycopg.Connection,
) -> pd.DataFrame:
    """
    Load all quality-valid generated announcements.

    This dataset is intended for later retrieval/ranking evaluation where
    a generated search is evaluated against the complete synthetic corpus.
    """
    sql = f"""
        SELECT
            {SYNTHETIC_ANNONCE_COLUMNS}
        FROM staging.annonces
        WHERE quality_valid = TRUE
        ORDER BY staging_id
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    return pd.DataFrame(rows)


def load_generated_matching_input(
    connection: psycopg.Connection,
    reference: str,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """
    Load one generated search and its explicitly linked announcements.

    The returned objects use the same field names consumed by
    build_matching_features(), allowing the deterministic feature and
    scoring implementation to be reused without staging-specific logic.
    """
    search = load_generated_search(
        connection=connection,
        reference=reference,
    )

    annonces = load_linked_generated_annonces(
        connection=connection,
        reference=reference,
    )

    return search, annonces