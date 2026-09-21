from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FactureChasseurCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id_paiement: int = Field(gt=0)
    numero_facture: str = Field(min_length=1, max_length=80)
    date_facture: date
    montant: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


class FactureChasseurDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    statut: Literal["CONFORME", "REJETEE"]
    motif_rejet: str | None = Field(default=None, min_length=1, max_length=2000)

    @model_validator(mode="after")
    def validate_reason(self):
        if (self.statut == "REJETEE") != (self.motif_rejet is not None):
            raise ValueError("motif_rejet is required only for REJETEE")
        return self


class FactureChasseurRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_facture_chasseur: int
    id_paiement: int
    id_chasseur: int
    numero_version: int
    numero_facture: str
    date_facture: date
    montant: Decimal
    date_soumission: datetime
    statut: Literal["SOUMISE", "CONFORME", "REJETEE"]
    date_verification: datetime | None
    id_verificateur: int | None
    motif_rejet: str | None
