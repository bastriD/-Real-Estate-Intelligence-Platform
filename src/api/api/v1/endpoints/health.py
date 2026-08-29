from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness endpoint for the Real Estate Backend API."""
    return {"status": "healthy"}


@router.get("/ready")
def readiness() -> dict[str, str]:
    """Basic application readiness endpoint.

    PostgreSQL connectivity will be added during the database integration step.
    """
    return {"status": "ready"}
