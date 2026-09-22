from sqlalchemy import select

from src.api.db.models.notaire import DossierNotarial, MouvementNotarial, Notaire
from src.api.db.models.offre import Offre
from src.api.db.models.presentation import Presentation
from src.api.db.models.demande import Demande, DemandeVersion
from src.api.db.models.paiement import Paiement


class NotaireRepository:
    def __init__(self, session):
        self.session = session

    def add(self, entity):
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def notaires(self):
        return list(self.session.scalars(select(Notaire).order_by(Notaire.id_notaire)).all())

    def dossier(self, identifier, *, lock=False):
        statement = select(DossierNotarial).where(DossierNotarial.id_dossier_notarial == identifier)
        return self.session.scalar(statement.with_for_update() if lock else statement)

    def offer_context(self, identifier):
        return self.session.execute(
            select(Offre, Demande.id_mandat)
            .join(Presentation, Presentation.id_presentation == Offre.id_presentation)
            .join(DemandeVersion, DemandeVersion.id_demande_version == Presentation.id_demande_version)
            .join(Demande, Demande.id_demande == DemandeVersion.id_demande)
            .where(Offre.id_offre == identifier).with_for_update(of=Offre)
        ).one_or_none()

    def payment(self, vente_id):
        return self.session.scalar(select(Paiement).where(Paiement.id_vente == vente_id).with_for_update())

    def movements(self, identifier):
        return list(self.session.scalars(select(MouvementNotarial).where(
            MouvementNotarial.id_dossier_notarial == identifier,
        ).order_by(MouvementNotarial.id_mouvement_notarial)).all())
