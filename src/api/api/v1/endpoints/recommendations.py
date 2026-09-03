from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from src.api.db.session import get_db
from src.api.schemas.recommendation import (
    RecommendationResponse,
)
from src.api.services.recommendation import (
    RecommendationPersistenceError,
    RecommendationService,
    RecommendationValidationError,
)


router = APIRouter(
    prefix="/demande-versions",
    tags=["Recommendations"],
)


@router.post(
    "/{id_demande_version}/recommendations",
    response_model=RecommendationResponse,
)
def generate_recommendations(
    id_demande_version: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    service = RecommendationService(db)

    try:
        return service.generate_recommendations(
            id_demande_version=id_demande_version,
            limit=limit,
        )

    except RecommendationValidationError as exc:
        message = str(exc)

        if "does not exist" in message:
            raise HTTPException(
                status_code=404,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=422,
            detail=message,
        ) from exc

    except RecommendationPersistenceError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc