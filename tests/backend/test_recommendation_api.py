from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.api.v1.endpoints.recommendations import (
    generate_recommendations,
)
from src.api.schemas.recommendation import (
    RecommendationItem,
    RecommendationResponse,
)
from src.api.services.recommendation import (
    RecommendationPersistenceError,
    RecommendationValidationError,
)


def build_response() -> RecommendationResponse:
    return RecommendationResponse(
        id_demande_version=55,
        requested_limit=10,
        eligible_candidates=400,
        selected_candidates=2,
        created_presentations=2,
        existing_presentations=0,
        recommendations=[
            RecommendationItem(
                id_bien=101,
                reference_externe="BIEN-101",
                matching_score=Decimal("98.50"),
                rank=1,
                presentation_id=501,
                persisted=True,
            ),
            RecommendationItem(
                id_bien=102,
                reference_externe="BIEN-102",
                matching_score=Decimal("94.25"),
                rank=2,
                presentation_id=502,
                persisted=True,
            ),
        ],
    )


def test_generate_recommendations_success() -> None:
    db = MagicMock()
    service = MagicMock()

    expected = build_response()

    service.generate_recommendations.return_value = (
        expected
    )

    with patch(
        "src.api.api.v1.endpoints.recommendations.RecommendationService",
        return_value=service,
    ):
        result = generate_recommendations(
            id_demande_version=55,
            limit=10,
            db=db,
        )

    assert result is expected
    assert result.id_demande_version == 55
    assert result.selected_candidates == 2
    assert result.created_presentations == 2

    service.generate_recommendations.assert_called_once_with(
        id_demande_version=55,
        limit=10,
    )


def test_generate_recommendations_returns_404_when_demande_missing() -> None:
    db = MagicMock()
    service = MagicMock()

    service.generate_recommendations.side_effect = (
        RecommendationValidationError(
            "DemandeVersion 999 does not exist."
        )
    )

    with patch(
        "src.api.api.v1.endpoints.recommendations.RecommendationService",
        return_value=service,
    ):
        with pytest.raises(
            HTTPException
        ) as exc:
            generate_recommendations(
                id_demande_version=999,
                limit=10,
                db=db,
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "DemandeVersion 999 does not exist."
    )


def test_generate_recommendations_returns_422_for_validation_error() -> None:
    db = MagicMock()
    service = MagicMock()

    service.generate_recommendations.side_effect = (
        RecommendationValidationError(
            "The demande version must contain "
            "a maximum budget before candidate retrieval."
        )
    )

    with patch(
        "src.api.api.v1.endpoints.recommendations.RecommendationService",
        return_value=service,
    ):
        with pytest.raises(
            HTTPException
        ) as exc:
            generate_recommendations(
                id_demande_version=55,
                limit=10,
                db=db,
            )

    assert exc.value.status_code == 422


def test_generate_recommendations_returns_409_on_persistence_error() -> None:
    db = MagicMock()
    service = MagicMock()

    service.generate_recommendations.side_effect = (
        RecommendationPersistenceError(
            "Unable to persist recommendations "
            "because a database constraint was violated."
        )
    )

    with patch(
        "src.api.api.v1.endpoints.recommendations.RecommendationService",
        return_value=service,
    ):
        with pytest.raises(
            HTTPException
        ) as exc:
            generate_recommendations(
                id_demande_version=55,
                limit=10,
                db=db,
            )

    assert exc.value.status_code == 409
    assert exc.value.detail == (
        "Unable to persist recommendations "
        "because a database constraint was violated."
    )