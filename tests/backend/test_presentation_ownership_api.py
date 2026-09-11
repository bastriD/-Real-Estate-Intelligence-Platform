from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.db.models.presentation import Presentation
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.presentation import (
    PresentationCreate,
    PresentationUpdate,
)


def build_presentation() -> Presentation:
    presentation = Presentation(
        id_demande_version=54,
        id_bien=13,
        score_matching=Decimal("91.25"),
        statut="PRESENTE",
        date_presentation=datetime(
            2026,
            8,
            30,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )
    presentation.id_presentation = 1
    return presentation


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


def build_service_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id_utilisateur=2,
        email="service@example.com",
        role="SERVICE",
    )


def build_create_payload() -> PresentationCreate:
    return PresentationCreate(
        id_demande_version=54,
        id_bien=13,
        score_matching=91.25,
        statut="PRESENTE",
        date_presentation=datetime(
            2026,
            8,
            30,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )


def test_chasseur_list_is_scoped() -> None:
    service = MagicMock()
    service.list_presentations_for_chasseur.return_value = [
        build_presentation()
    ]

    from src.api.api.v1.endpoints.presentations import (
        list_presentations,
    )

    result = list_presentations(
        demande_version_id=None,
        bien_id=None,
        service=service,
        current_user=build_chasseur_user(4),
    )

    assert len(result) == 1

    service.list_presentations_for_chasseur.assert_called_once_with(
        chasseur_id=4,
        demande_version_id=None,
        bien_id=None,
    )
    service.list_presentations.assert_not_called()


def test_chasseur_list_preserves_filters() -> None:
    service = MagicMock()
    service.list_presentations_for_chasseur.return_value = [
        build_presentation()
    ]

    from src.api.api.v1.endpoints.presentations import (
        list_presentations,
    )

    list_presentations(
        demande_version_id=54,
        bien_id=13,
        service=service,
        current_user=build_chasseur_user(4),
    )

    service.list_presentations_for_chasseur.assert_called_once_with(
        chasseur_id=4,
        demande_version_id=54,
        bien_id=13,
    )


def test_chasseur_without_identity_cannot_list() -> None:
    service = MagicMock()

    from src.api.api.v1.endpoints.presentations import (
        list_presentations,
    )

    with pytest.raises(HTTPException) as exc:
        list_presentations(
            demande_version_id=None,
            bien_id=None,
            service=service,
            current_user=build_chasseur_user(None),
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Hunter identity is not available"
    )


def test_admin_list_remains_unrestricted() -> None:
    service = MagicMock()
    service.list_presentations.return_value = [
        build_presentation()
    ]

    from src.api.api.v1.endpoints.presentations import (
        list_presentations,
    )

    result = list_presentations(
        demande_version_id=None,
        bien_id=None,
        service=service,
        current_user=build_admin_user(),
    )

    assert len(result) == 1
    service.list_presentations.assert_called_once_with(
        demande_version_id=None,
        bien_id=None,
    )
    service.list_presentations_for_chasseur.assert_not_called()


def test_service_list_remains_unrestricted() -> None:
    service = MagicMock()
    service.list_presentations.return_value = [
        build_presentation()
    ]

    from src.api.api.v1.endpoints.presentations import (
        list_presentations,
    )

    list_presentations(
        demande_version_id=None,
        bien_id=None,
        service=service,
        current_user=build_service_user(),
    )

    service.list_presentations.assert_called_once_with(
        demande_version_id=None,
        bien_id=None,
    )
    service.list_presentations_for_chasseur.assert_not_called()


def test_chasseur_can_get_accessible_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_presentation.return_value = 4
    service.get_presentation.return_value = build_presentation()

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = True

    with patch(
        "src.api.api.v1.endpoints.presentations."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.presentations import (
            get_presentation,
        )

        result = get_presentation(
            presentation_id=1,
            service=service,
            current_user=build_chasseur_user(4),
        )

    assert result.id_presentation == 1

    affectation_service.hunter_can_access_demande.assert_called_once_with(
        demande_id=4,
        chasseur_id=4,
    )
    service.get_presentation.assert_called_once_with(1)


def test_chasseur_cannot_get_cross_owner_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_presentation.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = False

    with patch(
        "src.api.api.v1.endpoints.presentations."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.presentations import (
            get_presentation,
        )

        with pytest.raises(HTTPException) as exc:
            get_presentation(
                presentation_id=1,
                service=service,
                current_user=build_chasseur_user(99),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"
    service.get_presentation.assert_not_called()


def test_chasseur_can_create_for_accessible_demande() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_version.return_value = 4
    service.create_presentation.return_value = (
        build_presentation()
    )

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = True

    payload = build_create_payload()

    with patch(
        "src.api.api.v1.endpoints.presentations."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.presentations import (
            create_presentation,
        )

        result = create_presentation(
            payload=payload,
            service=service,
            current_user=build_chasseur_user(4),
        )

    assert result.id_presentation == 1

    affectation_service.hunter_can_access_demande.assert_called_once_with(
        demande_id=4,
        chasseur_id=4,
    )

    service.create_presentation.assert_called_once_with(
        payload,
        utilisateur="chasseur@example.com",
    )


def test_chasseur_cannot_create_for_cross_owner_demande() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_version.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = False

    payload = build_create_payload()

    with patch(
        "src.api.api.v1.endpoints.presentations."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.presentations import (
            create_presentation,
        )

        with pytest.raises(HTTPException) as exc:
            create_presentation(
                payload=payload,
                service=service,
                current_user=build_chasseur_user(99),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"
    service.create_presentation.assert_not_called()


def test_chasseur_can_update_accessible_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_presentation.return_value = 4
    service.update_presentation.return_value = (
        build_presentation()
    )

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = True

    payload = PresentationUpdate(
        statut="VISITE",
    )

    with patch(
        "src.api.api.v1.endpoints.presentations."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.presentations import (
            update_presentation,
        )

        result = update_presentation(
            presentation_id=1,
            payload=payload,
            service=service,
            current_user=build_chasseur_user(4),
        )

    assert result.id_presentation == 1

    service.update_presentation.assert_called_once_with(
        1,
        payload,
        utilisateur="chasseur@example.com",
    )


def test_chasseur_cannot_update_cross_owner_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_presentation.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = False

    payload = PresentationUpdate(
        statut="VISITE",
    )

    with patch(
        "src.api.api.v1.endpoints.presentations."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.presentations import (
            update_presentation,
        )

        with pytest.raises(HTTPException) as exc:
            update_presentation(
                presentation_id=1,
                payload=payload,
                service=service,
                current_user=build_chasseur_user(99),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"
    service.update_presentation.assert_not_called()


def test_chasseur_can_delete_accessible_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_presentation.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = True

    with patch(
        "src.api.api.v1.endpoints.presentations."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.presentations import (
            delete_presentation,
        )

        result = delete_presentation(
            presentation_id=1,
            service=service,
            current_user=build_chasseur_user(4),
        )

    assert result is None

    service.delete_presentation.assert_called_once_with(
        1,
        utilisateur="chasseur@example.com",
    )


def test_chasseur_cannot_delete_cross_owner_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_presentation.return_value = 4

    affectation_service = MagicMock()
    affectation_service.hunter_can_access_demande.return_value = False

    with patch(
        "src.api.api.v1.endpoints.presentations."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.presentations import (
            delete_presentation,
        )

        with pytest.raises(HTTPException) as exc:
            delete_presentation(
                presentation_id=1,
                service=service,
                current_user=build_chasseur_user(99),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"
    service.delete_presentation.assert_not_called()