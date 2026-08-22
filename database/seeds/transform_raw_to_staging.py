#!/usr/bin/env python3

"""
transform_raw_to_staging.py

Transform one Real Estate RAW ingestion batch into typed STAGING tables.

Source:
    raw.recherches
    raw.annonces

Target:
    staging.recherches
    staging.annonces

Required environment variables:
    POSTGRES_HOST
    POSTGRES_PORT
    POSTGRES_DB
    POSTGRES_USER
    POSTGRES_PASSWORD
    INGESTION_BATCH

Principles:
    - RAW values are never modified.
    - Every RAW row is represented in STAGING.
    - Valid values are converted to proper PostgreSQL types.
    - Invalid values become NULL where appropriate.
    - Parsing problems are recorded in quality_errors.
    - quality_valid is FALSE whenever parsing/validation errors exist.
    - Transformation is rerunnable through ON CONFLICT(raw_id).
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
import uuid

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import psycopg

from dotenv import load_dotenv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


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
# GENERIC HELPERS
# =============================================================================


def clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    if text == "":
        return None

    return text


def add_error(
    errors: list[dict[str, Any]],
    field: str,
    value: Any,
    message: str,
) -> None:
    errors.append(
        {
            "field": field,
            "value": value,
            "error": message,
        }
    )


# =============================================================================
# NUMERIC PARSING
# =============================================================================


def normalize_numeric_text(value: Any) -> str | None:
    text = clean_text(value)

    if text is None:
        return None

    text = (
        text
        .replace("\u00a0", "")
        .replace("\u202f", "")
        .replace("€", "")
        .replace("EUR", "")
        .replace("eur", "")
        .replace("m²", "")
        .replace("m2", "")
        .replace(" ", "")
        .strip()
    )

    # French decimal comma.
    if "," in text and "." not in text:
        text = text.replace(",", ".")

    return text


def parse_decimal(
    value: Any,
    field: str,
    errors: list[dict[str, Any]],
    *,
    minimum: Decimal | None = None,
    maximum: Decimal | None = None,
) -> Decimal | None:
    text = normalize_numeric_text(value)

    if text is None:
        return None

    try:
        result = Decimal(text)

    except InvalidOperation:
        add_error(
            errors,
            field,
            value,
            "invalid numeric value",
        )
        return None

    if minimum is not None and result < minimum:
        add_error(
            errors,
            field,
            value,
            f"value must be >= {minimum}",
        )
        return None

    if maximum is not None and result > maximum:
        add_error(
            errors,
            field,
            value,
            f"value must be <= {maximum}",
        )
        return None

    return result


def parse_integer(
    value: Any,
    field: str,
    errors: list[dict[str, Any]],
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int | None:
    text = normalize_numeric_text(value)

    if text is None:
        return None

    try:
        number = Decimal(text)

    except InvalidOperation:
        add_error(
            errors,
            field,
            value,
            "invalid integer value",
        )
        return None

    if number != number.to_integral_value():
        add_error(
            errors,
            field,
            value,
            "value is not an integer",
        )
        return None

    result = int(number)

    if minimum is not None and result < minimum:
        add_error(
            errors,
            field,
            value,
            f"value must be >= {minimum}",
        )
        return None

    if maximum is not None and result > maximum:
        add_error(
            errors,
            field,
            value,
            f"value must be <= {maximum}",
        )
        return None

    return result


# =============================================================================
# BOOLEAN PARSING
# =============================================================================


TRUE_VALUES = {
    "true",
    "1",
    "yes",
    "y",
    "oui",
    "o",
    "vrai",
}

FALSE_VALUES = {
    "false",
    "0",
    "no",
    "n",
    "non",
    "faux",
}


def parse_boolean(
    value: Any,
    field: str,
    errors: list[dict[str, Any]],
) -> bool | None:
    text = clean_text(value)

    if text is None:
        return None

    normalized = text.lower()

    if normalized in TRUE_VALUES:
        return True

    if normalized in FALSE_VALUES:
        return False

    add_error(
        errors,
        field,
        value,
        "invalid boolean value",
    )

    return None


# =============================================================================
# UUID
# =============================================================================


def parse_uuid(
    value: Any,
    field: str,
    errors: list[dict[str, Any]],
) -> uuid.UUID | None:
    text = clean_text(value)

    if text is None:
        return None

    try:
        return uuid.UUID(text)

    except (ValueError, AttributeError):
        add_error(
            errors,
            field,
            value,
            "invalid UUID",
        )

        return None


# =============================================================================
# DPE
# =============================================================================


VALID_DPE = {
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
}


def parse_dpe(
    value: Any,
    field: str,
    errors: list[dict[str, Any]],
) -> str | None:
    text = clean_text(value)

    if text is None:
        return None

    normalized = text.upper()

    if normalized in VALID_DPE:
        return normalized

    add_error(
        errors,
        field,
        value,
        "DPE must be between A and G",
    )

    return None


# =============================================================================
# DATE / DATETIME PARSING
# =============================================================================


DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d.%m.%Y",
)

DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%d/%m/%Y %H:%M:%S",
)


def parse_date(
    value: Any,
    field: str,
    errors: list[dict[str, Any]],
) -> date | None:
    text = clean_text(value)

    if text is None:
        return None

    # ISO date/datetime.
    try:
        return datetime.fromisoformat(
            text.replace("Z", "+00:00")
        ).date()

    except ValueError:
        pass

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(
                text,
                fmt,
            ).date()

        except ValueError:
            continue

    # Unix timestamp.
    try:
        timestamp = float(text)

        # Millisecond epoch.
        if timestamp > 10_000_000_000:
            timestamp /= 1000

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        ).date()

    except (ValueError, OSError, OverflowError):
        pass

    add_error(
        errors,
        field,
        value,
        "invalid date format",
    )

    return None


def parse_datetime(
    value: Any,
    field: str,
    errors: list[dict[str, Any]],
) -> datetime | None:
    text = clean_text(value)

    if text is None:
        return None

    # ISO 8601.
    try:
        result = datetime.fromisoformat(
            text.replace("Z", "+00:00")
        )

        if result.tzinfo is None:
            result = result.replace(
                tzinfo=timezone.utc
            )

        return result

    except ValueError:
        pass

    for fmt in DATETIME_FORMATS:
        try:
            result = datetime.strptime(
                text,
                fmt,
            )

            return result.replace(
                tzinfo=timezone.utc
            )

        except ValueError:
            continue

    # Date-only values.
    for fmt in DATE_FORMATS:
        try:
            result = datetime.strptime(
                text,
                fmt,
            )

            return result.replace(
                tzinfo=timezone.utc
            )

        except ValueError:
            continue

    # Unix timestamp seconds or milliseconds.
    try:
        timestamp = float(text)

        if timestamp > 10_000_000_000:
            timestamp /= 1000

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        )

    except (ValueError, OSError, OverflowError):
        pass

    add_error(
        errors,
        field,
        value,
        "invalid datetime format",
    )

    return None


# =============================================================================
# JSON / LIST PARSING
# =============================================================================


def parse_list(
    value: Any,
    field: str,
    errors: list[dict[str, Any]],
) -> list[Any]:
    text = clean_text(value)

    if text is None:
        return []

    # Proper JSON.
    try:
        parsed = json.loads(text)

        if isinstance(parsed, list):
            return parsed

        if isinstance(parsed, str):
            return [parsed]

    except json.JSONDecodeError:
        pass

    # Python literal representation such as:
    # ['photo1', 'photo2']
    try:
        parsed = ast.literal_eval(text)

        if isinstance(parsed, (list, tuple)):
            return list(parsed)

    except (ValueError, SyntaxError):
        pass

    # Flattened CSV representation.
    if ";" in text:
        return [
            item.strip()
            for item in text.split(";")
            if item.strip()
        ]

    if "|" in text:
        return [
            item.strip()
            for item in text.split("|")
            if item.strip()
        ]

    # A single value is still usable.
    return [text]


# =============================================================================
# FETCH RAW DATA
# =============================================================================


def fetch_raw_recherches(
    connection: psycopg.Connection,
    batch: str,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            raw_id,
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
        FROM raw.recherches
        WHERE ingestion_batch = %s
        ORDER BY raw_id
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


def fetch_raw_annonces(
    connection: psycopg.Connection,
    batch: str,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            raw_id,
            id,
            reference,
            recherche_ref,
            type_bien,
            titre,
            ville,
            code_postal,
            date_publication,
            prix,
            surface,
            nb_pieces,
            nb_chambres,
            meuble,
            dpe,
            description,
            terrasse,
            calme,
            contact_nom,
            contact_telephone,
            contact_email,
            contact_agence,
            photos,
            exclusivite,
            particulier,
            surface_m2,
            annee_construction,
            adresse,
            latitude,
            longitude,
            etage,
            charges_mensuelles,
            vue,
            jardin,
            source_file,
            ingestion_batch
        FROM raw.annonces
        WHERE ingestion_batch = %s
        ORDER BY raw_id
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
# RECHERCHE TRANSFORMATION
# =============================================================================


def transform_recherche(
    raw: dict[str, Any],
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    legacy_generated_id = parse_integer(
        raw["id"],
        "id",
        errors,
        minimum=0,
    )

    reference = clean_text(
        raw["reference"]
    )

    if reference is None:
        add_error(
            errors,
            "reference",
            raw["reference"],
            "reference is mandatory",
        )

    ville = clean_text(
        raw["ville"]
    )

    if ville is None:
        add_error(
            errors,
            "ville",
            raw["ville"],
            "ville is mandatory",
        )

    type_bien = clean_text(
        raw["type_bien"]
    )

    if type_bien is None:
        add_error(
            errors,
            "type_bien",
            raw["type_bien"],
            "type_bien is mandatory",
        )

    budget_max = parse_decimal(
        raw["budget_max"],
        "budget_max",
        errors,
        minimum=Decimal("0"),
    )

    if budget_max is None:
        add_error(
            errors,
            "budget_max",
            raw["budget_max"],
            "budget_max is mandatory and must be numeric",
        )

    surface_min = parse_decimal(
        raw["surface_min"],
        "surface_min",
        errors,
        minimum=Decimal("0"),
    )

    if surface_min is None:
        add_error(
            errors,
            "surface_min",
            raw["surface_min"],
            "surface_min is mandatory and must be numeric",
        )

    return {
        "raw_id": raw["raw_id"],
        "legacy_generated_id": legacy_generated_id,
        "reference": reference,
        "date_creation": parse_date(
            raw["date_creation"],
            "date_creation",
            errors,
        ),
        "ville": ville,
        "code_postal": clean_text(
            raw["code_postal"]
        ),
        "type_bien": type_bien,
        "budget_max": budget_max,
        "surface_min": surface_min,
        "criteres_souhaites": parse_list(
            raw["criteres_souhaites"],
            "criteres_souhaites",
            errors,
        ),
        "nb_pieces_min": parse_integer(
            raw["nb_pieces_min"],
            "nb_pieces_min",
            errors,
            minimum=0,
        ),
        "nb_chambres_min": parse_integer(
            raw["nb_chambres_min"],
            "nb_chambres_min",
            errors,
            minimum=0,
        ),
        "dpe_max": parse_dpe(
            raw["dpe_max"],
            "dpe_max",
            errors,
        ),
        "ingestion_batch": raw["ingestion_batch"],
        "source_file": raw["source_file"],
        "quality_valid": len(errors) == 0,
        "quality_errors": errors,
    }


# =============================================================================
# ANNONCE TRANSFORMATION
# =============================================================================


def transform_annonce(
    raw: dict[str, Any],
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    reference = clean_text(
        raw["reference"]
    )

    if reference is None:
        add_error(
            errors,
            "reference",
            raw["reference"],
            "reference is mandatory",
        )

    recherche_ref = clean_text(
        raw["recherche_ref"]
    )

    if recherche_ref is None:
        add_error(
            errors,
            "recherche_ref",
            raw["recherche_ref"],
            "recherche_ref is mandatory",
        )

    ville = clean_text(
        raw["ville"]
    )

    if ville is None:
        add_error(
            errors,
            "ville",
            raw["ville"],
            "ville is mandatory",
        )

    type_bien = clean_text(
        raw["type_bien"]
    )

    if type_bien is None:
        add_error(
            errors,
            "type_bien",
            raw["type_bien"],
            "type_bien is mandatory",
        )

    prix = parse_decimal(
        raw["prix"],
        "prix",
        errors,
        minimum=Decimal("0"),
    )

    if prix is None:
        add_error(
            errors,
            "prix",
            raw["prix"],
            "prix is mandatory and must be numeric",
        )

    # Prefer surface, fallback to surface_m2.
    raw_surface = (
        clean_text(raw["surface"])
        or clean_text(raw["surface_m2"])
    )

    surface = parse_decimal(
        raw_surface,
        "surface",
        errors,
        minimum=Decimal("0"),
    )

    if surface is None:
        add_error(
            errors,
            "surface",
            raw_surface,
            "surface is mandatory and must be numeric",
        )

    return {
        "raw_id": raw["raw_id"],

        "source_uuid": parse_uuid(
            raw["id"],
            "id",
            errors,
        ),

        "reference": reference,
        "recherche_ref": recherche_ref,

        "type_bien": type_bien,

        "titre": clean_text(
            raw["titre"]
        ),

        "ville": ville,

        "code_postal": clean_text(
            raw["code_postal"]
        ),

        "date_publication": parse_datetime(
            raw["date_publication"],
            "date_publication",
            errors,
        ),

        "prix": prix,
        "surface": surface,

        "nb_pieces": parse_integer(
            raw["nb_pieces"],
            "nb_pieces",
            errors,
            minimum=0,
        ),

        "nb_chambres": parse_integer(
            raw["nb_chambres"],
            "nb_chambres",
            errors,
            minimum=0,
        ),

        "meuble": parse_boolean(
            raw["meuble"],
            "meuble",
            errors,
        ),

        "dpe": parse_dpe(
            raw["dpe"],
            "dpe",
            errors,
        ),

        "description": clean_text(
            raw["description"]
        ),

        "terrasse": parse_boolean(
            raw["terrasse"],
            "terrasse",
            errors,
        ),

        "calme": parse_boolean(
            raw["calme"],
            "calme",
            errors,
        ),

        "vue": parse_boolean(
            raw["vue"],
            "vue",
            errors,
        ),

        "jardin": parse_boolean(
            raw["jardin"],
            "jardin",
            errors,
        ),

        "contact_nom": clean_text(
            raw["contact_nom"]
        ),

        "contact_telephone": clean_text(
            raw["contact_telephone"]
        ),

        "contact_email": clean_text(
            raw["contact_email"]
        ),

        "contact_agence": clean_text(
            raw["contact_agence"]
        ),

        "photos": parse_list(
            raw["photos"],
            "photos",
            errors,
        ),

        "exclusivite": parse_boolean(
            raw["exclusivite"],
            "exclusivite",
            errors,
        ),

        "particulier": parse_boolean(
            raw["particulier"],
            "particulier",
            errors,
        ),

        "annee_construction": parse_integer(
            raw["annee_construction"],
            "annee_construction",
            errors,
            minimum=1800,
            maximum=2100,
        ),

        "adresse": clean_text(
            raw["adresse"]
        ),

        "latitude": parse_decimal(
            raw["latitude"],
            "latitude",
            errors,
            minimum=Decimal("-90"),
            maximum=Decimal("90"),
        ),

        "longitude": parse_decimal(
            raw["longitude"],
            "longitude",
            errors,
            minimum=Decimal("-180"),
            maximum=Decimal("180"),
        ),

        "etage": clean_text(
            raw["etage"]
        ),

        "charges_mensuelles": parse_decimal(
            raw["charges_mensuelles"],
            "charges_mensuelles",
            errors,
            minimum=Decimal("0"),
        ),

        "ingestion_batch": raw["ingestion_batch"],
        "source_file": raw["source_file"],

        "quality_valid": len(errors) == 0,
        "quality_errors": errors,
    }


# =============================================================================
# LOAD STAGING RECHERCHES
# =============================================================================


def upsert_recherches(
    connection: psycopg.Connection,
    rows: list[dict[str, Any]],
) -> None:
    query = """
        INSERT INTO staging.recherches (
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
            source_file,
            quality_valid,
            quality_errors
        )
        VALUES (
            %(raw_id)s,
            %(legacy_generated_id)s,
            %(reference)s,
            %(date_creation)s,
            %(ville)s,
            %(code_postal)s,
            %(type_bien)s,
            %(budget_max)s,
            %(surface_min)s,
            %(criteres_souhaites)s::jsonb,
            %(nb_pieces_min)s,
            %(nb_chambres_min)s,
            %(dpe_max)s,
            %(ingestion_batch)s,
            %(source_file)s,
            %(quality_valid)s,
            %(quality_errors)s::jsonb
        )

        ON CONFLICT (raw_id)
        DO UPDATE SET
            legacy_generated_id = EXCLUDED.legacy_generated_id,
            reference = EXCLUDED.reference,
            date_creation = EXCLUDED.date_creation,
            ville = EXCLUDED.ville,
            code_postal = EXCLUDED.code_postal,
            type_bien = EXCLUDED.type_bien,
            budget_max = EXCLUDED.budget_max,
            surface_min = EXCLUDED.surface_min,
            criteres_souhaites = EXCLUDED.criteres_souhaites,
            nb_pieces_min = EXCLUDED.nb_pieces_min,
            nb_chambres_min = EXCLUDED.nb_chambres_min,
            dpe_max = EXCLUDED.dpe_max,
            ingestion_batch = EXCLUDED.ingestion_batch,
            source_file = EXCLUDED.source_file,
            quality_valid = EXCLUDED.quality_valid,
            quality_errors = EXCLUDED.quality_errors,
            staged_at = CURRENT_TIMESTAMP
    """

    prepared = []

    for row in rows:
        item = dict(row)

        item["criteres_souhaites"] = json.dumps(
            row["criteres_souhaites"],
            ensure_ascii=False,
        )

        item["quality_errors"] = json.dumps(
            row["quality_errors"],
            ensure_ascii=False,
        )

        prepared.append(item)

    with connection.cursor() as cursor:
        cursor.executemany(
            query,
            prepared,
        )


# =============================================================================
# LOAD STAGING ANNONCES
# =============================================================================


def upsert_annonces(
    connection: psycopg.Connection,
    rows: list[dict[str, Any]],
) -> None:
    query = """
        INSERT INTO staging.annonces (
            raw_id,
            source_uuid,
            reference,
            recherche_ref,
            type_bien,
            titre,
            ville,
            code_postal,
            date_publication,
            prix,
            surface,
            nb_pieces,
            nb_chambres,
            meuble,
            dpe,
            description,
            terrasse,
            calme,
            vue,
            jardin,
            contact_nom,
            contact_telephone,
            contact_email,
            contact_agence,
            photos,
            exclusivite,
            particulier,
            annee_construction,
            adresse,
            latitude,
            longitude,
            etage,
            charges_mensuelles,
            ingestion_batch,
            source_file,
            quality_valid,
            quality_errors
        )
        VALUES (
            %(raw_id)s,
            %(source_uuid)s,
            %(reference)s,
            %(recherche_ref)s,
            %(type_bien)s,
            %(titre)s,
            %(ville)s,
            %(code_postal)s,
            %(date_publication)s,
            %(prix)s,
            %(surface)s,
            %(nb_pieces)s,
            %(nb_chambres)s,
            %(meuble)s,
            %(dpe)s,
            %(description)s,
            %(terrasse)s,
            %(calme)s,
            %(vue)s,
            %(jardin)s,
            %(contact_nom)s,
            %(contact_telephone)s,
            %(contact_email)s,
            %(contact_agence)s,
            %(photos)s::jsonb,
            %(exclusivite)s,
            %(particulier)s,
            %(annee_construction)s,
            %(adresse)s,
            %(latitude)s,
            %(longitude)s,
            %(etage)s,
            %(charges_mensuelles)s,
            %(ingestion_batch)s,
            %(source_file)s,
            %(quality_valid)s,
            %(quality_errors)s::jsonb
        )

        ON CONFLICT (raw_id)
        DO UPDATE SET
            source_uuid = EXCLUDED.source_uuid,
            reference = EXCLUDED.reference,
            recherche_ref = EXCLUDED.recherche_ref,
            type_bien = EXCLUDED.type_bien,
            titre = EXCLUDED.titre,
            ville = EXCLUDED.ville,
            code_postal = EXCLUDED.code_postal,
            date_publication = EXCLUDED.date_publication,
            prix = EXCLUDED.prix,
            surface = EXCLUDED.surface,
            nb_pieces = EXCLUDED.nb_pieces,
            nb_chambres = EXCLUDED.nb_chambres,
            meuble = EXCLUDED.meuble,
            dpe = EXCLUDED.dpe,
            description = EXCLUDED.description,
            terrasse = EXCLUDED.terrasse,
            calme = EXCLUDED.calme,
            vue = EXCLUDED.vue,
            jardin = EXCLUDED.jardin,
            contact_nom = EXCLUDED.contact_nom,
            contact_telephone = EXCLUDED.contact_telephone,
            contact_email = EXCLUDED.contact_email,
            contact_agence = EXCLUDED.contact_agence,
            photos = EXCLUDED.photos,
            exclusivite = EXCLUDED.exclusivite,
            particulier = EXCLUDED.particulier,
            annee_construction = EXCLUDED.annee_construction,
            adresse = EXCLUDED.adresse,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            etage = EXCLUDED.etage,
            charges_mensuelles = EXCLUDED.charges_mensuelles,
            ingestion_batch = EXCLUDED.ingestion_batch,
            source_file = EXCLUDED.source_file,
            quality_valid = EXCLUDED.quality_valid,
            quality_errors = EXCLUDED.quality_errors,
            staged_at = CURRENT_TIMESTAMP
    """

    prepared = []

    for row in rows:
        item = dict(row)

        item["source_uuid"] = (
            str(row["source_uuid"])
            if row["source_uuid"] is not None
            else None
        )

        item["photos"] = json.dumps(
            row["photos"],
            ensure_ascii=False,
        )

        item["quality_errors"] = json.dumps(
            row["quality_errors"],
            ensure_ascii=False,
        )

        prepared.append(item)

    with connection.cursor() as cursor:
        cursor.executemany(
            query,
            prepared,
        )


# =============================================================================
# RECONCILIATION
# =============================================================================


def validate_reconciliation(
    connection: psycopg.Connection,
    batch: str,
) -> None:
    query = """
        SELECT
            (
                SELECT COUNT(*)
                FROM raw.recherches
                WHERE ingestion_batch = %s
            ) AS raw_recherches,

            (
                SELECT COUNT(*)
                FROM staging.recherches
                WHERE ingestion_batch = %s
            ) AS staging_recherches,

            (
                SELECT COUNT(*)
                FROM raw.annonces
                WHERE ingestion_batch = %s
            ) AS raw_annonces,

            (
                SELECT COUNT(*)
                FROM staging.annonces
                WHERE ingestion_batch = %s
            ) AS staging_annonces,

            (
                SELECT COUNT(*)
                FROM staging.recherches
                WHERE ingestion_batch = %s
                  AND quality_valid = FALSE
            ) AS invalid_recherches,

            (
                SELECT COUNT(*)
                FROM staging.annonces
                WHERE ingestion_batch = %s
                  AND quality_valid = FALSE
            ) AS invalid_annonces
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                batch,
                batch,
                batch,
                batch,
                batch,
                batch,
            ),
        )

        result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            "Unable to reconcile RAW and STAGING"
        )

    (
        raw_recherches,
        staging_recherches,
        raw_annonces,
        staging_annonces,
        invalid_recherches,
        invalid_annonces,
    ) = result

    if raw_recherches != staging_recherches:
        raise RuntimeError(
            "RAW/STAGING recherche reconciliation failed: "
            f"{raw_recherches} RAW vs "
            f"{staging_recherches} STAGING"
        )

    if raw_annonces != staging_annonces:
        raise RuntimeError(
            "RAW/STAGING annonce reconciliation failed: "
            f"{raw_annonces} RAW vs "
            f"{staging_annonces} STAGING"
        )

    print(
        f"PASS: {raw_recherches} recherches reconciled "
        "RAW -> STAGING"
    )

    print(
        f"PASS: {raw_annonces} annonces reconciled "
        "RAW -> STAGING"
    )

    print(
        f"QUALITY: invalid recherches = "
        f"{invalid_recherches}"
    )

    print(
        f"QUALITY: invalid annonces = "
        f"{invalid_annonces}"
    )


