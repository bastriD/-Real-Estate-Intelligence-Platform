from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.api.db.models.visite import Visite
from src.api.schemas.visite import VisiteCreate, VisiteUpdate
from src.api.services.visite import (
    PresentationNotFoundForVisiteError,
    VisiteNotFoundError,
    VisiteService,
)


def build_visite() -> Visite:
    return Visite(
        id_visite=1,
        date_visite=datetime(
            2026,
            9,
            2,
            14,
            30,
            tzinfo=timezone.utc,
        ),
        statut="PLANIFIEE",
        compte_rendu=None,
        note=None,
        photos=[],
        id_presentation=19,
    )


def test_get_visite_returns_existing_visite() -> None:
    db = MagicMock()

    visite = build_visite()

    service = VisiteService(db)
    service.repository.get_by_id = MagicMock(
        return_value=visite
    )

    result = service.get_visite(1)

    assert result is visite

    service.repository.get_by_id.assert_called_once_with(
        1
    )


def test_get_visite_raises_when_missing() -> None:
    db = MagicMock()

    service = VisiteService(db)
    service.repository.get_by_id = MagicMock(
        return_value=None
    )

    with pytest.raises(VisiteNotFoundError):
        service.get_visite(999)

    service.repository.get_by_id.assert_called_once_with(
        999
    )


def test_create_visite_rejects_missing_presentation() -> None:
    db = MagicMock()
    db.scalar.return_value = None

    service = VisiteService(db)

    payload = VisiteCreate(
        date_visite=datetime(
            2026,
            9,
            2,
            14,
            30,
            tzinfo=timezone.utc,
        ),
        id_presentation=999,
        statut="PLANIFIEE",
        photos=[],
    )

    with pytest.raises(
        PresentationNotFoundForVisiteError
    ):
        service.create_visite(payload)

    db.scalar.assert_called_once()


def test_create_visite_success() -> None:
    db = MagicMock()
    db.scalar.return_value = 19

    service = VisiteService(db)

    payload = VisiteCreate(
        date_visite=datetime(
            2026,
            9,
            2,
            14,
            30,
            tzinfo=timezone.utc,
        ),
        id_presentation=19,
        statut="PLANIFIEE",
        photos=[],
    )

    created = build_visite()

    service.repository.create = MagicMock(
        return_value=created
    )

    result = service.create_visite(payload)

    assert result is created
    assert result.id_presentation == 19
    assert result.statut == "PLANIFIEE"

    db.scalar.assert_called_once()
    service.repository.create.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created)


def test_update_visite_success() -> None:
    db = MagicMock()

    visite = build_visite()

    service = VisiteService(db)
    service.repository.get_by_id = MagicMock(
        return_value=visite
    )

    payload = VisiteUpdate(
        statut="REALISEE",
        compte_rendu=(
            "Visite runtime validation completed "
            "successfully"
        ),
        note=4,
    )

    result = service.update_visite(
        visite_id=1,
        payload=payload,
    )

    assert result is visite
    assert result.statut == "REALISEE"
    assert (
        result.compte_rendu
        == "Visite runtime validation completed "
        "successfully"
    )
    assert result.note == 4

    service.repository.get_by_id.assert_called_once_with(
        1
    )
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(visite)


def test_delete_visite_success() -> None:
    db = MagicMock()

    visite = build_visite()

    service = VisiteService(db)
    service.repository.get_by_id = MagicMock(
        return_value=visite
    )
    service.repository.delete = MagicMock()

    service.delete_visite(1)

    service.repository.get_by_id.assert_called_once_with(
        1
    )
    service.repository.delete.assert_called_once_with(
        visite
    )
    db.commit.assert_called_once()