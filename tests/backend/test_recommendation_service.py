from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from sqlalchemy.exc import IntegrityError

from prometheus_client import REGISTRY

from src.api.observability.metrics import (
    RECOMMENDATION_DURATION_SECONDS,
    RECOMMENDATION_ELIGIBLE_CANDIDATES,
    RECOMMENDATION_FAILURES_TOTAL,
    RECOMMENDATION_PRESENTATIONS_CREATED,
    RECOMMENDATION_PRESENTATIONS_EXISTING,
    RECOMMENDATION_REQUESTS_TOTAL,
    RECOMMENDATION_SELECTED_CANDIDATES,
)

from src.api.services.recommendation import (
    RecommendationPersistenceError,
    RecommendationService,
    RecommendationValidationError,
)


def build_matching_input():
    demande = {
        "id_demande_version": 55,
        "ville": "Paris",
        "code_postal": "75000",
        "type_bien": "Studio",
        "budget_min": Decimal("150000"),
        "budget_max": Decimal("250000"),
        "surface_min": Decimal("20"),
        "nb_pieces_min": 1,
        "nb_chambres_min": 1,
        "dpe_max": "D",
    }

    biens = pd.DataFrame(
        [
            {
                "id_bien": 101,
                "reference_externe": "BIEN-101",
                "type_bien": "Studio",
                "ville": "Paris",
                "code_postal": "75001",
                "prix": Decimal("180000"),
                "surface": Decimal("30"),
                "nb_pieces": 1,
                "nb_chambres": 1,
                "dpe": "C",
            },
            {
                "id_bien": 102,
                "reference_externe": "BIEN-102",
                "type_bien": "Studio",
                "ville": "Paris",
                "code_postal": "75002",
                "prix": Decimal("220000"),
                "surface": Decimal("25"),
                "nb_pieces": 1,
                "nb_chambres": 1,
                "dpe": "D",
            },
            {
                "id_bien": 103,
                "reference_externe": "BIEN-103",
                "type_bien": "Studio",
                "ville": "Paris",
                "code_postal": "75003",
                "prix": Decimal("240000"),
                "surface": Decimal("22"),
                "nb_pieces": 1,
                "nb_chambres": 1,
                "dpe": "E",
            },
        ]
    )

    return demande, biens


def build_ranked_candidates():
    return pd.DataFrame(
        [
            {
                "id_bien": 101,
                "reference_externe": "BIEN-101",
                "matching_score": 98.50,
            },
            {
                "id_bien": 102,
                "reference_externe": "BIEN-102",
                "matching_score": 94.25,
            },
            {
                "id_bien": 103,
                "reference_externe": "BIEN-103",
                "matching_score": 88.75,
            },
        ]
    )


def test_generate_recommendations_rejects_invalid_demande_version() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    with pytest.raises(
        RecommendationValidationError
    ):
        service.generate_recommendations(
            id_demande_version=0,
            limit=10,
        )


def test_generate_recommendations_rejects_invalid_limit() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    with pytest.raises(
        RecommendationValidationError
    ):
        service.generate_recommendations(
            id_demande_version=55,
            limit=0,
        )


def test_generate_recommendations_rejects_limit_over_100() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    with pytest.raises(
        RecommendationValidationError
    ):
        service.generate_recommendations(
            id_demande_version=55,
            limit=101,
        )


def test_generate_recommendations_returns_empty_result() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    service._load_matching_input = MagicMock(
        return_value=(
            {
                "id_demande_version": 55,
            },
            pd.DataFrame(),
        )
    )

    result = service.generate_recommendations(
        id_demande_version=55,
        limit=10,
    )

    assert result.id_demande_version == 55
    assert result.eligible_candidates == 0
    assert result.selected_candidates == 0
    assert result.created_presentations == 0
    assert result.existing_presentations == 0
    assert result.recommendations == []

    db.commit.assert_not_called()


