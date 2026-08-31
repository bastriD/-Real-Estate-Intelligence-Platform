from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.db.models.client import Client
from src.api.schemas.client import ClientCreate, ClientUpdate
from src.api.services.client import (
    ClientAlreadyExistsError,
    ClientNotFoundError,
    ClientService,
)


def build_client() -> Client:
    return Client(
        id_client=1,
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        telephone="0600000000",
        ville="Montpellier",
        statut="ACTIF",
        consentement_contact=True,
    )


def build_create_payload() -> ClientCreate:
    return ClientCreate(
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        telephone="0600000000",
        ville="Montpellier",
        statut="ACTIF",
        consentement_contact=True,
    )


def test_list_clients_returns_all() -> None:
    db = MagicMock()

    service = ClientService(db)
    service.repository.list_all = MagicMock(
        return_value=[build_client()]
    )

    result = service.list_clients()

    assert len(result) == 1
    assert result[0].id_client == 1

    service.repository.list_all.assert_called_once()


def test_get_client_returns_existing_client() -> None:
    db = MagicMock()
    client = build_client()

    service = ClientService(db)
    service.repository.get_by_id = MagicMock(
        return_value=client
    )

    result = service.get_client(1)

    assert result is client

    service.repository.get_by_id.assert_called_once_with(
        1
    )


def test_get_client_raises_when_missing() -> None:
    db = MagicMock()

    service = ClientService(db)
    service.repository.get_by_id = MagicMock(
        return_value=None
    )

    with pytest.raises(ClientNotFoundError):
        service.get_client(999)


def test_create_client_rejects_duplicate_email() -> None:
    db = MagicMock()

    service = ClientService(db)
    service.repository.get_by_email = MagicMock(
        return_value=build_client()
    )
    service.repository.create = MagicMock()

    payload = build_create_payload()

    with pytest.raises(
        ClientAlreadyExistsError
    ):
        service.create_client(payload)

    service.repository.create.assert_not_called()
    db.commit.assert_not_called()


def test_create_client_success() -> None:
    db = MagicMock()

    service = ClientService(db)

    service.repository.get_by_email = MagicMock(
        return_value=None
    )

    created = build_client()

    service.repository.create = MagicMock(
        return_value=created
    )

    payload = build_create_payload()

    result = service.create_client(payload)

    assert result is created
    assert result.email == "jean.dupont@example.com"
    assert result.statut == "ACTIF"

    service.repository.get_by_email.assert_called_once_with(
        "jean.dupont@example.com"
    )
    service.repository.create.assert_called_once()
    db.commit.assert_called_once()


def test_create_client_rolls_back_on_integrity_error() -> None:
    db = MagicMock()

    service = ClientService(db)

    service.repository.get_by_email = MagicMock(
        return_value=None
    )

    service.repository.create = MagicMock(
        side_effect=IntegrityError(
            "statement",
            {},
            Exception("database constraint"),
        )
    )

    payload = build_create_payload()

    with pytest.raises(
        ClientAlreadyExistsError
    ):
        service.create_client(payload)

    db.rollback.assert_called_once()


def test_update_client_success() -> None:
    db = MagicMock()
    client = build_client()

    service = ClientService(db)
    service.repository.get_by_id = MagicMock(
        return_value=client
    )

    payload = ClientUpdate(
        ville="Nimes",
        statut="INACTIF",
    )

    result = service.update_client(
        client_id=1,
        payload=payload,
    )

    assert result is client
    assert result.ville == "Nimes"
    assert result.statut == "INACTIF"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(client)


def test_update_client_changes_email() -> None:
    db = MagicMock()
    client = build_client()

    service = ClientService(db)
    service.repository.get_by_id = MagicMock(
        return_value=client
    )
    service.repository.get_by_email = MagicMock(
        return_value=None
    )

    payload = ClientUpdate(
        email="nouveau@example.com"
    )

    result = service.update_client(
        client_id=1,
        payload=payload,
    )

    assert result.email == "nouveau@example.com"

    service.repository.get_by_email.assert_called_once_with(
        "nouveau@example.com"
    )
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(client)


def test_update_client_allows_same_email_for_same_client() -> None:
    db = MagicMock()
    client = build_client()

    service = ClientService(db)
    service.repository.get_by_id = MagicMock(
        return_value=client
    )
    service.repository.get_by_email = MagicMock(
        return_value=client
    )

    payload = ClientUpdate(
        email="jean.dupont@example.com"
    )

    result = service.update_client(
        client_id=1,
        payload=payload,
    )

    assert result is client
    assert result.email == "jean.dupont@example.com"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(client)


def test_update_client_rejects_email_used_by_other_client() -> None:
    db = MagicMock()
    client = build_client()

    other_client = build_client()
    other_client.id_client = 2
    other_client.email = "other@example.com"

    service = ClientService(db)
    service.repository.get_by_id = MagicMock(
        return_value=client
    )
    service.repository.get_by_email = MagicMock(
        return_value=other_client
    )

    payload = ClientUpdate(
        email="other@example.com"
    )

    with pytest.raises(
        ClientAlreadyExistsError
    ):
        service.update_client(
            client_id=1,
            payload=payload,
        )

    db.commit.assert_not_called()


def test_update_client_rolls_back_on_integrity_error() -> None:
    db = MagicMock()
    client = build_client()

    service = ClientService(db)
    service.repository.get_by_id = MagicMock(
        return_value=client
    )

    db.commit.side_effect = IntegrityError(
        "statement",
        {},
        Exception("database constraint"),
    )

    payload = ClientUpdate(
        ville="Nimes"
    )

    with pytest.raises(
        ClientAlreadyExistsError
    ):
        service.update_client(
            client_id=1,
            payload=payload,
        )

    db.rollback.assert_called_once()


def test_delete_client_success() -> None:
    db = MagicMock()
    client = build_client()

    service = ClientService(db)
    service.repository.get_by_id = MagicMock(
        return_value=client
    )
    service.repository.delete = MagicMock()

    service.delete_client(1)

    service.repository.delete.assert_called_once_with(
        client
    )
    db.commit.assert_called_once()