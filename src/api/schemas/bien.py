from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class BienStatut(StrEnum):
    ACTIF = "ACTIF"
    EXPIRE = "EXPIRE"
    VENDU = "VENDU"
    INDISPONIBLE = "INDISPONIBLE"


class BienRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_bien: int
    reference_externe: str
    type_bien: str

    titre: str | None
    adresse: str | None
    code_postal: str | None
    ville: str | None

    latitude: Decimal | None
    longitude: Decimal | None

    prix: Decimal | None
    surface: Decimal | None
    nb_pieces: int | None
    nb_chambres: int | None
    dpe: str | None

    description: str | None

    date_publication: datetime | None
    date_collecte: datetime

    statut: BienStatut
    id_source: int