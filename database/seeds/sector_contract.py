"""Portable sector identity for generated data; never infer sectors from postcode."""

import hashlib
import json
import os
import unicodedata
from pathlib import Path


def normalized(value):
    return unicodedata.normalize("NFC", str(value or "")).strip().casefold()


def sector_code(sector):
    """Versioned identity independent of database sequences and row ordering."""
    key = [normalized(sector.get(k)) for k in ("pays", "ville", "quartier", "code_postal")]
    return "geo-v1-" + hashlib.sha256(
        json.dumps(key, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def index_catalogue(rows):
    catalogue = {}
    for row in rows:
        code = sector_code(row)
        if code in catalogue:
            raise RuntimeError("Ambiguous canonical sector geography; resolve duplicate sectors first")
        catalogue[code] = dict(row, secteur_code=code)
    return catalogue


def load_catalogue(connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_secteur, pays, ville, quartier, code_postal
            FROM real_estate.secteur WHERE actif = TRUE ORDER BY id_secteur
        """)
        columns = ("id_secteur", "pays", "ville", "quartier", "code_postal")
        return index_catalogue(dict(zip(columns, row)) for row in cursor.fetchall())


def resolve_sector(row, catalogue):
    code = (row.get("secteur_code") or "").strip()
    if not code:
        return None  # Legacy files have no evidence of precise geography.
    sector = catalogue.get(code)
    if sector is None:
        raise ValueError(f"Unknown or inactive sector code on {row.get('reference')}")
    for field in ("ville", "code_postal"):
        if normalized(row.get(field)) != normalized(sector.get(field)):
            raise ValueError(f"Sector {field} conflicts with {row.get('reference')}")
    return sector["id_secteur"]


def link_search_sector(connection, version_id, sector_id):
    if sector_id is None:
        return  # Do not erase existing reviewed geography on a legacy replay.
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_secteur FROM real_estate.demande_version_secteur
            WHERE id_demande_version = %s
        """, (version_id,))
        previous = {row[0] for row in cursor.fetchall()}
        if previous and previous != {sector_id}:
            raise ValueError("Generated search sector changed; create a new search reference")
        cursor.execute("""
            INSERT INTO real_estate.demande_version_secteur (id_demande_version, id_secteur)
            VALUES (%s, %s) ON CONFLICT DO NOTHING
        """, (version_id, sector_id))


def assign_property_sectors(connection, rows, source_id):
    # This must run AFTER the property UPSERT, in the same transaction.
    # Migration 017 invalidates old geography when an address changes. Only
    # independently resolved, explicit source evidence can restore the mapping.
    values = [(row["id_secteur"], source_id, row["reference"])
              for row in rows if row.get("id_secteur") is not None]
    if values:
        with connection.cursor() as cursor:
            cursor.executemany("""
                UPDATE real_estate.bien SET id_secteur = %s
                WHERE id_source = %s AND reference_externe = %s
            """, values)


def check_schema(connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (SELECT 1 FROM migration_control.schema_version WHERE version = '018')
        """)
        if not cursor.fetchone()[0]:
            raise RuntimeError("Apply migration 018 before running sector-aware ingestion")
        # Verify actual columns too, rather than relying only on the registry.
        for table in ("raw.annonces", "raw.recherches", "staging.annonces", "staging.recherches"):
            cursor.execute(f"SELECT secteur_code FROM {table} LIMIT 0")
        cursor.execute("SELECT id_secteur FROM real_estate.bien LIMIT 0")
        cursor.execute("SELECT id_secteur FROM real_estate.demande_version_secteur LIMIT 0")
        cursor.execute("SELECT secteur_key FROM warehouse.dim_bien LIMIT 0")
        cursor.execute("SELECT secteur_key FROM warehouse.bridge_demande_version_secteur LIMIT 0")


def database_connection():
    import psycopg

    connection = psycopg.connect(
        host=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    connection.read_only = True
    return connection


def check_database_schema():
    """Check readiness without fetching sectors or producing a catalogue file."""
    with database_connection() as connection:
        check_schema(connection)


def export_catalogue(path):
    with database_connection() as connection:
        check_schema(connection)
        # Existing synthetic generator models French properties only. Unknown
        # neighbourhood boundaries are not replaced with invented coordinates.
        rows = [dict(row) for row in load_catalogue(connection).values()
                if normalized(row["pays"]) == "france" and row["quartier"] and row["code_postal"]]
    if not rows:
        raise RuntimeError("No active, precise French sectors available for generation")
    for row in rows:
        row.pop("id_secteur")  # Never ship environment-specific IDs to fixtures.
    Path(path).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Read-only schema check and canonical sector export")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--check-schema", action="store_true")
    args = parser.parse_args(argv)
    if args.check_schema and args.output:
        parser.error("--check-schema does not accept an output file")
    if args.check_schema:
        check_database_schema()
    elif args.output:
        export_catalogue(args.output)
    else:
        parser.error("provide --check-schema or a catalogue output path")


if __name__ == "__main__":
    main()
