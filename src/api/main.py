from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from src.api.api.v1.endpoints.health import router as health_router
from src.api.api.v1.router import api_router
from src.api.observability.metrics import prometheus_metrics_middleware


app = FastAPI(
    title="Real Estate Intelligence API",
    description="Business API for the Chasse Immobiliere platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.middleware("http")(prometheus_metrics_middleware)

# Root health endpoints for Kubernetes probes
app.include_router(health_router)

# Versioned API
app.include_router(api_router, prefix="/api/v1")


@app.get(
    "/metrics",
    include_in_schema=False,
)
def metrics() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )