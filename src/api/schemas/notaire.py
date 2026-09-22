from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field, StringConstraints

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Reference = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Money = Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]


class NotaireCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nom: Name
    office: Name
    email: EmailStr


class NotaireRead(NotaireCreate):
    model_config = ConfigDict(from_attributes=True)
    id_notaire: int


class DossierNotarialCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_notaire: int = Field(gt=0)
    id_offre: int = Field(gt=0)
    date_rendez_vous: AwareDatetime


class DossierNotarialRead(DossierNotarialCreate):
    model_config = ConfigDict(from_attributes=True)
    id_dossier_notarial: int
    id_vente: int | None
    reference_acte: str | None
    reference_document: str | None
    date_creation: datetime


class SignatureNotariale(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date_acte_authentique: date
    montant_achat: Money
    reference_acte: Reference
    reference_document: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class NatureMouvement(StrEnum):
    COLLECTE_NOTAIRE = "COLLECTE_NOTAIRE"
    RECEPTION_ENTREPRISE = "RECEPTION_ENTREPRISE"


class MouvementNotarialCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nature: NatureMouvement
    montant: Money
    date_operation: date
    reference: Reference


class MouvementNotarialRead(MouvementNotarialCreate):
    model_config = ConfigDict(from_attributes=True)
    id_mouvement_notarial: int
    id_dossier_notarial: int
    date_creation: datetime
