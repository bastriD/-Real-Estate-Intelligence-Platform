from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.chasseur import Chasseur
from src.api.db.models.demande_affectation import DemandeAffectation
from src.api.repositories.demande import DemandeRepository
from src.api.repositories.demande_affectation import (
    DemandeAffectationRepository,
)
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.demande_affectation import (
    DemandeAffectationDecision,
    DemandeAffectationStatut,
)


class DemandeAffectationNotFoundError(Exception):
    pass


class DemandeAffectationConflictError(Exception):
    pass


class DemandeAffectationAuthorizationError(Exception):
    pass


class DemandeAffectationValidationError(Exception):
    pass


class ChasseurNotFoundForAffectationError(Exception):
    pass


class DemandeAffectationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = DemandeAffectationRepository(session)
        self.demande_repository = DemandeRepository(session)

    def list_by_demande(
        self,
        demande_id: int,
    ) -> list[DemandeAffectation]:
        self._ensure_demande_exists(demande_id)

        return self.repository.list_by_demande(demande_id)

    def get_current(
        self,
        demande_id: int,
    ) -> DemandeAffectation | None:
        self._ensure_demande_exists(demande_id)

        return self.repository.get_current_by_demande(demande_id)

    def get_accepted_owner(
        self,
        demande_id: int,
    ) -> DemandeAffectation | None:
        self._ensure_demande_exists(demande_id)

        return self.repository.get_accepted_by_demande(demande_id)

    def create_assignment(
        self,
        demande_id: int,
        chasseur_id: int,
        current_user: AuthenticatedUser,
    ) -> DemandeAffectation:
        if current_user.role != "ADMIN":
            raise DemandeAffectationAuthorizationError(
                "Only an administrator can assign a demande"
            )

        self._ensure_demande_exists(demande_id)
        self._ensure_chasseur_exists(chasseur_id)

        current = self.repository.get_current_by_demande(
            demande_id,
            for_update=True,
        )

        if current is not None:
            raise DemandeAffectationConflictError(
                f"Demande {demande_id} already has a current assignment"
            )

        affectation = DemandeAffectation(
            id_demande=demande_id,
            id_chasseur=chasseur_id,
            statut=DemandeAffectationStatut.ASSIGNEE.value,
            id_utilisateur_affectation=current_user.id_utilisateur,
        )

        try:
            affectation = self.repository.create(affectation)

            self.session.commit()

            return affectation

        except IntegrityError as exc:
            self.session.rollback()

            raise DemandeAffectationValidationError(
                "Assignment creation violates a database constraint"
            ) from exc

    def decide_assignment(
        self,
        demande_id: int,
        payload: DemandeAffectationDecision,
        current_user: AuthenticatedUser,
    ) -> DemandeAffectation:
        if current_user.role != "CHASSEUR":
            raise DemandeAffectationAuthorizationError(
                "Only a hunter can accept or refuse an assignment"
            )

        if current_user.id_chasseur is None:
            raise DemandeAffectationAuthorizationError(
                "Hunter identity is not available"
            )

        affectation = self.repository.get_pending_for_chasseur(
            demande_id,
            current_user.id_chasseur,
            for_update=True,
        )

        if affectation is None:
            raise DemandeAffectationNotFoundError(
                "Pending assignment not found"
            )

        affectation.statut = payload.statut.value
        affectation.date_decision = datetime.now(timezone.utc)
        affectation.id_utilisateur_decision = (
            current_user.id_utilisateur
        )

        if payload.statut == DemandeAffectationStatut.REFUSEE:
            affectation.motif_refus = payload.motif_refus
        else:
            affectation.motif_refus = None

        try:
            affectation = self.repository.save(affectation)

            self.session.commit()

            return affectation

        except IntegrityError as exc:
            self.session.rollback()

            raise DemandeAffectationValidationError(
                "Assignment decision violates a database constraint"
            ) from exc

    def hunter_can_access_demande(
        self,
        demande_id: int,
        chasseur_id: int,
    ) -> bool:
        current = self.repository.get_current_by_demande(
            demande_id
        )

        if current is None:
            return False

        return current.id_chasseur == chasseur_id

    def hunter_owns_demande(
        self,
        demande_id: int,
        chasseur_id: int,
    ) -> bool:
        accepted = self.repository.get_accepted_by_demande(
            demande_id
        )

        if accepted is None:
            return False

        return accepted.id_chasseur == chasseur_id

    def _ensure_demande_exists(
        self,
        demande_id: int,
    ) -> None:
        if self.demande_repository.get_by_id(demande_id) is None:
            raise DemandeAffectationNotFoundError(
                f"Demande {demande_id} not found"
            )

    def _ensure_chasseur_exists(
        self,
        chasseur_id: int,
    ) -> None:
        statement = select(Chasseur.id_chasseur).where(
            Chasseur.id_chasseur == chasseur_id
        )

        if self.session.scalar(statement) is None:
            raise ChasseurNotFoundForAffectationError(
                f"Chasseur {chasseur_id} not found"
            )