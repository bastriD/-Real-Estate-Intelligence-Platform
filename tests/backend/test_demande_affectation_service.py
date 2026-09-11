from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.demande_affectation import (
    DemandeAffectationDecision,
    DemandeAffectationStatut,
)
from src.api.services.demande_affectation import (
    ChasseurNotFoundForAffectationError,
    DemandeAffectationAuthorizationError,
    DemandeAffectationConflictError,
    DemandeAffectationNotFoundError,
    DemandeAffectationService,
    DemandeAffectationValidationError,
)


def build_admin_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id_utilisateur=1,
        email="admin@example.com",
        role="ADMIN",
    )


def build_chasseur_user(
    id_chasseur: int | None = 4,
    *,
    id_utilisateur: int = 10,
) -> AuthenticatedUser:
    return AuthenticatedUser(
        id_utilisateur=id_utilisateur,
        email=f"chasseur{id_utilisateur}@example.com",
        role="CHASSEUR",
        id_chasseur=id_chasseur,
    )


def build_service():
    session = MagicMock()
    service = DemandeAffectationService(session)

    service.repository = MagicMock()
    service.demande_repository = MagicMock()

    return service, session


def test_create_assignment_success() -> None:
    service, session = build_service()

    service.demande_repository.get_by_id.return_value = (
        SimpleNamespace(id_demande=4)
    )
    session.scalar.return_value = 4
    service.repository.get_current_by_demande.return_value = None

    created = SimpleNamespace(
        id_affectation=20,
        id_demande=4,
        id_chasseur=4,
        statut="ASSIGNEE",
        id_utilisateur_affectation=1,
    )
    service.repository.create.return_value = created

    result = service.create_assignment(
        demande_id=4,
        chasseur_id=4,
        current_user=build_admin_user(),
    )

    assert result is created

    service.repository.get_current_by_demande.assert_called_once_with(
        4,
        for_update=True,
    )

    created_argument = service.repository.create.call_args.args[0]

    assert created_argument.id_demande == 4
    assert created_argument.id_chasseur == 4
    assert created_argument.statut == "ASSIGNEE"
    assert created_argument.id_utilisateur_affectation == 1

    session.commit.assert_called_once()


def test_create_assignment_requires_admin() -> None:
    service, _ = build_service()

    with pytest.raises(
        DemandeAffectationAuthorizationError
    ):
        service.create_assignment(
            demande_id=4,
            chasseur_id=4,
            current_user=build_chasseur_user(),
        )


def test_create_assignment_requires_existing_demande() -> None:
    service, _ = build_service()

    service.demande_repository.get_by_id.return_value = None

    with pytest.raises(
        DemandeAffectationNotFoundError
    ) as exc:
        service.create_assignment(
            demande_id=999,
            chasseur_id=4,
            current_user=build_admin_user(),
        )

    assert str(exc.value) == "Demande 999 not found"


def test_create_assignment_requires_existing_chasseur() -> None:
    service, session = build_service()

    service.demande_repository.get_by_id.return_value = (
        SimpleNamespace(id_demande=4)
    )
    session.scalar.return_value = None

    with pytest.raises(
        ChasseurNotFoundForAffectationError
    ) as exc:
        service.create_assignment(
            demande_id=4,
            chasseur_id=999,
            current_user=build_admin_user(),
        )

    assert str(exc.value) == "Chasseur 999 not found"


def test_create_assignment_rejects_existing_current_assignment() -> None:
    service, session = build_service()

    service.demande_repository.get_by_id.return_value = (
        SimpleNamespace(id_demande=4)
    )
    session.scalar.return_value = 4

    service.repository.get_current_by_demande.return_value = (
        SimpleNamespace(
            id_affectation=20,
            statut="ASSIGNEE",
        )
    )

    with pytest.raises(
        DemandeAffectationConflictError
    ):
        service.create_assignment(
            demande_id=4,
            chasseur_id=4,
            current_user=build_admin_user(),
        )


def test_create_assignment_rolls_back_integrity_error() -> None:
    service, session = build_service()

    service.demande_repository.get_by_id.return_value = (
        SimpleNamespace(id_demande=4)
    )
    session.scalar.return_value = 4
    service.repository.get_current_by_demande.return_value = None

    service.repository.create.side_effect = IntegrityError(
        statement="INSERT",
        params={},
        orig=Exception("constraint"),
    )

    with pytest.raises(
        DemandeAffectationValidationError
    ):
        service.create_assignment(
            demande_id=4,
            chasseur_id=4,
            current_user=build_admin_user(),
        )

    session.rollback.assert_called_once()


def test_decide_assignment_accept_success() -> None:
    service, session = build_service()

    affectation = SimpleNamespace(
        id_affectation=20,
        id_demande=4,
        id_chasseur=4,
        statut="ASSIGNEE",
        date_decision=None,
        id_utilisateur_decision=None,
        motif_refus=None,
    )

    service.repository.get_pending_for_chasseur.return_value = (
        affectation
    )
    service.repository.save.side_effect = lambda obj: obj

    payload = DemandeAffectationDecision(
        statut=DemandeAffectationStatut.ACCEPTEE,
    )

    result = service.decide_assignment(
        demande_id=4,
        payload=payload,
        current_user=build_chasseur_user(
            4,
            id_utilisateur=10,
        ),
    )

    assert result.statut == "ACCEPTEE"
    assert result.date_decision is not None
    assert result.id_utilisateur_decision == 10
    assert result.motif_refus is None

    service.repository.get_pending_for_chasseur.assert_called_once_with(
        4,
        4,
        for_update=True,
    )

    session.commit.assert_called_once()


