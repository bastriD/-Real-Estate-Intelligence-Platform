from datetime import date
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from src.api.db.models.mandat import Mandat
from src.api.schemas.mandat import MandatCreate, MandatUpdate
from src.api.services.mandat import (
    ChasseurNotFoundForMandatError,
    ClientNotFoundForMandatError,
    MandatAlreadyExistsError,
    MandatNotFoundError,
    MandatService,
)


def build_mandat() -> Mandat:
    return Mandat(
        id_mandat=36,
        reference_mandat="API-TEST-MANDAT",
        type_mandat="EXCLUSIF",
        date_signature=date(2026, 8, 30),
        mode_signature="ELECTRONIQUE",
        date_debut=date(2026, 8, 30),
        date_fin=date(2026, 12, 31),
        statut="ACTIF",
        commentaire=None,
        id_client=1,
        id_chasseur=1,
    )


def test_get_mandat_returns_existing_mandat() -> None:
    db = MagicMock()
    mandat = build_mandat()

    service = MandatService(db)
    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    result = service.get_mandat(36)

    assert result is mandat

    service.repository.get_by_id.assert_called_once_with(
        36
    )


def test_get_mandat_raises_when_missing() -> None:
    db = MagicMock()

    service = MandatService(db)
    service.repository.get_by_id = MagicMock(
        return_value=None
    )

    with pytest.raises(MandatNotFoundError):
        service.get_mandat(999)


def test_list_by_client_validates_client() -> None:
    db = MagicMock()
    db.scalar.return_value = 1

    service = MandatService(db)
    service.repository.list_by_client = MagicMock(
        return_value=[build_mandat()]
    )

    result = service.list_by_client(1)

    assert len(result) == 1
    assert result[0].id_client == 1

    db.scalar.assert_called_once()

    service.repository.list_by_client.assert_called_once_with(
        1
    )


def test_list_by_client_rejects_missing_client() -> None:
    db = MagicMock()
    db.scalar.return_value = None

    service = MandatService(db)

    with pytest.raises(
        ClientNotFoundForMandatError
    ):
        service.list_by_client(999)


def test_list_by_chasseur_validates_chasseur() -> None:
    db = MagicMock()
    db.scalar.return_value = 1

    service = MandatService(db)
    service.repository.list_by_chasseur = MagicMock(
        return_value=[build_mandat()]
    )

    result = service.list_by_chasseur(1)

    assert len(result) == 1
    assert result[0].id_chasseur == 1

    db.scalar.assert_called_once()

    service.repository.list_by_chasseur.assert_called_once_with(
        1
    )


def test_list_by_chasseur_rejects_missing_chasseur() -> None:
    db = MagicMock()
    db.scalar.return_value = None

    service = MandatService(db)

    with pytest.raises(
        ChasseurNotFoundForMandatError
    ):
        service.list_by_chasseur(999)


def test_create_mandat_rejects_duplicate_reference() -> None:
    db = MagicMock()

    service = MandatService(db)
    service.repository.get_by_reference = MagicMock(
        return_value=build_mandat()
    )

    payload = MandatCreate(
        reference_mandat="API-TEST-MANDAT",
        type_mandat="EXCLUSIF",
        date_signature=date(2026, 8, 30),
        mode_signature="ELECTRONIQUE",
        date_debut=date(2026, 8, 30),
        date_fin=date(2026, 12, 31),
        statut="ACTIF",
        id_client=1,
        id_chasseur=1,
    )

    with pytest.raises(
        MandatAlreadyExistsError
    ):
        service.create_mandat(payload)


def test_create_mandat_success() -> None:
    db = MagicMock()

    service = MandatService(db)

    service.repository.get_by_reference = MagicMock(
        return_value=None
    )

    # Client existence check, then chasseur existence check.
    db.scalar.side_effect = [1, 1]

    created = build_mandat()

    service.repository.create = MagicMock(
        return_value=created
    )

    payload = MandatCreate(
        reference_mandat="API-TEST-MANDAT",
        type_mandat="EXCLUSIF",
        date_signature=date(2026, 8, 30),
        mode_signature="ELECTRONIQUE",
        date_debut=date(2026, 8, 30),
        date_fin=date(2026, 12, 31),
        statut="ACTIF",
        id_client=1,
        id_chasseur=1,
    )

    result = service.create_mandat(payload)

    assert result is created
    assert result.reference_mandat == (
        "API-TEST-MANDAT"
    )

    assert db.scalar.call_count == 2
    service.repository.create.assert_called_once()
    db.commit.assert_called_once()


def test_create_mandat_rejects_invalid_dates() -> None:
    with pytest.raises(
        ValidationError,
        match=(
            "date_fin must be greater than or equal "
            "to date_debut"
        ),
    ):
        MandatCreate(
            reference_mandat="INVALID-DATES",
            type_mandat="EXCLUSIF",
            date_signature=date(2026, 8, 30),
            mode_signature="ELECTRONIQUE",
            date_debut=date(2026, 12, 31),
            date_fin=date(2026, 8, 30),
            statut="ACTIF",
            id_client=1,
            id_chasseur=1,
        )


def test_update_mandat_success() -> None:
    db = MagicMock()
    mandat = build_mandat()

    service = MandatService(db)
    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    payload = MandatUpdate(
        statut="SUSPENDU",
        commentaire="Runtime update validation",
    )

    result = service.update_mandat(
        mandat_id=36,
        payload=payload,
    )

    assert result is mandat
    assert result.statut == "SUSPENDU"
    assert (
        result.commentaire
        == "Runtime update validation"
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(mandat)


def test_update_rejects_duplicate_reference() -> None:
    db = MagicMock()

    mandat = build_mandat()

    other_mandat = build_mandat()
    other_mandat.id_mandat = 99
    other_mandat.reference_mandat = "OTHER-REF"

    service = MandatService(db)
    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )
    service.repository.get_by_reference = MagicMock(
        return_value=other_mandat
    )

    payload = MandatUpdate(
        reference_mandat="OTHER-REF"
    )

    with pytest.raises(
        MandatAlreadyExistsError
    ):
        service.update_mandat(
            mandat_id=36,
            payload=payload,
        )


def test_delete_mandat_success() -> None:
    db = MagicMock()
    mandat = build_mandat()

    service = MandatService(db)
    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )
    service.repository.delete = MagicMock()

    service.delete_mandat(36)

    service.repository.delete.assert_called_once_with(
        mandat
    )
    db.commit.assert_called_once()