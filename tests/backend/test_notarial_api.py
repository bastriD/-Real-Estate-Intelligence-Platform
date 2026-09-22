from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.api.v1.endpoints import notaires
from src.api.core.dependencies import get_current_user
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.services.notaire import NotarialConflictError, NotarialNotFoundError, NotarialValidationError


@pytest.fixture
def api(monkeypatch):
    app = FastAPI()
    app.include_router(notaires.router)
    app.dependency_overrides[get_db] = lambda: MagicMock()
    service = MagicMock()
    service.create_notaire.return_value = SimpleNamespace(id_notaire=1, nom="Notary", office="Office", email="notary@example.com")
    service.repository.notaires.return_value = [service.create_notaire.return_value]
    service.create_dossier.return_value = SimpleNamespace(id_dossier_notarial=2, id_notaire=1, id_offre=3,
        id_vente=None, date_rendez_vous=datetime(2025, 1, 1, tzinfo=timezone.utc),
        reference_acte=None, reference_document=None, date_creation=datetime.now(timezone.utc))
    service.get_dossier.return_value = service.create_dossier.return_value
    service.sign.return_value = service.create_dossier.return_value
    service.repository.movements.return_value = []
    monkeypatch.setattr(notaires, "NotaireService", lambda db: service)
    return app, TestClient(app), service


def login(app, role):
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id_utilisateur=1, email="actor@example.com", role=role,
        id_client=1 if role == "CLIENT" else None, id_chasseur=1 if role == "CHASSEUR" else None,
    )


@pytest.mark.parametrize("role", ["CLIENT", "CHASSEUR"])
@pytest.mark.parametrize("method,path", [("get", "/notaires"), ("post", "/notaires"),
    ("post", "/notaires/dossiers"), ("get", "/notaires/dossiers/1"),
    ("post", "/notaires/dossiers/1/signature"), ("get", "/notaires/dossiers/1/mouvements"),
    ("post", "/notaires/dossiers/1/mouvements")])
def test_non_admin_cannot_read_or_write_notarial_finances(api, role, method, path):
    app, client, service = api
    login(app, role)
    assert getattr(client, method)(path).status_code == 403
    service.create_notaire.assert_not_called()
    service.record_movement.assert_not_called()


def test_admin_creation_and_read_paths(api):
    app, client, service = api
    login(app, "ADMIN")
    assert client.post("/notaires", json={"nom":"Notary", "office":"Office", "email":"notary@example.com"}).status_code == 201
    assert service.create_notaire.call_args.kwargs == {"utilisateur": "actor@example.com"}
    assert client.get("/notaires").status_code == 200
    assert client.post("/notaires/dossiers", json={"id_notaire":1, "id_offre":3, "date_rendez_vous":"2025-01-01T10:00:00Z"}).status_code == 201
    assert client.get("/notaires/dossiers/2").status_code == 200
    assert client.get("/notaires/dossiers/2/mouvements").json() == []
    assert client.post("/notaires/dossiers/2/signature", json={"date_acte_authentique":"2025-01-02",
        "montant_achat":"200000", "reference_acte":"ACT-1", "reference_document":"archive/act-1"}).status_code == 200
    assert service.sign.call_args.kwargs == {"utilisateur": "actor@example.com"}


@pytest.mark.parametrize("error,code", [(NotarialNotFoundError,404), (NotarialConflictError,409), (NotarialValidationError,422)])
def test_financial_errors_are_exposed_as_controlled_responses(api, error, code):
    app, client, service = api
    login(app, "ADMIN")
    service.record_movement.side_effect = error("Rejected")
    response = client.post("/notaires/dossiers/2/mouvements", json={
        "nature":"COLLECTE_NOTAIRE", "montant":"1000", "date_operation":"2025-01-03", "reference":"receipt-1"})
    assert response.status_code == code


@pytest.mark.parametrize("change", [{"montant":"-1"}, {"montant":"NaN"}, {"montant":"0.001"},
    {"nature":"PAYE"}, {"reference":"   "}, {"id_utilisateur":999}])
def test_invalid_financial_payloads_do_not_reach_service(api, change):
    app, client, service = api
    login(app, "ADMIN")
    payload = {"nature":"COLLECTE_NOTAIRE", "montant":"1000", "date_operation":"2025-01-03", "reference":"receipt-1"}
    assert client.post("/notaires/dossiers/2/mouvements", json=payload | change).status_code == 422
    service.record_movement.assert_not_called()
