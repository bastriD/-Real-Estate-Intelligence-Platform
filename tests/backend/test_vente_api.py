from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.vente import (
    VenteCreate,
    VenteOrigine,
)


def build_admin_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id_utilisateur=1,
        email="admin@example.com",
        role="ADMIN",
    )


def build_chasseur_user(
    id_chasseur: int | None = 1,
) -> AuthenticatedUser:
    return AuthenticatedUser(
        id_utilisateur=10,
        email="chasseur@example.com",
        role="CHASSEUR",
        id_chasseur=id_chasseur,
    )


def build_vente(
    *,
    id_vente: int = 1,
    id_mandat: int = 11,
    id_chasseur_beneficiaire: int | None = 1,
):
    return SimpleNamespace(
        id_vente=id_vente,
        id_mandat=id_mandat,
        id_mandat_periode=18,
        id_presentation=31,
        id_bien=11225,
        id_chasseur_beneficiaire=(
            id_chasseur_beneficiaire
        ),
        origine_vente="CHASSEUR",
        date_acte_authentique=date(
            2026,
            9,
            12,
        ),
        montant_achat=Decimal(
            "420000.00"
        ),
        date_creation=None,
    )


def build_payload(
    *,
    id_mandat: int = 11,
) -> VenteCreate:
    return VenteCreate(
        id_mandat=id_mandat,
        id_presentation=31,
        id_bien=11225,
        origine_vente=VenteOrigine.CHASSEUR,
        date_acte_authentique=date(
            2026,
            9,
            12,
        ),
        montant_achat=Decimal(
            "420000.00"
        ),
    )


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_admin_list_is_unrestricted(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service.list_ventes.return_value = [
        build_vente()
    ]

    from src.api.api.v1.endpoints.ventes import (
        list_ventes,
    )

    result = list_ventes(
        mandat_id=None,
        chasseur_id=None,
        db=MagicMock(),
        current_user=build_admin_user(),
    )

    assert len(result) == 1

    service.list_ventes.assert_called_once_with()


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_admin_can_filter_by_mandat(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service.list_by_mandat.return_value = [
        build_vente()
    ]

    from src.api.api.v1.endpoints.ventes import (
        list_ventes,
    )

    result = list_ventes(
        mandat_id=11,
        chasseur_id=None,
        db=MagicMock(),
        current_user=build_admin_user(),
    )

    assert len(result) == 1

    service.list_by_mandat.assert_called_once_with(
        11
    )


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_admin_can_filter_by_chasseur(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service.list_by_chasseur.return_value = [
        build_vente()
    ]

    from src.api.api.v1.endpoints.ventes import (
        list_ventes,
    )

    result = list_ventes(
        mandat_id=None,
        chasseur_id=1,
        db=MagicMock(),
        current_user=build_admin_user(),
    )

    assert len(result) == 1

    service.list_by_chasseur.assert_called_once_with(
        1
    )


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_chasseur_list_is_scoped_to_self(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service.list_by_chasseur.return_value = [
        build_vente()
    ]

    from src.api.api.v1.endpoints.ventes import (
        list_ventes,
    )

    result = list_ventes(
        mandat_id=None,
        chasseur_id=None,
        db=MagicMock(),
        current_user=build_chasseur_user(1),
    )

    assert len(result) == 1

    service.list_by_chasseur.assert_called_once_with(
        1
    )

    service.list_ventes.assert_not_called()


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_chasseur_without_identity_cannot_list(
    service_class: MagicMock,
) -> None:
    from src.api.api.v1.endpoints.ventes import (
        list_ventes,
    )

    with pytest.raises(HTTPException) as exc:
        list_ventes(
            mandat_id=None,
            chasseur_id=None,
            db=MagicMock(),
            current_user=build_chasseur_user(
                None
            ),
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Hunter identity is not available"
    )


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_chasseur_cannot_filter_another_chasseur(
    service_class: MagicMock,
) -> None:
    from src.api.api.v1.endpoints.ventes import (
        list_ventes,
    )

    with pytest.raises(HTTPException) as exc:
        list_ventes(
            mandat_id=None,
            chasseur_id=2,
            db=MagicMock(),
            current_user=build_chasseur_user(1),
        )

    assert exc.value.status_code == 404


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_chasseur_gets_own_vente(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service.get_vente.return_value = (
        build_vente(
            id_chasseur_beneficiaire=1
        )
    )

    from src.api.api.v1.endpoints.ventes import (
        get_vente,
    )

    result = get_vente(
        vente_id=1,
        db=MagicMock(),
        current_user=build_chasseur_user(1),
    )

    assert result.id_vente == 1

    service.get_vente.assert_called_once_with(
        1
    )


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_chasseur_cannot_get_other_chasseur_vente(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service.get_vente.return_value = (
        build_vente(
            id_chasseur_beneficiaire=2
        )
    )

    from src.api.api.v1.endpoints.ventes import (
        get_vente,
    )

    with pytest.raises(HTTPException) as exc:
        get_vente(
            vente_id=1,
            db=MagicMock(),
            current_user=build_chasseur_user(1),
        )

    assert exc.value.status_code == 404


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_chasseur_cannot_get_vente_without_beneficiary(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service.get_vente.return_value = (
        build_vente(
            id_chasseur_beneficiaire=None
        )
    )

    from src.api.api.v1.endpoints.ventes import (
        get_vente,
    )

    with pytest.raises(HTTPException) as exc:
        get_vente(
            vente_id=1,
            db=MagicMock(),
            current_user=build_chasseur_user(1),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Resource not found"
    )


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_admin_can_create_vente(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service.create_vente.return_value = (
        build_vente()
    )

    from src.api.api.v1.endpoints.ventes import (
        create_vente,
    )

    payload = build_payload()

    result = create_vente(
        payload=payload,
        db=MagicMock(),
        current_user=build_admin_user(),
    )

    assert result.id_vente == 1

    service.create_vente.assert_called_once_with(
        payload,
        utilisateur="admin@example.com",
    )


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_chasseur_can_create_on_own_mandat(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service._get_mandat.return_value = (
        SimpleNamespace(
            id_mandat=11,
            id_chasseur=1,
        )
    )

    service.create_vente.return_value = (
        build_vente()
    )

    from src.api.api.v1.endpoints.ventes import (
        create_vente,
    )

    payload = build_payload()

    result = create_vente(
        payload=payload,
        db=MagicMock(),
        current_user=build_chasseur_user(1),
    )

    assert result.id_vente == 1

    service._get_mandat.assert_called_once_with(
        11
    )

    service.create_vente.assert_called_once_with(
        payload,
        utilisateur="chasseur@example.com",
    )


@patch(
    "src.api.api.v1.endpoints.ventes.VenteService"
)
def test_chasseur_cannot_create_on_other_mandat(
    service_class: MagicMock,
) -> None:
    service = service_class.return_value

    service._get_mandat.return_value = (
        SimpleNamespace(
            id_mandat=11,
            id_chasseur=2,
        )
    )

    from src.api.api.v1.endpoints.ventes import (
        create_vente,
    )

    with pytest.raises(HTTPException) as exc:
        create_vente(
            payload=build_payload(),
            db=MagicMock(),
            current_user=build_chasseur_user(1),
        )

    assert exc.value.status_code == 404

    service.create_vente.assert_not_called()