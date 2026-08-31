import time

from fastapi import Request, Response
from prometheus_client import Counter, Histogram


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


def _get_normalized_path(request: Request) -> str:
    route = request.scope.get("route")

    if route is not None:
        route_path = getattr(route, "path", None)

        if route_path:
            return route_path

    return request.url.path


async def prometheus_metrics_middleware(
    request: Request,
    call_next,
) -> Response:
    # Prometheus scraping must not generate API traffic metrics itself.
    if request.url.path == "/metrics":
        return await call_next(request)

    start_time = time.perf_counter()
    method = request.method

    try:
        response = await call_next(request)
        status_code = str(response.status_code)

    except Exception:
        duration = time.perf_counter() - start_time
        path = _get_normalized_path(request)

        REQUESTS_TOTAL.labels(
            method=method,
            path=path,
            status_code="500",
        ).inc()

        REQUEST_DURATION_SECONDS.labels(
            method=method,
            path=path,
        ).observe(duration)

        ERRORS_TOTAL.labels(
            method=method,
            path=path,
            status_code="500",
        ).inc()

        raise

    duration = time.perf_counter() - start_time
    path = _get_normalized_path(request)

    REQUESTS_TOTAL.labels(
        method=method,
        path=path,
        status_code=status_code,
    ).inc()

    REQUEST_DURATION_SECONDS.labels(
        method=method,
        path=path,
    ).observe(duration)

    if response.status_code >= 400:
        ERRORS_TOTAL.labels(
            method=method,
            path=path,
            status_code=status_code,
        ).inc()

    return response