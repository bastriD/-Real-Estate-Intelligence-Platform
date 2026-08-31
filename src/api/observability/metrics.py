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


async def prometheus_metrics_middleware(
    request: Request,
    call_next,
) -> Response:
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    path = request.url.path
    method = request.method
    status_code = str(response.status_code)

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