from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.api.v1.endpoints.demandes import (
    create_demande_affectation,
    decide_demande_affectation,
    list_demande_affectations,
)
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.demande_affectation import (
    DemandeAffectationCreate,
    DemandeAffectationDecision,
    DemandeAffectationStatut,
)
from src.api.services.demande_affectation import (
    ChasseurNotFoundForAffectationError,
    DemandeAffectationAuthorizationError,
    DemandeAffectationConflictError,
    DemandeAffectationNotFoundError,
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


def build_affectation(
    *,
    id_affectation: int = 20,
    id_demande: int = 4,
    id_chasseur: int = 4,
    statut: str = "ASSIGNEE",
    id_utilisateur_affectation: int | None = 1,
    id_utilisateur_decision: int | None = None,
    motif_refus: str | None = None,
):
    decision_date = None

    if statut in {"ACCEPTEE", "REFUSEE"}:
        decision_date = datetime(
            2026,
            9,
            11,
            12,
            30,
            tzinfo=timezone.utc,
        )

    return SimpleNamespace(
        id_affectation=id_affectation,
        id_demande=id_demande,
        id_chasseur=id_chasseur,
        statut=statut,
        date_affectation=datetime(
            2026,
            9,
            11,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        date_decision=decision_date,
        id_utilisateur_affectation=id_utilisateur_affectation,
        id_utilisateur_decision=id_utilisateur_decision,
        motif_refus=motif_refus,
    )


def test_create_demande_affectation_success() -> None:
    db = MagicMock()
    service = MagicMock()

    affectation = build_affectation()
    service.create_assignment.return_value = affectation

    payload = DemandeAffectationCreate(
        id_chasseur=4,
    )
    current_user = build_admin_user()

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        result = create_demande_affectation(
            demande_id=4,
            payload=payload,
            db=db,
            current_user=current_user,
        )

    assert result is affectation

    service.create_assignment.assert_called_once_with(
        demande_id=4,
        chasseur_id=4,
        current_user=current_user,
    )


def test_create_demande_affectation_returns_404_for_missing_demande() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_assignment.side_effect = (
        DemandeAffectationNotFoundError(
            "Demande 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande_affectation(
                demande_id=999,
                payload=DemandeAffectationCreate(
                    id_chasseur=4,
                ),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Demande 999 not found"


def test_create_demande_affectation_returns_404_for_missing_chasseur() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_assignment.side_effect = (
        ChasseurNotFoundForAffectationError(
            "Chasseur 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande_affectation(
                demande_id=4,
                payload=DemandeAffectationCreate(
                    id_chasseur=999,
                ),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Chasseur 999 not found"


def test_create_demande_affectation_returns_409_for_current_assignment() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_assignment.side_effect = (
        DemandeAffectationConflictError(
            "Demande 4 already has a current assignment"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande_affectation(
                demande_id=4,
                payload=DemandeAffectationCreate(
                    id_chasseur=4,
                ),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 409


def test_create_demande_affectation_returns_403_for_service_authorization() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_assignment.side_effect = (
        DemandeAffectationAuthorizationError(
            "Only an administrator can assign a demande"
        )
    )

    current_user = AuthenticatedUser(
        id_utilisateur=30,
        email="service@example.com",
        role="SERVICE",
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande_affectation(
                demande_id=4,
                payload=DemandeAffectationCreate(
                    id_chasseur=4,
                ),
                db=db,
                current_user=current_user,
            )

    assert exc.value.status_code == 403


def test_create_demande_affectation_returns_422_for_constraint_error() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_assignment.side_effect = (
        DemandeAffectationValidationError(
            "Assignment creation violates a database constraint"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande_affectation(
                demande_id=4,
                payload=DemandeAffectationCreate(
                    id_chasseur=4,
                ),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 422


def test_list_demande_affectations_admin_sees_full_history() -> None:
    db = MagicMock()
    service = MagicMock()

    first = build_affectation(
        id_affectation=20,
        id_chasseur=4,
        statut="REFUSEE",
        id_utilisateur_decision=10,
        motif_refus="Unavailable",
    )
    second = build_affectation(
        id_affectation=21,
        id_chasseur=5,
        statut="ACCEPTEE",
        id_utilisateur_decision=11,
    )

    service.list_by_demande.return_value = [
        first,
        second,
    ]

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        result = list_demande_affectations(
            demande_id=4,
            db=db,
            current_user=build_admin_user(),
        )

    assert result == [first, second]
    service.list_by_demande.assert_called_once_with(4)


def test_list_demande_affectations_chasseur_sees_only_own_records() -> None:
    db = MagicMock()
    service = MagicMock()

    own = build_affectation(
        id_affectation=20,
        id_chasseur=4,
        statut="REFUSEE",
        id_utilisateur_decision=10,
        motif_refus="Unavailable",
    )
    other = build_affectation(
        id_affectation=21,
        id_chasseur=5,
        statut="ACCEPTEE",
        id_utilisateur_decision=11,
    )

    service.list_by_demande.return_value = [
        own,
        other,
    ]

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        result = list_demande_affectations(
            demande_id=4,
            db=db,
            current_user=build_chasseur_user(4),
        )

    assert result == [own]


def test_list_demande_affectations_chasseur_cannot_see_other_history() -> None:
    db = MagicMock()
    service = MagicMock()

    service.list_by_demande.return_value = [
        build_affectation(
            id_chasseur=5,
            statut="ACCEPTEE",
            id_utilisateur_decision=11,
        )
    ]

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            list_demande_affectations(
                demande_id=4,
                db=db,
                current_user=build_chasseur_user(4),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Assignment history not found"


def test_list_demande_affectations_requires_hunter_identity() -> None:
    db = MagicMock()
    service = MagicMock()

    service.list_by_demande.return_value = [
        build_affectation()
    ]

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            list_demande_affectations(
                demande_id=4,
                db=db,
                current_user=build_chasseur_user(None),
            )

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Hunter identity is not available"
    )


def test_list_demande_affectations_returns_404_for_missing_demande() -> None:
    db = MagicMock()
    service = MagicMock()

    service.list_by_demande.side_effect = (
        DemandeAffectationNotFoundError(
            "Demande 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            list_demande_affectations(
                demande_id=999,
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404


def test_decide_demande_affectation_accept_success() -> None:
    db = MagicMock()
    service = MagicMock()

    affectation = build_affectation(
        statut="ACCEPTEE",
        id_utilisateur_decision=10,
    )
    service.decide_assignment.return_value = affectation

    payload = DemandeAffectationDecision(
        statut=DemandeAffectationStatut.ACCEPTEE,
    )
    current_user = build_chasseur_user(4)

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        result = decide_demande_affectation(
            demande_id=4,
            payload=payload,
            db=db,
            current_user=current_user,
        )

    assert result is affectation

    service.decide_assignment.assert_called_once_with(
        demande_id=4,
        payload=payload,
        current_user=current_user,
    )


def test_decide_demande_affectation_refuse_success() -> None:
    db = MagicMock()
    service = MagicMock()

    affectation = build_affectation(
        statut="REFUSEE",
        id_utilisateur_decision=10,
        motif_refus="Capacity unavailable",
    )
    service.decide_assignment.return_value = affectation

    payload = DemandeAffectationDecision(
        statut=DemandeAffectationStatut.REFUSEE,
        motif_refus="Capacity unavailable",
    )
    current_user = build_chasseur_user(4)

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        result = decide_demande_affectation(
            demande_id=4,
            payload=payload,
            db=db,
            current_user=current_user,
        )

    assert result.statut == "REFUSEE"
    assert result.motif_refus == "Capacity unavailable"


def test_decide_demande_affectation_returns_404_for_wrong_hunter() -> None:
    db = MagicMock()
    service = MagicMock()

    service.decide_assignment.side_effect = (
        DemandeAffectationNotFoundError(
            "Pending assignment not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            decide_demande_affectation(
                demande_id=4,
                payload=DemandeAffectationDecision(
                    statut=DemandeAffectationStatut.ACCEPTEE,
                ),
                db=db,
                current_user=build_chasseur_user(5),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Pending assignment not found"


def test_decide_demande_affectation_returns_403_without_hunter_identity() -> None:
    db = MagicMock()
    service = MagicMock()

    service.decide_assignment.side_effect = (
        DemandeAffectationAuthorizationError(
            "Hunter identity is not available"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            decide_demande_affectation(
                demande_id=4,
                payload=DemandeAffectationDecision(
                    statut=DemandeAffectationStatut.ACCEPTEE,
                ),
                db=db,
                current_user=build_chasseur_user(None),
            )

    assert exc.value.status_code == 403


def test_decide_demande_affectation_returns_422_for_constraint_error() -> None:
    db = MagicMock()
    service = MagicMock()

    service.decide_assignment.side_effect = (
        DemandeAffectationValidationError(
            "Assignment decision violates a database constraint"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            decide_demande_affectation(
                demande_id=4,
                payload=DemandeAffectationDecision(
                    statut=DemandeAffectationStatut.ACCEPTEE,
                ),
                db=db,
                current_user=build_chasseur_user(4),
            )

    assert exc.value.status_code == 422