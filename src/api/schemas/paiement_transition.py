from datetime import date
from typing import Literal

from pydantic import BaseModel


PaiementTargetStatus = Literal[
    "RECU",
    "VERIFIE",
    "PROGRAMME",
    "PAYE",
    "ANNULE",
]


class PaiementTransitionRequest(
    BaseModel
):
    statut: PaiementTargetStatus

    date_reception_honoraires: (
        date | None
    ) = None

    date_paiement_chasseur: (
        date | None
    ) = None

    motif_annulation: (
        str | None
    ) = None