def test_generate_recommendations_creates_ranked_presentations() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    service._load_matching_input = MagicMock(
        return_value=build_matching_input()
    )

    service.presentation_repository.get_by_demande_and_bien = MagicMock(
        return_value=None
    )

    created_presentations = [
        SimpleNamespace(
            id_presentation=501
        ),
        SimpleNamespace(
            id_presentation=502
        ),
    ]

    service.presentation_repository.create = MagicMock(
        side_effect=created_presentations
    )

    service.presentation_repository.get_by_id = MagicMock(
        side_effect=created_presentations
    )

    with patch(
        "src.api.services.recommendation.build_matching_features",
        return_value=build_ranked_candidates(),
    ), patch(
        "src.api.services.recommendation.compute_matching_score",
        return_value=build_ranked_candidates(),
    ):
        result = service.generate_recommendations(
            id_demande_version=55,
            limit=2,
        )

    assert result.id_demande_version == 55
    assert result.requested_limit == 2
    assert result.eligible_candidates == 3
    assert result.selected_candidates == 2
    assert result.created_presentations == 2
    assert result.existing_presentations == 0
    assert len(result.recommendations) == 2

    assert result.recommendations[0].id_bien == 101
    assert result.recommendations[0].rank == 1
    assert result.recommendations[0].matching_score == Decimal(
        "98.5"
    )

    assert result.recommendations[1].id_bien == 102
    assert result.recommendations[1].rank == 2

    assert (
        service.presentation_repository.create.call_count
        == 2
    )

    db.flush.assert_called_once()
    db.commit.assert_called_once()


def test_generate_recommendations_reuses_existing_presentation() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    service._load_matching_input = MagicMock(
        return_value=build_matching_input()
    )

    existing = SimpleNamespace(
        id_presentation=700
    )

    created = SimpleNamespace(
        id_presentation=701
    )

    service.presentation_repository.get_by_demande_and_bien = MagicMock(
        side_effect=[
            existing,
            None,
        ]
    )

    service.presentation_repository.create = MagicMock(
        return_value=created
    )

    service.presentation_repository.get_by_id = MagicMock(
        return_value=created
    )

    with patch(
        "src.api.services.recommendation.build_matching_features",
        return_value=build_ranked_candidates(),
    ), patch(
        "src.api.services.recommendation.compute_matching_score",
        return_value=build_ranked_candidates(),
    ):
        result = service.generate_recommendations(
            id_demande_version=55,
            limit=2,
        )

    assert result.created_presentations == 1
    assert result.existing_presentations == 1

    assert (
        result.recommendations[0].presentation_id
        == 700
    )

    assert (
        result.recommendations[1].presentation_id
        == 701
    )

    service.presentation_repository.create.assert_called_once()

    db.commit.assert_called_once()


def test_generate_recommendations_translates_matching_error() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    service._load_matching_input = MagicMock(
        side_effect=ValueError(
            "DemandeVersion 999 does not exist."
        )
    )

    with pytest.raises(
        RecommendationValidationError
    ) as exc:
        service.generate_recommendations(
            id_demande_version=999,
            limit=10,
        )

    assert (
        str(exc.value)
        == "DemandeVersion 999 does not exist."
    )


def test_generate_recommendations_rolls_back_on_integrity_error() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    service._load_matching_input = MagicMock(
        return_value=build_matching_input()
    )

    service.presentation_repository.get_by_demande_and_bien = MagicMock(
        return_value=None
    )

    service.presentation_repository.create = MagicMock(
        side_effect=IntegrityError(
            "statement",
            {},
            Exception(
                "database constraint"
            ),
        )
    )

    with patch(
        "src.api.services.recommendation.build_matching_features",
        return_value=build_ranked_candidates(),
    ), patch(
        "src.api.services.recommendation.compute_matching_score",
        return_value=build_ranked_candidates(),
    ):
        with pytest.raises(
            RecommendationPersistenceError
        ):
            service.generate_recommendations(
                id_demande_version=55,
                limit=2,
            )

    db.rollback.assert_called_once()
    db.commit.assert_not_called()

def _sample_value(
    name: str,
    labels: dict[str, str] | None = None,
) -> float:
    value = REGISTRY.get_sample_value(
        name,
        labels or {},
    )

    assert value is not None

    return float(value)


