from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientStatut(StrEnum):
    ACTIF = "ACTIF"
    INACTIF = "INACTIF"
    ARCHIVE = "ARCHIVE"


class ClientBase(BaseModel):
    nom: str = Field(min_length=1, max_length=120)
    prenom: str | None = Field(default=None, max_length=120)
    email: EmailStr
    telephone: str | None = Field(default=None, max_length=40)
    ville: str | None = Field(default=None, max_length=120)
    statut: ClientStatut = ClientStatut.ACTIF
    consentement_contact: bool = False


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=120)
    prenom: str | None = Field(default=None, max_length=120)
    email: EmailStr | None = None
    telephone: str | None = Field(default=None, max_length=40)
    ville: str | None = Field(default=None, max_length=120)
    statut: ClientStatut | None = None
    consentement_contact: bool | None = None


class ClientRead(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id_client: int
    date_creation: datetime