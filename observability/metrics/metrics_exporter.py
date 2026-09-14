from __future__ import annotations

import os
import time

from prometheus_client import (
    CollectorRegistry,
    Gauge,
    Histogram,
    push_to_gateway,
)


# =============================================================================
# PUSHGATEWAY CONFIGURATION
# =============================================================================

PUSHGATEWAY_URL = os.getenv(
    "PUSHGATEWAY_URL",
    "http://retail-pushgateway.monitoring.svc.cluster.local:9091",
)

PUSHGATEWAY_JOB = os.getenv(
    "PUSHGATEWAY_JOB",
    "real_estate_data_platform",
)


registry = CollectorRegistry()


# =============================================================================
# PIPELINE / METRICS COLLECTION HEALTH
# =============================================================================

pipeline_run_status = Gauge(
    "real_estate_pipeline_run_status",
    (
        "Status of the latest Real Estate platform metrics collection: "
        "1=success, 0=failure"
    ),
    registry=registry,
)

pipeline_duration_seconds = Histogram(
    "real_estate_pipeline_duration_seconds",
    "Duration of Real Estate platform metrics collection in seconds",
    registry=registry,
)

pipeline_last_run_timestamp = Gauge(
    "real_estate_pipeline_last_run_timestamp",
    "Unix timestamp of the latest Real Estate platform metrics collection",
    registry=registry,
)

pipeline_last_success_timestamp = Gauge(
    "real_estate_pipeline_last_success_timestamp",
    (
        "Unix timestamp of the latest successful "
        "Real Estate platform metrics collection"
    ),
    registry=registry,
)


# =============================================================================
# DATA VOLUME METRICS
#
# Logical Medallion mapping:
#
# BRONZE
#   raw
#
# SILVER
#   staging
#   real_estate OLTP
#
# GOLD
#   warehouse
#   analytics
#
# IMPORTANT:
# We intentionally DO NOT add a "medallion" label here.
#
# These metric families already identify their physical/logical layer.
# Adding a new label to an existing metric creates a second Prometheus
# time series and causes duplicate values in existing Grafana panels.
# =============================================================================

raw_table_rows = Gauge(
    "real_estate_raw_table_rows",
    "Number of rows available in RAW tables",
    ["table"],
    registry=registry,
)

staging_table_rows = Gauge(
    "real_estate_staging_table_rows",
    "Number of rows available in STAGING tables or views",
    ["table"],
    registry=registry,
)

oltp_table_rows = Gauge(
    "real_estate_oltp_table_rows",
    "Number of rows available in Real Estate OLTP tables",
    ["table"],
    registry=registry,
)

warehouse_table_rows = Gauge(
    "real_estate_warehouse_table_rows",
    "Number of rows available in warehouse tables",
    ["table"],
    registry=registry,
)

analytics_table_rows = Gauge(
    "real_estate_analytics_table_rows",
    "Number of rows available in analytics models or views",
    ["view"],
    registry=registry,
)


# =============================================================================
# BUSINESS / OLTP KPI METRICS
# =============================================================================

clients_total = Gauge(
    "real_estate_clients_total",
    "Total number of Real Estate clients",
    registry=registry,
)

chasseurs_total = Gauge(
    "real_estate_chasseurs_total",
    "Total number of Real Estate chasseurs",
    registry=registry,
)

mandats_total = Gauge(
    "real_estate_mandats_total",
    "Total number of Real Estate mandats",
    registry=registry,
)

active_mandats = Gauge(
    "real_estate_active_mandats",
    "Number of currently active Real Estate mandats",
    registry=registry,
)

biens_total = Gauge(
    "real_estate_biens_total",
    "Total number of Real Estate properties",
    registry=registry,
)

presentations_total = Gauge(
    "real_estate_presentations_total",
    "Total number of Real Estate property presentations",
    registry=registry,
)

visites_total = Gauge(
    "real_estate_visites_total",
    "Total number of Real Estate property visits",
    registry=registry,
)

paiements_total = Gauge(
    "real_estate_paiements_total",
    "Total number of Real Estate payments",
    registry=registry,
)
paiements_payes_total = Gauge(
    "real_estate_paiements_payes_total",
    "Total number of Real Estate payments in PAYE status",
    registry=registry,
)

honoraires_total_euros = Gauge(
    "real_estate_honoraires_total_euros",
    "Total Real Estate company fees for paid payments in euros",
    registry=registry,
)

remunerations_chasseur_total_euros = Gauge(
    "real_estate_remunerations_chasseur_total_euros",
    "Total hunter remuneration for paid payments in euros",
    registry=registry,
)

taux_remuneration_moyen = Gauge(
    "real_estate_taux_remuneration_moyen",
    "Average final hunter remuneration rate for paid payments",
    registry=registry,
)

# =============================================================================
# MARKET / ANALYTICS KPI METRICS
# =============================================================================

market_listings_total = Gauge(
    "real_estate_market_listings_total",
    "Total number of listings represented in the analytics layer",
    registry=registry,
)

market_average_price = Gauge(
    "real_estate_market_average_price",
    "Average Real Estate property price",
    registry=registry,
)

