from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MandatType(StrEnum):
    EXCLUSIF = "EXCLUSIF"
    NON_EXCLUSIF = "NON_EXCLUSIF"


class ModeSignature(StrEnum):
    PAPIER = "PAPIER"
    ELECTRONIQUE = "ELECTRONIQUE"
    AUTRE = "AUTRE"
    INCONNU = "INCONNU"


class MandatStatut(StrEnum):
    BROUILLON = "BROUILLON"
    ACTIF = "ACTIF"
    SUSPENDU = "SUSPENDU"
    TERMINE = "TERMINE"
    EXPIRE = "EXPIRE"
    ANNULE = "ANNULE"


class MandatPeriodeType(StrEnum):
    INITIAL = "INITIAL"
    RENOUVELLEMENT = "RENOUVELLEMENT"


class MandatBase(BaseModel):
    reference_mandat: str = Field(min_length=1, max_length=80)
    type_mandat: MandatType
    date_signature: date
    mode_signature: ModeSignature
    date_debut: date
    date_fin: date
    statut: MandatStatut = MandatStatut.ACTIF
    commentaire: str | None = None
    id_client: int = Field(gt=0)
    id_chasseur: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_fin < self.date_debut:
            raise ValueError(
                "date_fin must be greater than or equal to date_debut"
            )

        return self


class MandatCreate(MandatBase):
    pass


class MandatUpdate(BaseModel):
    reference_mandat: str | None = Field(
        default=None,
        min_length=1,
        max_length=80,
    )
    type_mandat: MandatType | None = None
    date_signature: date | None = None
    mode_signature: ModeSignature | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    statut: MandatStatut | None = None
    commentaire: str | None = None
    id_client: int | None = Field(default=None, gt=0)
    id_chasseur: int | None = Field(default=None, gt=0)


class MandatRead(MandatBase):
    model_config = ConfigDict(from_attributes=True)

    id_mandat: int


class MandatPeriodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_mandat_periode: int
    id_mandat: int
    numero_periode: int
    type_periode: MandatPeriodeType
    date_debut: date
    date_fin: date
    date_renouvellement: date | None
    commentaire: str | None
    est_historique_legacy: bool
    created_at: datetime


class MandatRenew(BaseModel):
    date_renouvellement: date
    commentaire: str | None = None


class MandatRenewResponse(BaseModel):
    mandat: MandatRead
    periode: MandatPeriodeRead