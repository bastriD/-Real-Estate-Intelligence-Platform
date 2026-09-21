from pydantic import BaseModel, ConfigDict, Field


class SecteurRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_secteur: int
    pays: str
    ville: str
    quartier: str | None
    code_postal: str | None
    actif: bool


class BienSecteurUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_secteur: int | None = Field(gt=0)
