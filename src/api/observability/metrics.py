import time

from fastapi import Request, Response
from prometheus_client import Counter, Histogram


# =============================================================================
# GENERIC API METRICS
# =============================================================================

REQUESTS_TOTAL = Counter(
    "real_estate_api_requests_total",
    "Total number of API requests",
    [
        "method",
        "path",
        "status_code",
    ],
)

REQUEST_DURATION_SECONDS = Histogram(
    "real_estate_api_request_duration_seconds",
    "API request duration in seconds",
    [
        "method",
        "path",
    ],
)

ERRORS_TOTAL = Counter(
    "real_estate_api_errors_total",
    "Total number of API responses with status code >= 400",
    [
        "method",
        "path",
        "status_code",
    ],
)


# =============================================================================
# RECOMMENDATION / MATCHING BUSINESS METRICS
# =============================================================================

RECOMMENDATION_REQUESTS_TOTAL = Counter(
    "real_estate_recommendation_requests_total",
    "Total number of recommendation generation requests",
)

RECOMMENDATION_FAILURES_TOTAL = Counter(
    "real_estate_recommendation_failures_total",
    "Total number of failed recommendation generation requests",
    [
        "failure_type",
    ],
)

RECOMMENDATION_DURATION_SECONDS = Histogram(
    "real_estate_recommendation_duration_seconds",
    "Recommendation generation duration in seconds",
)

RECOMMENDATION_ELIGIBLE_CANDIDATES = Histogram(
    "real_estate_recommendation_eligible_candidates",
    "Number of eligible candidates per recommendation request",
)

RECOMMENDATION_SELECTED_CANDIDATES = Histogram(
    "real_estate_recommendation_selected_candidates",
    "Number of selected candidates per recommendation request",
)

RECOMMENDATION_PRESENTATIONS_CREATED = Histogram(
    "real_estate_recommendation_presentations_created",
    "Number of newly created presentations per recommendation request",
)

RECOMMENDATION_PRESENTATIONS_EXISTING = Histogram(
    "real_estate_recommendation_presentations_existing",
    "Number of existing presentations reused per recommendation request",
)


# =============================================================================
# PATH NORMALIZATION
# =============================================================================

def _get_normalized_path(
    request: Request,
) -> str:
    """
    Return the normalized FastAPI route path whenever possible.

    Example:

        /api/v1/demande-versions/55/recommendations

    becomes:

        /api/v1/demande-versions/{id_demande_version}/recommendations

    This prevents high-cardinality Prometheus time series caused by
    identifiers embedded directly in request URLs.
    """

    route = request.scope.get("route")

    if route is not None:
        route_path = getattr(
            route,
            "path",
            None,
        )

        if route_path:
            return route_path

    return request.url.path


# =============================================================================
# PROMETHEUS HTTP MIDDLEWARE
# =============================================================================

async def prometheus_metrics_middleware(
    request: Request,
    call_next,
) -> Response:
    """
    Collect generic HTTP API metrics.

    Recommendation-specific business metrics are collected separately
    in the RecommendationService.

    The /metrics endpoint itself is intentionally excluded so that
    Prometheus scraping does not generate artificial API traffic.
    """

    if request.url.path == "/metrics":
        return await call_next(
            request
        )

    start_time = time.perf_counter()
    method = request.method

    try:
        response = await call_next(
            request
        )

        status_code = str(
            response.status_code
        )

    except Exception:
        duration = (
            time.perf_counter()
            - start_time
        )

        path = _get_normalized_path(
            request
        )

        REQUESTS_TOTAL.labels(
            method=method,
            path=path,
            status_code="500",
        ).inc()

        REQUEST_DURATION_SECONDS.labels(
            method=method,
            path=path,
        ).observe(
            duration
        )

        ERRORS_TOTAL.labels(
            method=method,
            path=path,
            status_code="500",
        ).inc()

        raise

    duration = (
        time.perf_counter()
        - start_time
    )

    path = _get_normalized_path(
        request
    )

    REQUESTS_TOTAL.labels(
        method=method,
        path=path,
        status_code=status_code,
    ).inc()

    REQUEST_DURATION_SECONDS.labels(
        method=method,
        path=path,
    ).observe(
        duration
    )

    if response.status_code >= 400:
        ERRORS_TOTAL.labels(
            method=method,
            path=path,
            status_code=status_code,
        ).inc()

    return response