# =============================================================================
# MAIN
# =============================================================================


def main() -> int:
    batch = require_env(
        "INGESTION_BATCH"
    )

    print(
        f"Transforming RAW batch: {batch}"
    )

    try:
        with psycopg.connect(
            connection_string()
        ) as connection:

            raw_recherches = fetch_raw_recherches(
                connection,
                batch,
            )

            raw_annonces = fetch_raw_annonces(
                connection,
                batch,
            )

            if not raw_recherches:
                raise RuntimeError(
                    f"No RAW recherches found for batch {batch}"
                )

            if not raw_annonces:
                raise RuntimeError(
                    f"No RAW annonces found for batch {batch}"
                )

            print(
                f"RAW recherches: {len(raw_recherches)}"
            )

            print(
                f"RAW annonces: {len(raw_annonces)}"
            )

            staging_recherches = [
                transform_recherche(row)
                for row in raw_recherches
            ]

            staging_annonces = [
                transform_annonce(row)
                for row in raw_annonces
            ]

            upsert_recherches(
                connection,
                staging_recherches,
            )

            upsert_annonces(
                connection,
                staging_annonces,
            )

            validate_reconciliation(
                connection,
                batch,
            )

            connection.commit()

    except Exception as exc:
        print(
            f"ERROR: RAW -> STAGING transformation failed: {exc}",
            file=sys.stderr,
        )

        return 1

    print(
        "RAW -> STAGING transformation completed successfully."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())