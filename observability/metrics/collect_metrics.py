from __future__ import annotations

import os
import sys

import psycopg

from metrics_exporter import (
    mark_pipeline_failure,
    mark_pipeline_success,
    observe_pipeline_duration,
    push_metrics,
    set_analytics_count,
    set_business_metrics,
    set_market_metrics,
    set_oltp_count,
    set_raw_count,
    set_staging_count,
    set_warehouse_count,
    start_timer,
)


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_connection():
    return psycopg.connect(
        host=env("POSTGRES_HOST"),
        port=int(env("POSTGRES_PORT")),
        dbname=env("POSTGRES_DB"),
        user=env("POSTGRES_USER"),
        password=env("POSTGRES_PASSWORD"),
        autocommit=True,
    )


def fetch_scalar(cur, query: str):
    cur.execute(query)
    row = cur.fetchone()

    if not row:
        return None

    return row[0]


def collect_raw_metrics(cur) -> None:
    tables = [
        "annonces",
        "recherches",
    ]

    for table in tables:
        count = fetch_scalar(
            cur,
            f"SELECT COUNT(*) FROM raw.{table};",
        )

        set_raw_count(
            table,
            int(count or 0),
        )


def collect_staging_metrics(cur) -> None:
    objects = [
        "annonces",
        "recherches",
    ]

    for table in objects:
        count = fetch_scalar(
            cur,
            f"SELECT COUNT(*) FROM staging.{table};",
        )

        set_staging_count(
            table,
            int(count or 0),
        )


def collect_oltp_metrics(cur) -> None:
    tables = [
        "client",
        "chasseur",
        "mandat",
        "demande",
        "demande_version",
        "bien",
        "presentation",
        "visite",
        "paiement",
        "audit_log",
    ]

    for table in tables:
        count = fetch_scalar(
            cur,
            f"SELECT COUNT(*) FROM real_estate.{table};",
        )

        set_oltp_count(
            table,
            int(count or 0),
        )


def collect_warehouse_metrics(cur) -> None:
    tables = [
        "dim_source",
        "dim_localisation",
        "dim_bien",
        "dim_client",
        "dim_chasseur",
        "dim_secteur",
        "dim_demande_version",
        "fact_annonce",
        "fact_mandat",
        "bridge_mandat_secteur",
        "fact_presentation",
        "fact_paiement",
    ]

    for table in tables:
        count = fetch_scalar(
            cur,
            f"SELECT COUNT(*) FROM warehouse.{table};",
        )

        set_warehouse_count(
            table,
            int(count or 0),
        )


def collect_analytics_metrics(cur) -> None:
    views = [
        "mart_market_by_city",
        "mart_market_overview",
        "mart_market_by_property_type",
        "mart_market_by_dpe",
        "mart_market_by_source",
        "mart_market_evolution",
        "mart_mandat_performance",
    ]

    for view in views:
        count = fetch_scalar(
            cur,
            f"SELECT COUNT(*) FROM analytics.{view};",
        )

        set_analytics_count(
            view,
            int(count or 0),
        )


def collect_business_metrics(cur) -> None:
    clients = fetch_scalar(
        cur,
        "SELECT COUNT(*) FROM real_estate.client;",
    )

    chasseurs = fetch_scalar(
        cur,
        "SELECT COUNT(*) FROM real_estate.chasseur;",
    )

    mandats = fetch_scalar(
        cur,
        "SELECT COUNT(*) FROM real_estate.mandat;",
    )

    active_mandats = fetch_scalar(
        cur,
        """
        SELECT COUNT(*)
        FROM real_estate.mandat
        WHERE statut IS NOT NULL
          AND UPPER(statut) IN (
              'ACTIF',
              'ACTIVE',
              'EN_COURS'
          );
        """,
    )

    biens = fetch_scalar(
        cur,
        "SELECT COUNT(*) FROM real_estate.bien;",
    )

    presentations = fetch_scalar(
        cur,
        "SELECT COUNT(*) FROM real_estate.presentation;",
    )

    visites = fetch_scalar(
        cur,
        "SELECT COUNT(*) FROM real_estate.visite;",
    )

    paiements = fetch_scalar(
        cur,
        "SELECT COUNT(*) FROM real_estate.paiement;",
    )

    set_business_metrics(
        clients=int(clients or 0),
        chasseurs=int(chasseurs or 0),
        mandats=int(mandats or 0),
        active_mandats_count=int(active_mandats or 0),
        biens=int(biens or 0),
        presentations=int(presentations or 0),
        visites=int(visites or 0),
        paiements=int(paiements or 0),
    )


def collect_market_metrics(cur) -> None:
    cur.execute(
        """
        SELECT
            COUNT(*) AS listings,
            AVG(prix) AS average_price,
            AVG(prix_m2) AS average_price_m2,
            AVG(surface) AS average_surface
        FROM warehouse.fact_annonce;
        """
    )

    row = cur.fetchone()

    if not row:
        return

    listings, average_price, average_price_m2, average_surface = row

    set_market_metrics(
        listings=int(listings or 0),
        average_price=float(average_price or 0),
        average_price_m2=float(average_price_m2 or 0),
        average_surface=float(average_surface or 0),
    )


def main() -> None:
    print("Collecting Real Estate observability metrics...")

    start_time = start_timer()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                collect_raw_metrics(cur)
                collect_staging_metrics(cur)
                collect_oltp_metrics(cur)
                collect_warehouse_metrics(cur)
                collect_analytics_metrics(cur)
                collect_business_metrics(cur)
                collect_market_metrics(cur)

        observe_pipeline_duration(
            start_time
        )

        mark_pipeline_success()

        push_metrics()

        print(
            "Real Estate observability metrics pushed successfully."
        )

    except Exception as exc:
        print(
            f"ERROR: Metrics collection failed: {exc}",
            file=sys.stderr,
        )

        try:
            observe_pipeline_duration(
                start_time
            )

            mark_pipeline_failure()

            push_metrics()

        except Exception as push_exc:
            print(
                f"ERROR: Unable to push failure metrics: {push_exc}",
                file=sys.stderr,
            )

        raise


if __name__ == "__main__":
    main()