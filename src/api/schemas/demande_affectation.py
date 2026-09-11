from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DemandeAffectationStatut(StrEnum):
    ASSIGNEE = "ASSIGNEE"
    ACCEPTEE = "ACCEPTEE"
    REFUSEE = "REFUSEE"


class DemandeAffectationCreate(BaseModel):
    id_chasseur: int = Field(gt=0)


class DemandeAffectationDecision(BaseModel):
    statut: DemandeAffectationStatut
    motif_refus: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_decision(self):
        if self.statut == DemandeAffectationStatut.ASSIGNEE:
            raise ValueError(
                "assignment decision must be ACCEPTEE or REFUSEE"
            )

        if (
            self.statut != DemandeAffectationStatut.REFUSEE
            and self.motif_refus is not None
        ):
            raise ValueError(
                "motif_refus is only allowed for a refused assignment"
            )

        return self


class DemandeAffectationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_affectation: int
    id_demande: int
    id_chasseur: int
    statut: DemandeAffectationStatut
    date_affectation: datetime
    date_decision: datetime | None
    id_utilisateur_affectation: int | None
    id_utilisateur_decision: int | None
    motif_refus: str | None