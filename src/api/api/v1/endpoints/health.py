from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.api.db.session import engine


router = APIRouter(tags=["Health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/ready")
def readiness() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "database": "available",
        }

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc