from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.api.v1.endpoints.mandats import (
    create_mandat,
    delete_mandat,
    get_mandat,
    list_mandat_periods,
    list_mandats,
    renew_mandat,
    update_mandat,
)
from src.api.db.models.mandat import Mandat
from src.api.db.models.mandat_periode import MandatPeriode
from src.api.schemas.mandat import (
    MandatCreate,
    MandatRenew,
    MandatUpdate,
)
from src.api.services.mandat import (
    ChasseurNotFoundForMandatError,
    ClientNotFoundForMandatError,
    MandatAlreadyExistsError,
    MandatNotFoundError,
    MandatValidationError,
)


TEST_USER_EMAIL = "admin.auth.test@example.com"


def build_current_user() -> SimpleNamespace:
    return SimpleNamespace(
        email=TEST_USER_EMAIL,
        role="ADMIN",
        id_chasseur=None,
        id_client=None,
    )


def build_chasseur_user(
    id_chasseur: int | None,
) -> SimpleNamespace:
    return SimpleNamespace(
        email="hunter.auth.test@example.com",
        role="CHASSEUR",
        id_chasseur=id_chasseur,
        id_client=None,
    )


def build_mandat() -> Mandat:
    return Mandat(
        id_mandat=36,
        reference_mandat="API-TEST-MANDAT",
        type_mandat="EXCLUSIF",
        date_signature=date(2026, 8, 30),
        mode_signature="ELECTRONIQUE",
        date_debut=date(2026, 8, 30),
        date_fin=date(2027, 2, 28),
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
        date_fin=date(2027, 2, 28),
        statut="ACTIF",
        id_client=1,
        id_chasseur=1,
    )


def build_initial_period() -> MandatPeriode:
    return MandatPeriode(
        id_mandat_periode=100,
        id_mandat=36,
        numero_periode=1,
        type_periode="INITIAL",
        date_debut=date(2026, 8, 30),
        date_fin=date(2027, 2, 28),
        date_renouvellement=None,
        commentaire=None,
        est_historique_legacy=False,
        created_at=datetime(
            2026,
            8,
            30,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )


def build_renewal_period() -> MandatPeriode:
    return MandatPeriode(
        id_mandat_periode=101,
        id_mandat=36,
        numero_periode=2,
        type_periode="RENOUVELLEMENT",
        date_debut=date(2027, 2, 28),
        date_fin=date(2027, 8, 28),
        date_renouvellement=date(2027, 2, 28),
        commentaire="Renewed with client approval",
        est_historique_legacy=False,
        created_at=datetime(
            2027,
            2,
            28,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )


# =============================================================================
# LIST
# =============================================================================


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
            current_user=build_current_user(),
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
            current_user=build_current_user(),
        )

    assert len(result) == 1

    service.list_by_client.assert_called_once_with(
        1
    )

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
            current_user=build_current_user(),
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
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Client 999 not found"
    )


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
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Chasseur 999 not found"
    )


# =============================================================================
# GET MANDAT
# =============================================================================


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
            current_user=build_current_user(),
        )

    assert result is mandat

    service.get_mandat.assert_called_once_with(
        36
    )


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
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Mandat 999 not found"
    )


# =============================================================================
# CONTRACTUAL HISTORY
# =============================================================================


def test_list_mandat_periods_success() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()

    periods = [
        build_initial_period(),
        build_renewal_period(),
    ]

    service.get_mandat.return_value = mandat
    service.list_periods.return_value = periods

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = list_mandat_periods(
            mandat_id=36,
            db=db,
            current_user=build_current_user(),
        )

    assert result == periods

    service.get_mandat.assert_called_once_with(
        36
    )

    service.list_periods.assert_called_once_with(
        36
    )


def test_list_mandat_periods_returns_404_when_missing() -> None:
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
            list_mandat_periods(
                mandat_id=999,
                db=db,
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Mandat 999 not found"
    )

    service.list_periods.assert_not_called()


# =============================================================================
# CREATE
# =============================================================================


def test_create_mandat_success() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()

    service.create_mandat.return_value = mandat

    payload = build_create_payload()
    current_user = build_current_user()

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = create_mandat(
            payload=payload,
            db=db,
            current_user=current_user,
        )

    assert result is mandat

    service.create_mandat.assert_called_once_with(
        payload,
        utilisateur=TEST_USER_EMAIL,
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
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 409

    assert (
        exc.value.detail
        == "Mandat already exists"
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
                current_user=build_current_user(),
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
                current_user=build_current_user(),
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
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 422

    assert (
        exc.value.detail
        == "Database constraint violation"
    )


# =============================================================================
# RENEW
# =============================================================================


def test_renew_mandat_success() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    renewed_mandat = build_mandat()
    renewal_period = build_renewal_period()

    renewed_mandat.date_debut = date(
        2027,
        2,
        28,
    )

    renewed_mandat.date_fin = date(
        2027,
        8,
        28,
    )

    service.get_mandat.return_value = mandat

    service.renew_mandat.return_value = (
        renewed_mandat,
        renewal_period,
    )

    payload = MandatRenew(
        date_renouvellement=date(
            2027,
            2,
            28,
        ),
        commentaire="Renewed with client approval",
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = renew_mandat(
            mandat_id=36,
            payload=payload,
            db=db,
            current_user=build_current_user(),
        )

    assert result.mandat.id_mandat == 36

    assert (
        result.mandat.date_debut
        == date(2027, 2, 28)
    )

    assert (
        result.mandat.date_fin
        == date(2027, 8, 28)
    )

    assert (
        result.periode.id_mandat_periode
        == 101
    )

    assert (
        result.periode.numero_periode
        == 2
    )

    assert (
        result.periode.type_periode
        == "RENOUVELLEMENT"
    )

    service.get_mandat.assert_called_once_with(
        36
    )

    service.renew_mandat.assert_called_once_with(
        36,
        payload,
        utilisateur=TEST_USER_EMAIL,
    )


def test_renew_mandat_returns_404_when_missing() -> None:
    db = MagicMock()
    service = MagicMock()

    service.get_mandat.side_effect = (
        MandatNotFoundError(
            "Mandat 999 not found"
        )
    )

    payload = MandatRenew(
        date_renouvellement=date(
            2027,
            2,
            28,
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            renew_mandat(
                mandat_id=999,
                payload=payload,
                db=db,
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Mandat 999 not found"
    )

    service.renew_mandat.assert_not_called()


def test_renew_mandat_returns_422_for_validation_error() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()

    service.get_mandat.return_value = mandat

    service.renew_mandat.side_effect = (
        MandatValidationError(
            "Mandat renewal violates "
            "a database constraint"
        )
    )

    payload = MandatRenew(
        date_renouvellement=date(
            2027,
            2,
            28,
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            renew_mandat(
                mandat_id=36,
                payload=payload,
                db=db,
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 422

    assert (
        exc.value.detail
        == (
            "Mandat renewal violates "
            "a database constraint"
        )
    )


# =============================================================================
# UPDATE
# =============================================================================


def test_update_mandat_success() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()

    service.get_mandat.return_value = mandat
    service.update_mandat.return_value = mandat

    payload = MandatUpdate(
        statut="SUSPENDU"
    )

    current_user = build_current_user()

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = update_mandat(
            mandat_id=36,
            payload=payload,
            db=db,
            current_user=current_user,
        )

    assert result is mandat

    service.get_mandat.assert_called_once_with(
        36
    )

    service.update_mandat.assert_called_once_with(
        36,
        payload,
        utilisateur=TEST_USER_EMAIL,
    )


def test_update_mandat_returns_404() -> None:
    db = MagicMock()
    service = MagicMock()

    service.get_mandat.side_effect = (
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
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 404

    service.update_mandat.assert_not_called()


def test_update_mandat_returns_409_for_duplicate() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()

    service.get_mandat.return_value = mandat

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
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 409


def test_update_mandat_returns_422_for_validation_error() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()

    service.get_mandat.return_value = mandat

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
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 422

    assert exc.value.detail == "Invalid update"


# =============================================================================
# DELETE
# =============================================================================


def test_delete_mandat_success() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()

    service.get_mandat.return_value = mandat

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = delete_mandat(
            mandat_id=36,
            db=db,
            current_user=build_current_user(),
        )

    assert result is None

    service.get_mandat.assert_called_once_with(
        36
    )

    service.delete_mandat.assert_called_once_with(
        36,
        utilisateur=TEST_USER_EMAIL,
    )


def test_delete_mandat_returns_404_when_missing() -> None:
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
            delete_mandat(
                mandat_id=999,
                db=db,
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 404

    service.delete_mandat.assert_not_called()


def test_delete_mandat_returns_409_on_conflict() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()

    service.get_mandat.return_value = mandat

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
                current_user=build_current_user(),
            )

    assert exc.value.status_code == 409

    assert (
        exc.value.detail
        == "Mandat is referenced"
    )


# =============================================================================
# CHASSEUR OWNERSHIP
# =============================================================================


def test_chasseur_list_mandats_is_scoped_to_own_id() -> None:
    db = MagicMock()
    service = MagicMock()

    own_mandat = build_mandat()
    own_mandat.id_chasseur = 7

    service.list_by_chasseur.return_value = [
        own_mandat
    ]

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = list_mandats(
            client_id=None,
            chasseur_id=None,
            db=db,
            current_user=build_chasseur_user(7),
        )

    assert result == [own_mandat]

    service.list_by_chasseur.assert_called_once_with(
        7
    )

    service.list_mandats.assert_not_called()


def test_chasseur_cannot_list_other_chasseur_mandats() -> None:
    db = MagicMock()
    service = MagicMock()

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            list_mandats(
                client_id=None,
                chasseur_id=8,
                db=db,
                current_user=build_chasseur_user(7),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Resource not found"
    )

    service.list_by_chasseur.assert_not_called()


def test_chasseur_gets_own_mandat() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    mandat.id_chasseur = 7

    service.get_mandat.return_value = mandat

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = get_mandat(
            mandat_id=36,
            db=db,
            current_user=build_chasseur_user(7),
        )

    assert result is mandat


def test_chasseur_cannot_get_other_chasseur_mandat() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    mandat.id_chasseur = 8

    service.get_mandat.return_value = mandat

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            get_mandat(
                mandat_id=36,
                db=db,
                current_user=build_chasseur_user(7),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Resource not found"
    )


def test_chasseur_can_list_own_mandat_periods() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    mandat.id_chasseur = 7

    period = build_initial_period()

    service.get_mandat.return_value = mandat

    service.list_periods.return_value = [
        period
    ]

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = list_mandat_periods(
            mandat_id=36,
            db=db,
            current_user=build_chasseur_user(7),
        )

    assert result == [period]

    service.list_periods.assert_called_once_with(
        36
    )


def test_chasseur_cannot_list_other_mandat_periods() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    mandat.id_chasseur = 8

    service.get_mandat.return_value = mandat

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            list_mandat_periods(
                mandat_id=36,
                db=db,
                current_user=build_chasseur_user(7),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Resource not found"
    )

    service.list_periods.assert_not_called()


def test_chasseur_can_renew_own_mandat() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    mandat.id_chasseur = 7

    renewed_mandat = build_mandat()
    renewed_mandat.id_chasseur = 7
    renewed_mandat.date_debut = date(
        2027,
        2,
        28,
    )
    renewed_mandat.date_fin = date(
        2027,
        8,
        28,
    )

    renewal_period = build_renewal_period()

    service.get_mandat.return_value = mandat

    service.renew_mandat.return_value = (
        renewed_mandat,
        renewal_period,
    )

    payload = MandatRenew(
        date_renouvellement=date(
            2027,
            2,
            28,
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        result = renew_mandat(
            mandat_id=36,
            payload=payload,
            db=db,
            current_user=build_chasseur_user(7),
        )

    assert result.mandat.id_chasseur == 7

    assert (
        result.periode.numero_periode
        == 2
    )

    service.renew_mandat.assert_called_once_with(
        36,
        payload,
        utilisateur="hunter.auth.test@example.com",
    )


def test_chasseur_cannot_renew_other_chasseur_mandat() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    mandat.id_chasseur = 8

    service.get_mandat.return_value = mandat

    payload = MandatRenew(
        date_renouvellement=date(
            2027,
            2,
            28,
        )
    )

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            renew_mandat(
                mandat_id=36,
                payload=payload,
                db=db,
                current_user=build_chasseur_user(7),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Resource not found"
    )

    service.renew_mandat.assert_not_called()


def test_chasseur_cannot_create_mandat_for_other_chasseur() -> None:
    db = MagicMock()
    service = MagicMock()

    payload = build_create_payload()
    payload.id_chasseur = 8

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_mandat(
                payload=payload,
                db=db,
                current_user=build_chasseur_user(7),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Resource not found"
    )

    service.create_mandat.assert_not_called()


def test_chasseur_cannot_reassign_mandat_to_other_chasseur() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    mandat.id_chasseur = 7

    service.get_mandat.return_value = mandat

    payload = MandatUpdate(
        id_chasseur=8
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
                current_user=build_chasseur_user(7),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Resource not found"
    )

    service.update_mandat.assert_not_called()


def test_chasseur_cannot_update_other_chasseur_mandat() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    mandat.id_chasseur = 8

    service.get_mandat.return_value = mandat

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            update_mandat(
                mandat_id=36,
                payload=MandatUpdate(
                    commentaire="Forbidden update"
                ),
                db=db,
                current_user=build_chasseur_user(7),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Resource not found"
    )

    service.update_mandat.assert_not_called()


def test_chasseur_cannot_delete_other_chasseur_mandat() -> None:
    db = MagicMock()
    service = MagicMock()

    mandat = build_mandat()
    mandat.id_chasseur = 8

    service.get_mandat.return_value = mandat

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            delete_mandat(
                mandat_id=36,
                db=db,
                current_user=build_chasseur_user(7),
            )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Resource not found"
    )

    service.delete_mandat.assert_not_called()


def test_chasseur_without_linked_identity_is_rejected() -> None:
    db = MagicMock()
    service = MagicMock()

    with patch(
        "src.api.api.v1.endpoints.mandats.MandatService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            list_mandats(
                client_id=None,
                chasseur_id=None,
                db=db,
                current_user=build_chasseur_user(None),
            )

    assert exc.value.status_code == 403

    assert (
        exc.value.detail
        == "Hunter identity is not available"
    )