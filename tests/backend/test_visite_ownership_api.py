from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.db.models.visite import Visite
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.visite import VisiteCreate, VisiteUpdate


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


def build_chasseur_user(
    id_chasseur: int | None = 4,
) -> AuthenticatedUser:
    return AuthenticatedUser(
        id_utilisateur=10,
        email="chasseur@example.com",
        role="CHASSEUR",
        id_chasseur=id_chasseur,
    )


def build_admin_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id_utilisateur=1,
        email="admin@example.com",
        role="ADMIN",
    )


def build_create_payload() -> VisiteCreate:
    return VisiteCreate(
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


def test_chasseur_list_is_scoped() -> None:
    service = MagicMock()
    service.list_visites_for_chasseur.return_value = [
        build_visite()
    ]

    from src.api.api.v1.endpoints.visites import (
        list_visites,
    )

    result = list_visites(
        presentation_id=None,
        service=service,
        current_user=build_chasseur_user(4),
    )

    assert len(result) == 1

    service.list_visites_for_chasseur.assert_called_once_with(
        chasseur_id=4,
        presentation_id=None,
    )
    service.list_visites.assert_not_called()


def test_chasseur_list_preserves_presentation_filter() -> None:
    service = MagicMock()
    service.list_visites_for_chasseur.return_value = [
        build_visite()
    ]

    from src.api.api.v1.endpoints.visites import (
        list_visites,
    )

    list_visites(
        presentation_id=19,
        service=service,
        current_user=build_chasseur_user(4),
    )

    service.list_visites_for_chasseur.assert_called_once_with(
        chasseur_id=4,
        presentation_id=19,
    )


def test_chasseur_without_identity_cannot_list() -> None:
    service = MagicMock()

    from src.api.api.v1.endpoints.visites import (
        list_visites,
    )

    with pytest.raises(HTTPException) as exc:
        list_visites(
            presentation_id=None,
            service=service,
            current_user=build_chasseur_user(None),
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Hunter identity is not available"
    )


def test_admin_list_remains_unrestricted() -> None:
    service = MagicMock()
    service.list_visites.return_value = [
        build_visite()
    ]

    from src.api.api.v1.endpoints.visites import (
        list_visites,
    )

    result = list_visites(
        presentation_id=None,
        service=service,
        current_user=build_admin_user(),
    )

    assert len(result) == 1

    service.list_visites.assert_called_once_with(
        presentation_id=None
    )
    service.list_visites_for_chasseur.assert_not_called()


def test_chasseur_can_get_accessible_visite() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_visite.return_value = 4
    service.get_visite.return_value = build_visite()

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = True

    with patch(
        "src.api.api.v1.endpoints.visites."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.visites import (
            get_visite,
        )

        result = get_visite(
            visite_id=1,
            service=service,
            current_user=build_chasseur_user(4),
        )

    assert result.id_visite == 1

    affectation_service.hunter_can_access_demande.assert_called_once_with(
        demande_id=4,
        chasseur_id=4,
    )
    service.get_visite.assert_called_once_with(1)


def test_chasseur_cannot_get_cross_owner_visite() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_visite.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = False

    with patch(
        "src.api.api.v1.endpoints.visites."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.visites import (
            get_visite,
        )

        with pytest.raises(HTTPException) as exc:
            get_visite(
                visite_id=1,
                service=service,
                current_user=build_chasseur_user(99),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"
    service.get_visite.assert_not_called()


def test_chasseur_can_create_for_accessible_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_presentation.return_value = 4
    service.create_visite.return_value = build_visite()

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = True

    payload = build_create_payload()

    with patch(
        "src.api.api.v1.endpoints.visites."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.visites import (
            create_visite,
        )

        result = create_visite(
            payload=payload,
            service=service,
            current_user=build_chasseur_user(4),
        )

    assert result.id_visite == 1

    affectation_service.hunter_can_access_demande.assert_called_once_with(
        demande_id=4,
        chasseur_id=4,
    )

    service.create_visite.assert_called_once_with(
        payload,
        utilisateur="chasseur@example.com",
    )


def test_chasseur_cannot_create_for_cross_owner_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_presentation.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = False

    payload = build_create_payload()

    with patch(
        "src.api.api.v1.endpoints.visites."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.visites import (
            create_visite,
        )

        with pytest.raises(HTTPException) as exc:
            create_visite(
                payload=payload,
                service=service,
                current_user=build_chasseur_user(99),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"
    service.create_visite.assert_not_called()


def test_chasseur_can_update_accessible_visite() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_visite.return_value = 4
    service.update_visite.return_value = build_visite()

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = True

    payload = VisiteUpdate(
        statut="REALISEE",
        compte_rendu="Visite completed",
        note=4,
    )

    with patch(
        "src.api.api.v1.endpoints.visites."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.visites import (
            update_visite,
        )

        result = update_visite(
            visite_id=1,
            payload=payload,
            service=service,
            current_user=build_chasseur_user(4),
        )

    assert result.id_visite == 1

    service.update_visite.assert_called_once_with(
        1,
        payload,
        utilisateur="chasseur@example.com",
    )


def test_chasseur_cannot_update_cross_owner_visite() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_visite.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = False

    payload = VisiteUpdate(
        statut="REALISEE",
        compte_rendu="Visite completed",
        note=4,
    )

    with patch(
        "src.api.api.v1.endpoints.visites."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.visites import (
            update_visite,
        )

        with pytest.raises(HTTPException) as exc:
            update_visite(
                visite_id=1,
                payload=payload,
                service=service,
                current_user=build_chasseur_user(99),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"
    service.update_visite.assert_not_called()


def test_chasseur_can_delete_accessible_visite() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_visite.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = True

    with patch(
        "src.api.api.v1.endpoints.visites."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.visites import (
            delete_visite,
        )

        result = delete_visite(
            visite_id=1,
            service=service,
            current_user=build_chasseur_user(4),
        )

    assert result.status_code == 204

    service.delete_visite.assert_called_once_with(
        1,
        utilisateur="chasseur@example.com",
    )


def test_chasseur_cannot_delete_cross_owner_visite() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_visite.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = False

    with patch(
        "src.api.api.v1.endpoints.visites."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.visites import (
            delete_visite,
        )

        with pytest.raises(HTTPException) as exc:
            delete_visite(
                visite_id=1,
                service=service,
                current_user=build_chasseur_user(99),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"
    service.delete_visite.assert_not_called()