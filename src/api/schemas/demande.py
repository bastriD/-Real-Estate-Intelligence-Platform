from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DemandeStatut(StrEnum):
    ACTIVE = "ACTIVE"
    SUSPENDUE = "SUSPENDUE"
    CLOTUREE = "CLOTUREE"
    ANNULEE = "ANNULEE"


class DPE(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


class DemandeVersionCriteria(BaseModel):
    ville: str | None = Field(default=None, max_length=120)
    code_postal: str | None = Field(default=None, max_length=20)
    type_bien: str | None = Field(default=None, max_length=50)

    budget_min: Decimal | None = Field(default=None, ge=0)
    budget_max: Decimal | None = Field(default=None, ge=0)
    surface_min: Decimal | None = Field(default=None, ge=0)

    nb_pieces_min: int | None = Field(default=None, ge=0)
    nb_chambres_min: int | None = Field(default=None, ge=0)

    dpe_max: DPE | None = None

    criteres_souhaites: list[Any] | dict[str, Any] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_budget_range(self):
        if (
            self.budget_min is not None
            and self.budget_max is not None
            and self.budget_min > self.budget_max
        ):
            raise ValueError(
                "budget_min must be less than or equal to budget_max"
            )
        return self


class DemandeCreate(DemandeVersionCriteria):
    reference_demande: str | None = Field(
        default=None,
        max_length=80,
    )
    statut: DemandeStatut = DemandeStatut.ACTIVE
    id_mandat: int = Field(gt=0)

    motif_modification: str = Field(min_length=1)

    auteur_client_id: int | None = Field(default=None, gt=0)
    auteur_chasseur_id: int | None = Field(default=None, gt=0)
    auteur_systeme: bool = False

    @model_validator(mode="after")
    def validate_author(self):
        authors = (
            int(self.auteur_client_id is not None)
            + int(self.auteur_chasseur_id is not None)
            + int(self.auteur_systeme)
        )

        if authors != 1:
            raise ValueError(
                "exactly one author must be provided: "
                "client, chasseur or system"
            )

        return self


class DemandeRevision(DemandeVersionCriteria):
    motif_modification: str = Field(min_length=1)

    auteur_client_id: int | None = Field(default=None, gt=0)
    auteur_chasseur_id: int | None = Field(default=None, gt=0)
    auteur_systeme: bool = False

    @model_validator(mode="after")
    def validate_author(self):
        authors = (
            int(self.auteur_client_id is not None)
            + int(self.auteur_chasseur_id is not None)
            + int(self.auteur_systeme)
        )

        if authors != 1:
            raise ValueError(
                "exactly one author must be provided: "
                "client, chasseur or system"
            )

        return self


class DemandeStatusUpdate(BaseModel):
    statut: DemandeStatut


class DemandeVersionRead(DemandeVersionCriteria):
    model_config = ConfigDict(from_attributes=True)

    id_demande_version: int
    numero_version: int
    date_version: datetime
    motif_modification: str

    active: bool
    id_demande: int

    auteur_client_id: int | None
    auteur_chasseur_id: int | None
    auteur_systeme: bool


class DemandeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_demande: int
    reference_demande: str | None
    date_creation: datetime
    statut: DemandeStatut
    id_mandat: int


class DemandeWithCurrentVersion(DemandeRead):
    current_version: DemandeVersionRead


class DemandeHistory(DemandeRead):
    versions: list[DemandeVersionRead]