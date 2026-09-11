from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.api.v1.endpoints.visites import get_service
from src.api.core.dependencies import get_current_user
from src.api.main import app
from src.api.schemas.auth import AuthenticatedUser


@pytest.fixture
def visite_api():
    service = MagicMock()

    visite = SimpleNamespace(
        id_visite=42,
        id_presentation=19,
        date_visite=datetime(
            2026,
            9,
            9,
            14,
            tzinfo=timezone.utc,
        ),
        date_creation=datetime(
            2026,
            9,
            9,
            tzinfo=timezone.utc,
        ),
        statut="PLANIFIEE",
        compte_rendu=None,
        note=None,
        photos=[],
    )

    service.create_visite.return_value = visite
    service.update_visite.return_value = visite

    # Ownership path used by CHASSEUR endpoints.
    service.get_demande_id_for_presentation.return_value = 4
    service.get_demande_id_for_visite.return_value = 4

    # The endpoint creates DemandeAffectationService from
    # service.session.
    service.session = MagicMock()

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = True

    old_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[get_service] = lambda: service

    with patch(
        "src.api.api.v1.endpoints.visites."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        with TestClient(app) as client:
            try:
                yield client, service
            finally:
                app.dependency_overrides.clear()
                app.dependency_overrides.update(
                    old_overrides
                )


def set_user(role):
    app.dependency_overrides[
        get_current_user
    ] = lambda: AuthenticatedUser(
        id_utilisateur=7,
        email="actor@example.com",
        role=role,
        id_client=None,
        id_chasseur=(
            1
            if role == "CHASSEUR"
            else None
        ),
    )


def request_mutation(client, method):
    if method == "post":
        return client.post(
            "/api/v1/visites",
            json={
                "id_presentation": 19,
                "date_visite": (
                    "2026-09-09T14:00:00Z"
                ),
            },
        )

    if method == "patch":
        return client.patch(
            "/api/v1/visites/42",
            json={
                "note": 4,
            },
        )

    return client.delete(
        "/api/v1/visites/42"
    )


@pytest.mark.parametrize(
    "role",
    [
        "ADMIN",
        "CHASSEUR",
    ],
)
@pytest.mark.parametrize(
    "method,action,code",
    [
        (
            "post",
            "create_visite",
            201,
        ),
        (
            "patch",
            "update_visite",
            200,
        ),
        (
            "delete",
            "delete_visite",
            204,
        ),
    ],
)
def test_actor_propagated_from_authenticated_user(
    visite_api,
    role,
    method,
    action,
    code,
):
    client, service = visite_api

    set_user(role)

    response = request_mutation(
        client,
        method,
    )

    assert response.status_code == code

    handler = getattr(
        service,
        action,
    )

    handler.assert_called_once()

    assert (
        handler.call_args.kwargs[
            "utilisateur"
        ]
        == "actor@example.com"
    )


@pytest.mark.parametrize(
    "role",
    [
        "CLIENT",
        "SERVICE",
    ],
)
@pytest.mark.parametrize(
    "method",
    [
        "post",
        "patch",
        "delete",
    ],
)
def test_existing_role_restrictions_preserved(
    visite_api,
    role,
    method,
):
    client, service = visite_api

    set_user(role)

    response = request_mutation(
        client,
        method,
    )

    assert response.status_code == 403
    assert not service.mock_calls