def test_decide_assignment_refuse_success() -> None:
    service, session = build_service()

    affectation = SimpleNamespace(
        id_affectation=20,
        id_demande=4,
        id_chasseur=4,
        statut="ASSIGNEE",
        date_decision=None,
        id_utilisateur_decision=None,
        motif_refus=None,
    )

    service.repository.get_pending_for_chasseur.return_value = (
        affectation
    )
    service.repository.save.side_effect = lambda obj: obj

    payload = DemandeAffectationDecision(
        statut=DemandeAffectationStatut.REFUSEE,
        motif_refus="Capacity unavailable",
    )

    result = service.decide_assignment(
        demande_id=4,
        payload=payload,
        current_user=build_chasseur_user(
            4,
            id_utilisateur=10,
        ),
    )

    assert result.statut == "REFUSEE"
    assert result.date_decision is not None
    assert result.id_utilisateur_decision == 10
    assert result.motif_refus == "Capacity unavailable"

    session.commit.assert_called_once()


def test_decide_assignment_requires_chasseur_role() -> None:
    service, _ = build_service()

    payload = DemandeAffectationDecision(
        statut=DemandeAffectationStatut.ACCEPTEE,
    )

    with pytest.raises(
        DemandeAffectationAuthorizationError
    ):
        service.decide_assignment(
            demande_id=4,
            payload=payload,
            current_user=build_admin_user(),
        )


def test_decide_assignment_requires_hunter_identity() -> None:
    service, _ = build_service()

    payload = DemandeAffectationDecision(
        statut=DemandeAffectationStatut.ACCEPTEE,
    )

    with pytest.raises(
        DemandeAffectationAuthorizationError
    ) as exc:
        service.decide_assignment(
            demande_id=4,
            payload=payload,
            current_user=build_chasseur_user(None),
        )

    assert str(exc.value) == (
        "Hunter identity is not available"
    )


def test_decide_assignment_wrong_hunter_is_not_found() -> None:
    service, _ = build_service()

    service.repository.get_pending_for_chasseur.return_value = None

    payload = DemandeAffectationDecision(
        statut=DemandeAffectationStatut.ACCEPTEE,
    )

    with pytest.raises(
        DemandeAffectationNotFoundError
    ) as exc:
        service.decide_assignment(
            demande_id=4,
            payload=payload,
            current_user=build_chasseur_user(5),
        )

    assert str(exc.value) == "Pending assignment not found"


def test_decide_assignment_rolls_back_integrity_error() -> None:
    service, session = build_service()

    affectation = SimpleNamespace(
        id_affectation=20,
        id_demande=4,
        id_chasseur=4,
        statut="ASSIGNEE",
        date_decision=None,
        id_utilisateur_decision=None,
        motif_refus=None,
    )

    service.repository.get_pending_for_chasseur.return_value = (
        affectation
    )

    service.repository.save.side_effect = IntegrityError(
        statement="UPDATE",
        params={},
        orig=Exception("constraint"),
    )

    payload = DemandeAffectationDecision(
        statut=DemandeAffectationStatut.ACCEPTEE,
    )

    with pytest.raises(
        DemandeAffectationValidationError
    ):
        service.decide_assignment(
            demande_id=4,
            payload=payload,
            current_user=build_chasseur_user(4),
        )

    session.rollback.assert_called_once()


def test_hunter_can_access_pending_assignment() -> None:
    service, _ = build_service()

    service.repository.get_current_by_demande.return_value = (
        SimpleNamespace(
            id_chasseur=4,
            statut="ASSIGNEE",
        )
    )

    assert (
        service.hunter_can_access_demande(
            demande_id=4,
            chasseur_id=4,
        )
        is True
    )


def test_hunter_cannot_access_other_assignment() -> None:
    service, _ = build_service()

    service.repository.get_current_by_demande.return_value = (
        SimpleNamespace(
            id_chasseur=5,
            statut="ASSIGNEE",
        )
    )

    assert (
        service.hunter_can_access_demande(
            demande_id=4,
            chasseur_id=4,
        )
        is False
    )


def test_hunter_owns_accepted_demande() -> None:
    service, _ = build_service()

    service.repository.get_accepted_by_demande.return_value = (
        SimpleNamespace(
            id_chasseur=4,
            statut="ACCEPTEE",
        )
    )

    assert (
        service.hunter_owns_demande(
            demande_id=4,
            chasseur_id=4,
        )
        is True
    )


def test_hunter_does_not_own_without_accepted_assignment() -> None:
    service, _ = build_service()

    service.repository.get_accepted_by_demande.return_value = None

    assert (
        service.hunter_owns_demande(
            demande_id=4,
            chasseur_id=4,
        )
        is False
    )