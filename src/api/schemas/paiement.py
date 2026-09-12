from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaiementRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id_paiement: int

    id_mandat: int
    id_bareme: int | None

    date_acte_authentique: date
    montant_achat: Decimal
    montant_honoraires: Decimal
    montant_chasseur: Decimal

    statut: str

    id_vente: int | None
    id_chasseur_beneficiaire: int | None

    id_parametres_honoraires: int | None
    id_parametres_remuneration: int | None

    date_calcul: datetime | None

    droit_remuneration: bool | None
    motif_refus: str | None

    semaines_mandat_acte: int | None
    nb_visites_calcul: int | None
    annees_anciennete_calcul: int | None

    nb_ventes_fenetre: int | None
    nb_mandats_fenetre: int | None

    note_delai: Decimal | None
    note_exclusivite: Decimal | None
    note_ventes: Decimal | None
    note_mandats: Decimal | None
    note_visites: Decimal | None

    score_performance: Decimal | None

    taux_base: Decimal | None
    majoration_anciennete: Decimal | None
    modulation_performance: Decimal | None
    taux_final: Decimal | None