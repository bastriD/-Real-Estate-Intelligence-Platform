from __future__ import annotations

import time
from decimal import Decimal
from typing import Any

import pandas as pd
import psycopg
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.ai.matching.features import (
    build_matching_features,
    compute_matching_score,
)
from src.ai.matching.repository import (
    load_matching_input,
)
from src.api.core.config import settings
from src.api.db.models.presentation import Presentation
from src.api.observability.metrics import (
    RECOMMENDATION_DURATION_SECONDS,
    RECOMMENDATION_ELIGIBLE_CANDIDATES,
    RECOMMENDATION_FAILURES_TOTAL,
    RECOMMENDATION_PRESENTATIONS_CREATED,
    RECOMMENDATION_PRESENTATIONS_EXISTING,
    RECOMMENDATION_REQUESTS_TOTAL,
    RECOMMENDATION_SELECTED_CANDIDATES,
)
from src.api.repositories.presentation import (
    PresentationRepository,
)
from src.api.schemas.recommendation import (
    RecommendationItem,
    RecommendationResponse,
)


class RecommendationValidationError(
    ValueError
):
    pass


class RecommendationPersistenceError(
    RuntimeError
):
    pass


class RecommendationService:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db
        self.presentation_repository = (
            PresentationRepository(db)
        )

    def generate_recommendations(
        self,
        *,
        id_demande_version: int,
        limit: int,
    ) -> RecommendationResponse:
        """
        Generate and persist deterministic Top-N recommendations.

        Prometheus instrumentation records:

        - total recommendation requests,
        - failures by stable failure category,
        - execution duration,
        - eligible candidate distribution,
        - selected candidate distribution,
        - newly created presentation distribution,
        - reused presentation distribution.

        Business identifiers such as id_demande_version and id_bien are
        intentionally not used as Prometheus labels in order to avoid
        high-cardinality time series.
        """

        RECOMMENDATION_REQUESTS_TOTAL.inc()

        start_time = time.perf_counter()

        try:
            response = self._generate_recommendations(
                id_demande_version=id_demande_version,
                limit=limit,
            )

        except RecommendationValidationError:
            RECOMMENDATION_FAILURES_TOTAL.labels(
                failure_type="validation",
            ).inc()

            raise

        except RecommendationPersistenceError:
            RECOMMENDATION_FAILURES_TOTAL.labels(
                failure_type="persistence",
            ).inc()

            raise

        except Exception:
            RECOMMENDATION_FAILURES_TOTAL.labels(
                failure_type="unexpected",
            ).inc()

            raise

        else:
            self._observe_recommendation_result(
                response
            )

            return response

        finally:
            duration = (
                time.perf_counter()
                - start_time
            )

            RECOMMENDATION_DURATION_SECONDS.observe(
                duration
            )

    def _generate_recommendations(
        self,
        *,
        id_demande_version: int,
        limit: int,
    ) -> RecommendationResponse:
        """
        Execute the recommendation business workflow.

        Prometheus lifecycle instrumentation is deliberately handled by
        generate_recommendations() so that business logic remains focused
        on matching and persistence.
        """

        if id_demande_version <= 0:
            raise RecommendationValidationError(
                "id_demande_version must be greater than 0."
            )

        if limit <= 0:
            raise RecommendationValidationError(
                "limit must be greater than 0."
            )

        if limit > 100:
            raise RecommendationValidationError(
                "limit must not exceed 100."
            )

        try:
            demande, biens = self._load_matching_input(
                id_demande_version=id_demande_version
            )

        except ValueError as exc:
            raise RecommendationValidationError(
                str(exc)
            ) from exc

        eligible_candidates = len(
            biens
        )

        if biens.empty:
            return RecommendationResponse(
                id_demande_version=id_demande_version,
                requested_limit=limit,
                eligible_candidates=0,
                selected_candidates=0,
                created_presentations=0,
                existing_presentations=0,
                recommendations=[],
            )

        demande_series = pd.Series(
            demande
        )

        features = build_matching_features(
            biens=biens,
            demande=demande_series,
        )

        ranked = compute_matching_score(
            features=features,
        )

        selected = (
            ranked
            .head(limit)
            .reset_index(
                drop=True
            )
        )

        recommendations: list[
            RecommendationItem
        ] = []

        created_presentations: list[
            tuple[
                RecommendationItem,
                Presentation,
            ]
        ] = []

        created_count = 0
        existing_count = 0

        try:
            for index, row in selected.iterrows():
                id_bien = int(
                    row["id_bien"]
                )

                score = Decimal(
                    str(
                        row[
                            "matching_score"
                        ]
                    )
                )

                reference_externe = (
                    self._safe_optional_string(
                        row.get(
                            "reference_externe"
                        )
                    )
                )

                existing = (
                    self.presentation_repository
                    .get_by_demande_and_bien(
                        id_demande_version,
                        id_bien,
                    )
                )

                if existing is not None:
                    existing_count += 1

                    recommendations.append(
                        RecommendationItem(
                            id_bien=id_bien,
                            reference_externe=(
                                reference_externe
                            ),
                            matching_score=score,
                            rank=index + 1,
                            presentation_id=(
                                existing.id_presentation
                            ),
                            persisted=True,
                        )
                    )

                    continue

                presentation = Presentation(
                    id_demande_version=(
                        id_demande_version
                    ),
                    id_bien=id_bien,
                    score_matching=score,
                    statut="IDENTIFIE",
                    date_presentation=None,
                )

                created = (
                    self.presentation_repository
                    .create(
                        presentation
                    )
                )

                recommendation = (
                    RecommendationItem(
                        id_bien=id_bien,
                        reference_externe=(
                            reference_externe
                        ),
                        matching_score=score,
                        rank=index + 1,
                        presentation_id=None,
                        persisted=True,
                    )
                )

                recommendations.append(
                    recommendation
                )

                created_presentations.append(
                    (
                        recommendation,
                        created,
                    )
                )

                created_count += 1

            # One flush assigns database-generated IDs to all newly
            # created Presentation objects while keeping the complete
            # recommendation operation transactional.
            self.db.flush()

            for (
                recommendation,
                presentation,
            ) in created_presentations:
                recommendation.presentation_id = (
                    presentation.id_presentation
                )

            # One commit for the complete Top-N operation.
            self.db.commit()

        except IntegrityError as exc:
            self.db.rollback()

            raise RecommendationPersistenceError(
                "Unable to persist recommendations "
                "because a database constraint was violated."
            ) from exc

        except Exception:
            self.db.rollback()
            raise

        return RecommendationResponse(
            id_demande_version=(
                id_demande_version
            ),
            requested_limit=limit,
            eligible_candidates=(
                eligible_candidates
            ),
            selected_candidates=(
                len(selected)
            ),
            created_presentations=(
                created_count
            ),
            existing_presentations=(
                existing_count
            ),
            recommendations=(
                recommendations
            ),
        )

    @staticmethod
    def _observe_recommendation_result(
        response: RecommendationResponse,
    ) -> None:
        """
        Record business-result distributions for a successful request.

        This includes valid requests returning zero eligible candidates.
        """

        RECOMMENDATION_ELIGIBLE_CANDIDATES.observe(
            response.eligible_candidates
        )

        RECOMMENDATION_SELECTED_CANDIDATES.observe(
            response.selected_candidates
        )

        RECOMMENDATION_PRESENTATIONS_CREATED.observe(
            response.created_presentations
        )

        RECOMMENDATION_PRESENTATIONS_EXISTING.observe(
            response.existing_presentations
        )

    def _load_matching_input(
        self,
        *,
        id_demande_version: int,
    ) -> tuple[
        dict[str, Any],
        pd.DataFrame,
    ]:
        with psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
        ) as connection:
            return load_matching_input(
                connection=connection,
                id_demande_version=(
                    id_demande_version
                ),
            )

    @staticmethod
    def _safe_optional_string(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if pd.isna(value):
            return None

        return str(value)