market_average_price_m2 = Gauge(
    "real_estate_market_average_price_m2",
    "Average Real Estate property price per square metre",
    registry=registry,
)

market_average_surface = Gauge(
    "real_estate_market_average_surface",
    "Average Real Estate property surface in square metres",
    registry=registry,
)


# =============================================================================
# TIMING HELPERS
# =============================================================================

def start_timer() -> float:
    """
    Start a timer for the metrics collection process.
    """

    return time.time()


def observe_pipeline_duration(
    start_time: float,
) -> float:
    """
    Observe the duration of the metrics collection process.
    """

    duration = time.time() - start_time

    pipeline_duration_seconds.observe(
        duration
    )

    return duration


# =============================================================================
# PIPELINE STATUS HELPERS
# =============================================================================

def mark_pipeline_success() -> None:
    """
    Mark platform metrics collection as successful.

    This metric represents the collect_metrics task itself.
    Airflow remains authoritative for the complete DAG execution state.
    """

    now = time.time()

    pipeline_run_status.set(1)

    pipeline_last_run_timestamp.set(
        now
    )

    pipeline_last_success_timestamp.set(
        now
    )


def mark_pipeline_failure() -> None:
    """
    Mark platform metrics collection as failed.

    This does not represent an upstream Airflow DAG failure.
    """

    pipeline_run_status.set(0)

    pipeline_last_run_timestamp.set(
        time.time()
    )


# =============================================================================
# DATA VOLUME HELPERS
# =============================================================================

def set_raw_count(
    table: str,
    count: int,
) -> None:
    raw_table_rows.labels(
        table=table,
    ).set(count)


def set_staging_count(
    table: str,
    count: int,
) -> None:
    staging_table_rows.labels(
        table=table,
    ).set(count)


def set_oltp_count(
    table: str,
    count: int,
) -> None:
    oltp_table_rows.labels(
        table=table,
    ).set(count)


def set_warehouse_count(
    table: str,
    count: int,
) -> None:
    warehouse_table_rows.labels(
        table=table,
    ).set(count)


def set_analytics_count(
    view: str,
    count: int,
) -> None:
    analytics_table_rows.labels(
        view=view,
    ).set(count)


# =============================================================================
# BUSINESS KPI HELPERS
# =============================================================================

def set_business_metrics(
    *,
    clients: int | None = None,
    chasseurs: int | None = None,
    mandats: int | None = None,
    active_mandats_count: int | None = None,
    biens: int | None = None,
    presentations: int | None = None,
    visites: int | None = None,
    paiements: int | None = None,
    paiements_payes: int | None = None,
    honoraires_total: float | None = None,
    remunerations_chasseur_total: float | None = None,
    taux_remuneration_moyen_value: float | None = None,
) -> None:

    if clients is not None:
        clients_total.set(
            clients
        )

    if chasseurs is not None:
        chasseurs_total.set(
            chasseurs
        )

    if mandats is not None:
        mandats_total.set(
            mandats
        )

    if active_mandats_count is not None:
        active_mandats.set(
            active_mandats_count
        )

    if biens is not None:
        biens_total.set(
            biens
        )

    if presentations is not None:
        presentations_total.set(
            presentations
        )

    if visites is not None:
        visites_total.set(
            visites
        )

    if paiements is not None:
        paiements_total.set(
            paiements
        )
    if paiements_payes is not None:
        paiements_payes_total.set(
            paiements_payes
        )

    if honoraires_total is not None:
        honoraires_total_euros.set(
            honoraires_total
        )

    if remunerations_chasseur_total is not None:
        remunerations_chasseur_total_euros.set(
            remunerations_chasseur_total
        )

    if taux_remuneration_moyen_value is not None:
        taux_remuneration_moyen.set(
            taux_remuneration_moyen_value
        )

# =============================================================================
# MARKET KPI HELPERS
# =============================================================================

def set_market_metrics(
    *,
    listings: int | None = None,
    average_price: float | None = None,
    average_price_m2: float | None = None,
    average_surface: float | None = None,
) -> None:

    if listings is not None:
        market_listings_total.set(
            listings
        )

    if average_price is not None:
        market_average_price.set(
            average_price
        )

    if average_price_m2 is not None:
        market_average_price_m2.set(
            average_price_m2
        )

    if average_surface is not None:
        market_average_surface.set(
            average_surface
        )


# =============================================================================
# PUSHGATEWAY
# =============================================================================

def push_metrics() -> None:
    """
    Push Real Estate platform metrics to Prometheus Pushgateway.

    Data Quality metrics are intentionally not exported here.

    DQ is handled independently by dq_runner.py because DQ metrics must
    still be published when a blocking validation fails and prevents
    collect_metrics from running.

    DQ metric families therefore remain:

        real_estate_dq_layer_status
        real_estate_dq_layer_checks_total
        real_estate_dq_layer_checks_passed
        real_estate_dq_layer_checks_failed
        real_estate_dq_layer_last_run_timestamp

    with:

        raw       -> bronze
        staging   -> silver
        oltp      -> silver
        warehouse -> gold
    """

    push_to_gateway(
        gateway=PUSHGATEWAY_URL,
        job=PUSHGATEWAY_JOB,
        registry=registry,
    )