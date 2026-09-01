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
            id_demande,
            source_recherche_ref,
            ingestion_batch
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
    """
    Retrieve operational matching candidates.

    Hard business constraints:
    - same city
    - same property type
    - price <= maximum budget
    - surface >= minimum surface

    Optional criteria such as postcode, room count, bedroom count and
    DPE are intentionally not applied here. They are ranking signals.
    """
    ville = demande.get("ville")
    type_bien = demande.get("type_bien")
    budget_max = demande.get("budget_max")
    surface_min = demande.get("surface_min")

    if not ville:
        raise ValueError(
            "The demande version must contain a city before candidate retrieval."
        )

    if not type_bien:
        raise ValueError(
            "The demande version must contain a property type "
            "before candidate retrieval."
        )

    if budget_max is None:
        raise ValueError(
            "The demande version must contain a maximum budget "
            "before candidate retrieval."
        )

    if surface_min is None:
        raise ValueError(
            "The demande version must contain a minimum surface "
            "before candidate retrieval."
        )

    sql = f"""
        SELECT
            {BIEN_COLUMNS}
        FROM real_estate.bien
        WHERE LOWER(TRIM(ville)) = LOWER(TRIM(%s))
          AND LOWER(TRIM(type_bien)) = LOWER(TRIM(%s))
          AND prix <= %s
          AND surface >= %s
          AND statut IS NOT NULL
        ORDER BY id_bien
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            sql,
            (
                ville,
                type_bien,
                budget_max,
                surface_min,
            ),
        )
        rows = cursor.fetchall()

    return pd.DataFrame(rows)


def load_ground_truth_references(
    connection: psycopg.Connection,
    source_recherche_ref: str,
) -> set[str]:
    """
    Load explicit synthetic ground-truth property references.

    Ground truth comes from generator provenance:

        demande_version.source_recherche_ref
            -> staging.annonces.recherche_ref
            -> staging.annonces.reference
            -> real_estate.bien.reference_externe

    This function exists exclusively for evaluation and training-data
    construction. Ground-truth lineage must never influence operational
    candidate retrieval or production ranking.
    """
    if not source_recherche_ref:
        return set()

    sql = """
        SELECT DISTINCT
            b.reference_externe
        FROM staging.annonces sa
        JOIN real_estate.bien b
          ON b.reference_externe = sa.reference
        WHERE sa.recherche_ref = %s
          AND sa.quality_valid = TRUE
          AND b.reference_externe IS NOT NULL
        ORDER BY b.reference_externe
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            sql,
            (source_recherche_ref,),
        )
        rows = cursor.fetchall()

    return {
        str(row["reference_externe"])
        for row in rows
        if row["reference_externe"] is not None
    }


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