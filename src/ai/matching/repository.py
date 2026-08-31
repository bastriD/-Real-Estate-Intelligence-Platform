from __future__ import annotations

from typing import Any

import pandas as pd
import psycopg
from psycopg.rows import dict_row


BIEN_COLUMNS = """
    id_bien,
    reference_externe,
    type_bien,
    ville,
    code_postal,
    latitude,
    longitude,
    prix,
    surface,
    nb_pieces,
    nb_chambres,
    dpe,
    statut,
    id_source
"""


def load_demande_version(
    connection: psycopg.Connection,
    id_demande_version: int,
) -> dict[str, Any]:
    sql = """
        SELECT
            id_demande_version,
            numero_version,
            date_version,
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
            active,
            id_demande
        FROM real_estate.demande_version
        WHERE id_demande_version = %s
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(sql, (id_demande_version,))
        row = cursor.fetchone()

    if row is None:
        raise ValueError(
            f"DemandeVersion {id_demande_version} does not exist."
        )

    return dict(row)


def load_candidate_biens(
    connection: psycopg.Connection,
    demande: dict[str, Any],
) -> pd.DataFrame:
    ville = demande.get("ville")

    if not ville:
        raise ValueError(
            "The demande version must contain a city before candidate retrieval."
        )

    sql = f"""
        SELECT
            {BIEN_COLUMNS}
        FROM real_estate.bien
        WHERE LOWER(TRIM(ville)) = LOWER(TRIM(%s))
          AND statut IS NOT NULL
        ORDER BY id_bien
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(sql, (ville,))
        rows = cursor.fetchall()

    return pd.DataFrame(rows)


def load_matching_input(
    connection: psycopg.Connection,
    id_demande_version: int,
) -> tuple[dict[str, Any], pd.DataFrame]:
    demande = load_demande_version(
        connection=connection,
        id_demande_version=id_demande_version,
    )

    biens = load_candidate_biens(
        connection=connection,
        demande=demande,
    )

    return demande, biens