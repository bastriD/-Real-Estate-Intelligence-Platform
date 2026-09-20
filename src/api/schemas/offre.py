from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OffreStatut(StrEnum):
    SOUMISE = "SOUMISE"
    ACCEPTEE = "ACCEPTEE"
    REFUSEE = "REFUSEE"
    RETIREE = "RETIREE"
    EXPIREE = "EXPIREE"
    REVISEE = "REVISEE"


class OffreCreate(BaseModel):
    id_presentation: int = Field(gt=0)

    montant: Decimal = Field(
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )

    date_expiration: datetime | None = None
    commentaire: str | None = None


class OffreDecisionStatut(StrEnum):
    ACCEPTEE = "ACCEPTEE"
    REFUSEE = "REFUSEE"
    RETIREE = "RETIREE"


class OffreDecision(BaseModel):
    statut: OffreDecisionStatut
    commentaire: str | None = None


class OffreRevision(BaseModel):
    montant: Decimal = Field(
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )

    date_expiration: datetime | None = None
    commentaire: str | None = None


class OffreRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_offre: int
    id_presentation: int
    numero_version: int

    montant: Decimal

    date_offre: datetime
    date_expiration: datetime | None
    date_decision: datetime | None

    statut: OffreStatut
    commentaire: str | None

    date_creation: datetime