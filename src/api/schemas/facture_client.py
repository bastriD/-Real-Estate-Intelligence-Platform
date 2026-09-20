from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FactureClientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_vente: int = Field(gt=0)


class FactureClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_facture_client: int
    id_vente: int
    id_client: int
    id_parametres_honoraires: int
    numero_facture: str
    date_emission: date
    montant_achat: Decimal
    montant_fixe_applique: Decimal
    taux_pourcentage_applique: Decimal
    montant_honoraires_ht: Decimal
    date_creation: datetime
