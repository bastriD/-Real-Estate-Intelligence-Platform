from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class VenteOrigine(StrEnum):
    CHASSEUR = "CHASSEUR"
    CLIENT_SEUL = "CLIENT_SEUL"
    AUTRE_AGENCE = "AUTRE_AGENCE"


class VenteCreate(BaseModel):
    id_mandat: int = Field(gt=0)
    id_presentation: int | None = Field(default=None, gt=0)
    id_bien: int | None = Field(default=None, gt=0)

    origine_vente: VenteOrigine

    date_acte_authentique: date

    montant_achat: Decimal = Field(
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )


class VenteRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id_vente: int

    id_mandat: int
    id_mandat_periode: int | None

    id_presentation: int | None
    id_bien: int | None

    id_chasseur_beneficiaire: int | None

    origine_vente: VenteOrigine

    date_acte_authentique: date
    montant_achat: Decimal

    date_creation: datetime