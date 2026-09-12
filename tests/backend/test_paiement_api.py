from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.api.v1.endpoints import paiements
from src.api.core.dependencies import (
    get_current_user,
)
from src.api.db.session import get_db
from src.api.schemas.auth import (
    AuthenticatedUser,
)
from src.api.services.paiement import (
    PaiementNotFoundError,
    PaiementTransitionError,
    PaiementValidationError,
)


app = FastAPI()

app.include_router(
    paiements.router
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


def make_paiement(
    *,
    statut="RECU",
):
    return SimpleNamespace(
        id_paiement=100,
        date_acte_authentique=(
            date(2026, 9, 1)
        ),
        montant_achat="420000.00",
        montant_honoraires="13500.00",
        montant_chasseur="6231.60",
        date_reception_honoraires=(
            date(2026, 9, 5)
        ),
        date_paiement_chasseur=None,
        statut=statut,
        id_mandat=11,
        id_bareme=5,
        id_vente=50,
        id_chasseur_beneficiaire=10,
        id_parametres_honoraires=1,
        id_parametres_remuneration=1,
        date_calcul=None,
        droit_remuneration=True,
        motif_refus=None,
        semaines_mandat_acte=20,
        nb_visites_calcul=3,
        annees_anciennete_calcul=3,
        nb_ventes_fenetre=2,
        nb_mandats_fenetre=4,
        note_delai="80.0",
        note_exclusivite="100.0",
        note_ventes="40.0",
        note_mandats="40.0",
        note_visites="100.0",
        score_performance="73.5",
        taux_base="0.4000",
        majoration_anciennete="0.0600",
        modulation_performance="0.0940",
        taux_final="0.4616",
    )


def setup_function():
    app.dependency_overrides.clear()

    app.dependency_overrides[
        get_db
    ] = override_db


def teardown_function():
    app.dependency_overrides.clear()


def test_admin_can_transition_payment(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    paiement = make_paiement(
        statut="RECU"
    )

    transition = MagicMock(
        return_value=paiement
    )

    monkeypatch.setattr(
        paiements.PaiementService,
        "transition",
        transition,
    )

    response = client.patch(
        "/paiements/100/statut",
        json={
            "statut": "RECU",
            "date_reception_honoraires": (
                "2026-09-05"
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["id_paiement"]
        == 100
    )

    assert (
        body["statut"]
        == "RECU"
    )

    transition.assert_called_once()

    kwargs = (
        transition.call_args.kwargs
    )

    assert (
        kwargs["statut_cible"]
        == "RECU"
    )

    assert (
        kwargs["utilisateur"]
        == "admin@example.com"
    )


def test_chasseur_cannot_transition_payment():
    app.dependency_overrides[
        get_current_user
    ] = chasseur_user

    response = client.patch(
        "/paiements/100/statut",
        json={
            "statut": "RECU",
            "date_reception_honoraires": (
                "2026-09-05"
            ),
        },
    )

    assert response.status_code == 403


def test_unauthenticated_request_is_rejected():
    response = client.patch(
        "/paiements/100/statut",
        json={
            "statut": "RECU",
            "date_reception_honoraires": (
                "2026-09-05"
            ),
        },
    )

    assert response.status_code == 401


def test_not_found_returns_404(
    monkeypatch,
):
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    def raise_not_found(
        *args,
        **kwargs,
    ):
        raise PaiementNotFoundError(
            "Paiement 999 not found"
        )

    monkeypatch.setattr(
        paiements.PaiementService,
        "transition",
        raise_not_found,
    )

    response = client.patch(
        "/paiements/999/statut",
        json={
            "statut": "RECU",
            "date_reception_honoraires": (
                "2026-09-05"
            ),
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Paiement 999 not found"
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
        raise PaiementTransitionError(
            (
                "Invalid payment transition: "
                "ATTENDU -> PAYE"
            )
        )

    monkeypatch.setattr(
        paiements.PaiementService,
        "transition",
        raise_transition,
    )

    response = client.patch(
        "/paiements/100/statut",
        json={
            "statut": "PAYE",
            "date_paiement_chasseur": (
                "2026-09-10"
            ),
        },
    )

    assert response.status_code == 409


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
        raise PaiementValidationError(
            (
                "date_reception_honoraires "
                "is required"
            )
        )

    monkeypatch.setattr(
        paiements.PaiementService,
        "transition",
        raise_validation,
    )

    response = client.patch(
        "/paiements/100/statut",
        json={
            "statut": "RECU",
        },
    )

    assert response.status_code == 422


def test_invalid_status_is_rejected_by_schema():
    app.dependency_overrides[
        get_current_user
    ] = admin_user

    response = client.patch(
        "/paiements/100/statut",
        json={
            "statut": "INVALID",
        },
    )

    assert response.status_code == 422