def test_recommendation_metrics_record_success() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    service._load_matching_input = MagicMock(
        return_value=build_matching_input()
    )

    service.presentation_repository.get_by_demande_and_bien = MagicMock(
        return_value=None
    )

    created_presentations = [
        SimpleNamespace(
            id_presentation=801
        ),
        SimpleNamespace(
            id_presentation=802
        ),
    ]

    service.presentation_repository.create = MagicMock(
        side_effect=created_presentations
    )

    requests_before = _sample_value(
        "real_estate_recommendation_requests_total"
    )

    eligible_count_before = _sample_value(
        "real_estate_recommendation_eligible_candidates_count"
    )

    eligible_sum_before = _sample_value(
        "real_estate_recommendation_eligible_candidates_sum"
    )

    selected_count_before = _sample_value(
        "real_estate_recommendation_selected_candidates_count"
    )

    selected_sum_before = _sample_value(
        "real_estate_recommendation_selected_candidates_sum"
    )

    created_count_before = _sample_value(
        "real_estate_recommendation_presentations_created_count"
    )

    created_sum_before = _sample_value(
        "real_estate_recommendation_presentations_created_sum"
    )

    existing_count_before = _sample_value(
        "real_estate_recommendation_presentations_existing_count"
    )

    existing_sum_before = _sample_value(
        "real_estate_recommendation_presentations_existing_sum"
    )

    duration_count_before = _sample_value(
        "real_estate_recommendation_duration_seconds_count"
    )

    with patch(
        "src.api.services.recommendation.build_matching_features",
        return_value=build_ranked_candidates(),
    ), patch(
        "src.api.services.recommendation.compute_matching_score",
        return_value=build_ranked_candidates(),
    ):
        result = service.generate_recommendations(
            id_demande_version=55,
            limit=2,
        )

    assert result.eligible_candidates == 3
    assert result.selected_candidates == 2
    assert result.created_presentations == 2
    assert result.existing_presentations == 0

    assert _sample_value(
        "real_estate_recommendation_requests_total"
    ) == requests_before + 1

    assert _sample_value(
        "real_estate_recommendation_eligible_candidates_count"
    ) == eligible_count_before + 1

    assert _sample_value(
        "real_estate_recommendation_eligible_candidates_sum"
    ) == eligible_sum_before + 3

    assert _sample_value(
        "real_estate_recommendation_selected_candidates_count"
    ) == selected_count_before + 1

    assert _sample_value(
        "real_estate_recommendation_selected_candidates_sum"
    ) == selected_sum_before + 2

    assert _sample_value(
        "real_estate_recommendation_presentations_created_count"
    ) == created_count_before + 1

    assert _sample_value(
        "real_estate_recommendation_presentations_created_sum"
    ) == created_sum_before + 2

    assert _sample_value(
        "real_estate_recommendation_presentations_existing_count"
    ) == existing_count_before + 1

    assert _sample_value(
        "real_estate_recommendation_presentations_existing_sum"
    ) == existing_sum_before

    assert _sample_value(
        "real_estate_recommendation_duration_seconds_count"
    ) == duration_count_before + 1


def test_recommendation_metrics_record_validation_failure() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    requests_before = _sample_value(
        "real_estate_recommendation_requests_total"
    )

    failures_before = _sample_value(
        "real_estate_recommendation_failures_total",
        {
            "failure_type": "validation",
        },
    )

    duration_count_before = _sample_value(
        "real_estate_recommendation_duration_seconds_count"
    )

    with pytest.raises(
        RecommendationValidationError
    ):
        service.generate_recommendations(
            id_demande_version=0,
            limit=10,
        )

    assert _sample_value(
        "real_estate_recommendation_requests_total"
    ) == requests_before + 1

    assert _sample_value(
        "real_estate_recommendation_failures_total",
        {
            "failure_type": "validation",
        },
    ) == failures_before + 1

    assert _sample_value(
        "real_estate_recommendation_duration_seconds_count"
    ) == duration_count_before + 1


def test_recommendation_metrics_record_empty_success() -> None:
    db = MagicMock()
    service = RecommendationService(db)

    service._load_matching_input = MagicMock(
        return_value=(
            {
                "id_demande_version": 55,
            },
            pd.DataFrame(),
        )
    )

    eligible_count_before = _sample_value(
        "real_estate_recommendation_eligible_candidates_count"
    )

    eligible_sum_before = _sample_value(
        "real_estate_recommendation_eligible_candidates_sum"
    )

    selected_count_before = _sample_value(
        "real_estate_recommendation_selected_candidates_count"
    )

    selected_sum_before = _sample_value(
        "real_estate_recommendation_selected_candidates_sum"
    )

    result = service.generate_recommendations(
        id_demande_version=55,
        limit=10,
    )

    assert result.eligible_candidates == 0
    assert result.selected_candidates == 0

    assert _sample_value(
        "real_estate_recommendation_eligible_candidates_count"
    ) == eligible_count_before + 1

    assert _sample_value(
        "real_estate_recommendation_eligible_candidates_sum"
    ) == eligible_sum_before

    assert _sample_value(
        "real_estate_recommendation_selected_candidates_count"
    ) == selected_count_before + 1

    assert _sample_value(
        "real_estate_recommendation_selected_candidates_sum"
    ) == selected_sum_before