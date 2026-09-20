from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.api.v1.endpoints import offres
from src.api.core.dependencies import get_current_user
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.services.offre import (
    OffreNotFoundError,
    OffreTransitionError,
    OffreValidationError,
    PresentationNotFoundForOffreError,
)


app = FastAPI()

app.include_router(
    offres.router
)


def override_db():
    yield MagicMock()


client = TestClient(
    app
)


def admin_user():
    return AuthenticatedUser(
        id_utilisateur=1,
        email="admin@example.com",
        role="ADMIN",
        id_client=None,
        id_chasseur=None,
    )


def chasseur_user():
    return AuthenticatedUser(
        id_utilisateur=2,
        email="hunter@example.com",
        role="CHASSEUR",
        id_client=None,
        id_chasseur=10,
    )


def make_offre(
    *,
    statut="SOUMISE",
    numero_version=1,
):
    return SimpleNamespace(
        id_offre=100,
        id_presentation=19,
        numero_version=numero_version,
        montant=Decimal("250000.00"),
        date_offre=datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        date_expiration=None,
        date_decision=None,
        statut=statut,
        commentaire=None,
        date_creation=datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )


def setup_function():
    app.dependency_overrides.clear()

    app.dependency_overrides[
        get_db
    ] = override_db


def teardown_function():
    app.dependency_overrides.clear()


def test_admin_can_create_offre(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    offre = make_offre()

    create = MagicMock(
        return_value=offre
    )

    monkeypatch.setattr(
        offres.OffreService,
        "create_offre",
        create,
    )

    response = client.post(
        "/offres",
        json={
            "id_presentation": 19,
            "montant": "250000.00",
            "commentaire": "Initial offer",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id_offre"] == 100
    assert body["id_presentation"] == 19
    assert body["numero_version"] == 1
    assert body["statut"] == "SOUMISE"

    create.assert_called_once()

    kwargs = create.call_args.kwargs

    assert (
        kwargs["utilisateur"]
        == "admin@example.com"
    )


def test_chasseur_can_create_offre(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = chasseur_user

    monkeypatch.setattr(
        offres.OffreService,
        "get_demande_id_for_presentation",
        MagicMock(return_value=4),
    )

    monkeypatch.setattr(
        offres.DemandeAffectationService,
        "hunter_can_access_demande",
        MagicMock(return_value=True),
    )

    create = MagicMock(
        return_value=make_offre()
    )

    monkeypatch.setattr(
        offres.OffreService,
        "create_offre",
        create,
    )

    response = client.post(
        "/offres",
        json={
            "id_presentation": 19,
            "montant": "250000.00",
        },
    )

    assert response.status_code == 201

    create.assert_called_once()


def test_unauthenticated_create_is_rejected():
    response = client.post(
        "/offres",
        json={
            "id_presentation": 19,
            "montant": "250000.00",
        },
    )

    assert response.status_code == 401


def test_presentation_not_found_returns_404(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    def raise_not_found(
        *args,
        **kwargs,
    ):
        raise PresentationNotFoundForOffreError(
            "Presentation 999 not found"
        )

    monkeypatch.setattr(
        offres.OffreService,
        "create_offre",
        raise_not_found,
    )

    response = client.post(
        "/offres",
        json={
            "id_presentation": 999,
            "montant": "250000.00",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Presentation not found"
    )


def test_offre_not_found_returns_404(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    def raise_not_found(
        *args,
        **kwargs,
    ):
        raise OffreNotFoundError(
            "Offre 999 not found"
        )

    monkeypatch.setattr(
        offres.OffreService,
        "decide_offre",
        raise_not_found,
    )

    response = client.post(
        "/offres/999/decision",
        json={
            "statut": "REFUSEE",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Offre not found"
    )


def test_invalid_transition_returns_409(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    def raise_transition(
        *args,
        **kwargs,
    ):
        raise OffreTransitionError(
            (
                "Invalid offer transition: "
                "ACCEPTEE -> REFUSEE"
            )
        )

    monkeypatch.setattr(
        offres.OffreService,
        "decide_offre",
        raise_transition,
    )

    response = client.post(
        "/offres/100/decision",
        json={
            "statut": "REFUSEE",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Invalid offer transition: "
        "ACCEPTEE -> REFUSEE"
    )


def test_validation_error_returns_422(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    def raise_validation(
        *args,
        **kwargs,
    ):
        raise OffreValidationError(
            "Offer history already exists"
        )

    monkeypatch.setattr(
        offres.OffreService,
        "create_offre",
        raise_validation,
    )

    response = client.post(
        "/offres",
        json={
            "id_presentation": 19,
            "montant": "250000.00",
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "Offer history already exists"
    )


def test_invalid_decision_status_is_rejected_by_schema():
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    response = client.post(
        "/offres/100/decision",
        json={
            "statut": "EXPIREE",
        },
    )

    assert response.status_code == 422


def test_invalid_amount_is_rejected_by_schema():
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    response = client.post(
        "/offres",
        json={
            "id_presentation": 19,
            "montant": "0.00",
        },
    )

    assert response.status_code == 422


def test_admin_can_decide_offre(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    offre = make_offre(
        statut="ACCEPTEE"
    )

    offre.date_decision = datetime(
        2026,
        9,
        20,
        13,
        0,
        tzinfo=timezone.utc,
    )

    decide = MagicMock(
        return_value=offre
    )

    monkeypatch.setattr(
        offres.OffreService,
        "decide_offre",
        decide,
    )

    response = client.post(
        "/offres/100/decision",
        json={
            "statut": "ACCEPTEE",
            "commentaire": "Accepted",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id_offre"] == 100
    assert body["statut"] == "ACCEPTEE"

    decide.assert_called_once()

    kwargs = decide.call_args.kwargs

    assert (
        kwargs["utilisateur"]
        == "admin@example.com"
    )


def test_admin_can_revise_offre(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    revised = make_offre(
        numero_version=2
    )

    revised.id_offre = 101

    revised.montant = Decimal(
        "245000.00"
    )

    revise = MagicMock(
        return_value=revised
    )

    monkeypatch.setattr(
        offres.OffreService,
        "revise_offre",
        revise,
    )

    response = client.post(
        "/offres/100/revisions",
        json={
            "montant": "245000.00",
            "commentaire": "Revised offer",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id_offre"] == 101
    assert body["numero_version"] == 2
    assert body["montant"] == "245000.00"
    assert body["statut"] == "SOUMISE"

    revise.assert_called_once()

    kwargs = revise.call_args.kwargs

    assert (
        kwargs["utilisateur"]
        == "admin@example.com"
    )


def test_invalid_revision_amount_is_rejected_by_schema():
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    response = client.post(
        "/offres/100/revisions",
        json={
            "montant": "-1.00",
        },
    )

    assert response.status_code == 422