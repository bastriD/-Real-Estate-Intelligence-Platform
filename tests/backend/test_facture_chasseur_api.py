from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.api.v1.endpoints import factures_chasseurs as endpoints
from src.api.core.dependencies import get_current_user
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.services.facture_chasseur import (
    FactureChasseurNotFoundError, FactureChasseurConflictError, FactureChasseurValidationError,
)
from tests.backend.test_facture_chasseur_service import invoice


URL = "/api/v1/factures-chasseurs"
BODY = {"id_paiement": 10, "numero_facture": "H-1", "date_facture": "2026-01-05", "montant": "3939.60"}


@pytest.fixture
def api(monkeypatch):
    app = FastAPI()
    app.include_router(endpoints.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: MagicMock()
    service = MagicMock()
    service.submit.return_value = service.get_facture.return_value = service.decide.return_value = invoice()
    service.list_factures.return_value = [invoice()]
    monkeypatch.setattr(endpoints, "FactureChasseurService", lambda db: service)
    with TestClient(app) as client:
        yield app, client, service


def login(app, role, identity=3):
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id_utilisateur=7, email="actor@example.com", role=role,
        id_chasseur=identity if role == "CHASSEUR" else None,
        id_client=identity if role == "CLIENT" else None,
    )


@pytest.mark.parametrize("role", ["ADMIN", "CHASSEUR", "CLIENT", "SERVICE"])
def test_role_matrix(api, role):
    app, client, service = api
    login(app, role)
    assert client.get(URL).status_code == (200 if role in {"ADMIN", "CHASSEUR"} else 403)
    assert client.get(URL + "/1").status_code == (200 if role in {"ADMIN", "CHASSEUR"} else 403)
    assert client.post(URL, json=BODY).status_code == (201 if role == "CHASSEUR" else 403)
    assert client.post(URL + "/1/decision", json={"statut": "CONFORME"}).status_code == (200 if role == "ADMIN" else 403)
    assert service.submit.call_count == (1 if role == "CHASSEUR" else 0)
    assert service.decide.call_count == (1 if role == "ADMIN" else 0)


def test_actor_and_ownership_come_only_from_authentication(api):
    app, client, service = api
    login(app, "CHASSEUR")
    assert client.get(URL + "?chasseur_id=999").status_code == 200
    service.list_factures.assert_called_once_with(3)
    assert client.get(URL + "/1?id_chasseur=999").status_code == 200
    service.get_facture.assert_called_once_with(1, 3)
    assert client.post(URL, json=BODY).status_code == 201
    assert service.submit.call_args.kwargs == {
        "chasseur_id": 3, "utilisateur": "actor@example.com", "id_utilisateur": 7,
    }
    login(app, "ADMIN")
    assert client.post(URL + "/1/decision", json={"statut": "CONFORME"}).status_code == 200
    assert service.decide.call_args.kwargs == {"utilisateur": "actor@example.com", "id_utilisateur": 7}


def test_missing_hunter_identity_fails_closed(api):
    app, client, service = api
    login(app, "CHASSEUR", None)
    assert client.get(URL).status_code == client.get(URL + "/1").status_code == 403
    assert client.post(URL, json=BODY).status_code == 403
    service.submit.assert_not_called()


def test_authentication_required(api):
    _, client, service = api
    assert client.get(URL).status_code == 401
    assert client.post(URL, json=BODY).status_code == 401
    assert client.post(URL + "/1/decision", json={"statut": "CONFORME"}).status_code == 401
    service.submit.assert_not_called()
    service.decide.assert_not_called()


@pytest.mark.parametrize("error,code", [(FactureChasseurNotFoundError, 404),
    (FactureChasseurConflictError, 409), (FactureChasseurValidationError, 422)])
def test_domain_errors(api, error, code):
    app, client, service = api
    login(app, "CHASSEUR")
    service.submit.side_effect = error("rejected")
    assert client.post(URL, json=BODY).status_code == code
    login(app, "ADMIN")
    service.decide.side_effect = error("rejected")
    assert client.post(URL + "/1/decision", json={"statut": "CONFORME"}).status_code == code


def test_cross_owner_and_absent_reads_are_indistinguishable(api):
    app, client, service = api
    login(app, "CHASSEUR")
    service.get_facture.side_effect = FactureChasseurNotFoundError("Resource not found")
    responses = [client.get(URL + path) for path in ["/2", "/999"]]
    assert all(response.status_code == 404 for response in responses)
    assert responses[0].json() == responses[1].json() == {"detail": "Resource not found"}


@pytest.mark.parametrize("field", ["id_chasseur", "id_verificateur", "numero_version", "statut", "date_verification"])
def test_forged_submission_authority_rejected(api, field):
    app, client, service = api
    login(app, "CHASSEUR")
    assert client.post(URL, json=BODY | {field: "1"}).status_code == 422
    service.submit.assert_not_called()


@pytest.mark.parametrize("override", [{"numero_facture": "  "}, {"montant": "0"},
    {"montant": "1.001"}, {"id_paiement": -1}, {"numero_facture": "X" * 81}])
def test_invalid_submission_rejected(api, override):
    app, client, service = api
    login(app, "CHASSEUR")
    assert client.post(URL, json=BODY | override).status_code == 422
    service.submit.assert_not_called()


@pytest.mark.parametrize("body", [{"statut": "REJETEE"}, {"statut": "REJETEE", "motif_rejet": " "},
    {"statut": "CONFORME", "motif_rejet": "Not allowed"}, {"statut": "SOUMISE"},
    {"statut": "CONFORME", "id_verificateur": 99}])
def test_invalid_decision_rejected(api, body):
    app, client, service = api
    login(app, "ADMIN")
    assert client.post(URL + "/1/decision", json=body).status_code == 422
    service.decide.assert_not_called()


def test_router_exposes_no_generic_mutations():
    from src.api.main import app
    paths = app.openapi()["paths"]
    assert set(paths[URL]) == {"get", "post"}
    assert set(paths[URL + "/{invoice_id}"]) == {"get"}
    assert set(paths[URL + "/{invoice_id}/decision"]) == {"post"}
