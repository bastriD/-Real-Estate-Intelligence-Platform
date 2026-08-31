from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.api.v1.endpoints.mandats import (
    create_mandat,
    delete_mandat,
    get_mandat,
    list_mandats,
    update_mandat,
)
from src.api.db.models.mandat import Mandat
from src.api.schemas.mandat import (
    MandatCreate,
    MandatUpdate,
)
from src.api.services.mandat import (
    ChasseurNotFoundForMandatError,
    ClientNotFoundForMandatError,
    MandatAlreadyExistsError,
    MandatNotFoundError,
    MandatValidationError,
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


def build_create_payload() -> MandatCreate:
    return MandatCreate(
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


def test_list_mandats_returns_all() -> None:
    db = MagicMock()
    service = MagicMock()
    service.list_mandats.return_value = [
        build_mandat()
    ]

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = list_mandats(
            client_id=None,
            chasseur_id=None,
            db=db,
        )

    assert len(result) == 1
    service.list_mandats.assert_called_once()


def test_list_mandats_filters_by_client() -> None:
    db = MagicMock()
    service = MagicMock()
    service.list_by_client.return_value = [
        build_mandat()
    ]

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = list_mandats(
            client_id=1,
            chasseur_id=None,
            db=db,
        )

    assert len(result) == 1
    service.list_by_client.assert_called_once_with(1)
    service.list_by_chasseur.assert_not_called()


def test_list_mandats_filters_by_chasseur() -> None:
    db = MagicMock()
    service = MagicMock()
    service.list_by_chasseur.return_value = [
        build_mandat()
    ]

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = list_mandats(
            client_id=None,
            chasseur_id=1,
            db=db,
        )

    assert len(result) == 1
    service.list_by_chasseur.assert_called_once_with(
        1
    )


def test_list_mandats_returns_404_for_missing_client() -> None:
    db = MagicMock()
    service = MagicMock()
    service.list_by_client.side_effect = (
        ClientNotFoundForMandatError(
            "Client 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            list_mandats(
                client_id=999,
                chasseur_id=None,
                db=db,
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Client 999 not found"


def test_list_mandats_returns_404_for_missing_chasseur() -> None:
    db = MagicMock()
    service = MagicMock()
    service.list_by_chasseur.side_effect = (
        ChasseurNotFoundForMandatError(
            "Chasseur 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            list_mandats(
                client_id=None,
                chasseur_id=999,
                db=db,
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Chasseur 999 not found"
    )


def test_get_mandat_success() -> None:
    db = MagicMock()
    service = MagicMock()
    mandat = build_mandat()
    service.get_mandat.return_value = mandat

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = get_mandat(
            mandat_id=36,
            db=db,
        )

    assert result is mandat
    service.get_mandat.assert_called_once_with(36)


def test_get_mandat_returns_404_when_missing() -> None:
    db = MagicMock()
    service = MagicMock()
    service.get_mandat.side_effect = (
        MandatNotFoundError(
            "Mandat 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            get_mandat(
                mandat_id=999,
                db=db,
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Mandat 999 not found"


def test_create_mandat_success() -> None:
    db = MagicMock()
    service = MagicMock()
    mandat = build_mandat()
    service.create_mandat.return_value = mandat

    payload = build_create_payload()

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = create_mandat(
            payload=payload,
            db=db,
        )

    assert result is mandat
    service.create_mandat.assert_called_once_with(
        payload
    )


def test_create_mandat_returns_409_for_duplicate() -> None:
    db = MagicMock()
    service = MagicMock()
    service.create_mandat.side_effect = (
        MandatAlreadyExistsError(
            "Mandat already exists"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_mandat(
                payload=build_create_payload(),
                db=db,
            )

    assert exc.value.status_code == 409
    assert exc.value.detail == (
        "Mandat already exists"
    )


def test_create_mandat_returns_404_for_missing_client() -> None:
    db = MagicMock()
    service = MagicMock()
    service.create_mandat.side_effect = (
        ClientNotFoundForMandatError(
            "Client 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_mandat(
                payload=build_create_payload(),
                db=db,
            )

    assert exc.value.status_code == 404


def test_create_mandat_returns_404_for_missing_chasseur() -> None:
    db = MagicMock()
    service = MagicMock()
    service.create_mandat.side_effect = (
        ChasseurNotFoundForMandatError(
            "Chasseur 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_mandat(
                payload=build_create_payload(),
                db=db,
            )

    assert exc.value.status_code == 404


def test_create_mandat_returns_422_for_validation_error() -> None:
    db = MagicMock()
    service = MagicMock()
    service.create_mandat.side_effect = (
        MandatValidationError(
            "Database constraint violation"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_mandat(
                payload=build_create_payload(),
                db=db,
            )

    assert exc.value.status_code == 422
    assert exc.value.detail == (
        "Database constraint violation"
    )


def test_update_mandat_success() -> None:
    db = MagicMock()
    service = MagicMock()
    mandat = build_mandat()
    service.update_mandat.return_value = mandat

    payload = MandatUpdate(
        statut="SUSPENDU"
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = update_mandat(
            mandat_id=36,
            payload=payload,
            db=db,
        )

    assert result is mandat

    service.update_mandat.assert_called_once_with(
        36,
        payload,
    )


def test_update_mandat_returns_404() -> None:
    db = MagicMock()
    service = MagicMock()
    service.update_mandat.side_effect = (
        MandatNotFoundError(
            "Mandat 999 not found"
        )
    )

    payload = MandatUpdate(
        commentaire="Test"
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            update_mandat(
                mandat_id=999,
                payload=payload,
                db=db,
            )

    assert exc.value.status_code == 404


def test_update_mandat_returns_409_for_duplicate() -> None:
    db = MagicMock()
    service = MagicMock()
    service.update_mandat.side_effect = (
        MandatAlreadyExistsError(
            "Reference already exists"
        )
    )

    payload = MandatUpdate(
        reference_mandat="DUPLICATE"
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            update_mandat(
                mandat_id=36,
                payload=payload,
                db=db,
            )

    assert exc.value.status_code == 409


def test_update_mandat_returns_422_for_validation_error() -> None:
    db = MagicMock()
    service = MagicMock()
    service.update_mandat.side_effect = (
        MandatValidationError(
            "Invalid update"
        )
    )

    payload = MandatUpdate(
        commentaire="Test"
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            update_mandat(
                mandat_id=36,
                payload=payload,
                db=db,
            )

    assert exc.value.status_code == 422


def test_delete_mandat_success() -> None:
    db = MagicMock()
    service = MagicMock()

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = delete_mandat(
            mandat_id=36,
            db=db,
        )

    assert result is None
    service.delete_mandat.assert_called_once_with(
        36
    )


def test_delete_mandat_returns_404_when_missing() -> None:
    db = MagicMock()
    service = MagicMock()
    service.delete_mandat.side_effect = (
        MandatNotFoundError(
            "Mandat 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            delete_mandat(
                mandat_id=999,
                db=db,
            )

    assert exc.value.status_code == 404


def test_delete_mandat_returns_409_on_conflict() -> None:
    db = MagicMock()
    service = MagicMock()
    service.delete_mandat.side_effect = (
        MandatValidationError(
            "Mandat is referenced"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            delete_mandat(
                mandat_id=36,
                db=db,
            )

    assert exc.value.status_code == 409
    assert exc.value.detail == (
        "Mandat is referenced"
    )