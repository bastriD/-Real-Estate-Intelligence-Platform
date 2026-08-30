from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class PresentationStatut(StrEnum):
    IDENTIFIE = "IDENTIFIE"
    QUALIFIE = "QUALIFIE"
    PRESENTE = "PRESENTE"
    REJETE = "REJETE"
    VISITE = "VISITE"
    RETENU = "RETENU"


class PresentationCreate(BaseModel):
    id_demande_version: int = Field(gt=0)
    id_bien: int = Field(gt=0)

    score_matching: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    statut: PresentationStatut = PresentationStatut.IDENTIFIE

    date_presentation: datetime | None = None


class PresentationUpdate(BaseModel):
    score_matching: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    statut: PresentationStatut | None = None
    date_presentation: datetime | None = None


class PresentationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_presentation: int
    date_selection: datetime
    date_presentation: datetime | None
    score_matching: Decimal | None
    statut: PresentationStatut
    id_demande_version: int
    id_bien: int