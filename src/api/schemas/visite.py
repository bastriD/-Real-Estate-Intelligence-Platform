from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class VisiteStatut(StrEnum):
    PLANIFIEE = "PLANIFIEE"
    REALISEE = "REALISEE"
    ANNULEE = "ANNULEE"
    REPORTEE = "REPORTEE"


class VisiteCreate(BaseModel):
    date_visite: datetime
    id_presentation: int = Field(gt=0)

    statut: VisiteStatut = VisiteStatut.PLANIFIEE
    compte_rendu: str | None = None
    note: int | None = Field(default=None, ge=0, le=5)

    photos: list[str] = Field(default_factory=list)


class VisiteUpdate(BaseModel):
    date_visite: datetime | None = None
    statut: VisiteStatut | None = None
    compte_rendu: str | None = None
    note: int | None = Field(default=None, ge=0, le=5)

    photos: list[str] | None = None


class VisiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_visite: int
    date_visite: datetime
    statut: VisiteStatut
    compte_rendu: str | None
    note: int | None
    photos: list[str]
    date_creation: datetime
    id_presentation: int