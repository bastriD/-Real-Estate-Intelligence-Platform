from decimal import Decimal

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    id_bien: int
    reference_externe: str | None = None
    matching_score: Decimal = Field(
        ge=0,
        le=100,
    )
    rank: int = Field(
        ge=1,
    )
    presentation_id: int | None = None
    persisted: bool


class RecommendationResponse(BaseModel):
    id_demande_version: int
    requested_limit: int
    eligible_candidates: int
    selected_candidates: int
    created_presentations: int
    existing_presentations: int
    recommendations: list[RecommendationItem]