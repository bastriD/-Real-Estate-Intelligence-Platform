from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.db.models.offre import Offre
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.offre import (
    OffreCreate,
    OffreDecision,
    OffreRevision,
)


def build_offre(
    *,
    id_offre: int = 10,
    numero_version: int = 1,
    statut: str = "SOUMISE",
) -> Offre:
    return Offre(
        id_offre=id_offre,
        id_presentation=19,
        numero_version=numero_version,
        montant=Decimal("250000.00"),
        date_offre=datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        date_expiration=None,
        date_decision=None,
        statut=statut,
        commentaire=None,
        date_creation=datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ),
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


def build_create_payload() -> OffreCreate:
    return OffreCreate(
        id_presentation=19,
        montant=Decimal("250000.00"),
        commentaire="Initial offer",
    )


def test_chasseur_list_is_scoped() -> None:
    service = MagicMock()
    service.list_offres_for_chasseur.return_value = [
        build_offre()
    ]

    from src.api.api.v1.endpoints.offres import (
        list_offres,
    )

    result = list_offres(
        presentation_id=None,
        service=service,
        current_user=build_chasseur_user(4),
    )

    assert len(result) == 1

    (
        service.list_offres_for_chasseur
        .assert_called_once_with(
            chasseur_id=4,
            presentation_id=None,
        )
    )

    service.list_offres.assert_not_called()


def test_chasseur_list_preserves_presentation_filter() -> None:
    service = MagicMock()
    service.list_offres_for_chasseur.return_value = [
        build_offre()
    ]

    from src.api.api.v1.endpoints.offres import (
        list_offres,
    )

    list_offres(
        presentation_id=19,
        service=service,
        current_user=build_chasseur_user(4),
    )

    (
        service.list_offres_for_chasseur
        .assert_called_once_with(
            chasseur_id=4,
            presentation_id=19,
        )
    )


def test_chasseur_without_identity_cannot_list() -> None:
    service = MagicMock()

    from src.api.api.v1.endpoints.offres import (
        list_offres,
    )

    with pytest.raises(HTTPException) as exc:
        list_offres(
            presentation_id=None,
            service=service,
            current_user=build_chasseur_user(
                None
            ),
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Hunter identity is not available"
    )


def test_admin_list_remains_unrestricted() -> None:
    service = MagicMock()
    service.list_offres.return_value = [
        build_offre()
    ]

    from src.api.api.v1.endpoints.offres import (
        list_offres,
    )

    result = list_offres(
        presentation_id=None,
        service=service,
        current_user=build_admin_user(),
    )

    assert len(result) == 1

    service.list_offres.assert_called_once_with(
        presentation_id=None
    )

    (
        service.list_offres_for_chasseur
        .assert_not_called()
    )


def test_chasseur_can_get_accessible_offre() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_offre.return_value = 4
    service.get_offre.return_value = build_offre()

    affectation_service = MagicMock()
    (
        affectation_service
        .hunter_can_access_demande
        .return_value
    ) = True

    with patch(
        "src.api.api.v1.endpoints.offres."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.offres import (
            get_offre,
        )

        result = get_offre(
            offre_id=10,
            service=service,
            current_user=build_chasseur_user(4),
        )

    assert result.id_offre == 10

    (
        affectation_service
        .hunter_can_access_demande
        .assert_called_once_with(
            demande_id=4,
            chasseur_id=4,
        )
    )

    service.get_offre.assert_called_once_with(
        10
    )


def test_chasseur_cannot_get_cross_owner_offre() -> None:
    service = MagicMock()
    service.session = MagicMock()
    service.get_demande_id_for_offre.return_value = 4

    affectation_service = MagicMock()
    (
        affectation_service
        .hunter_can_access_demande
        .return_value
    ) = False

    with patch(
        "src.api.api.v1.endpoints.offres."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.offres import (
            get_offre,
        )

        with pytest.raises(
            HTTPException
        ) as exc:
            get_offre(
                offre_id=10,
                service=service,
                current_user=(
                    build_chasseur_user(99)
                ),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Resource not found"
    )

    service.get_offre.assert_not_called()


def test_chasseur_can_create_for_accessible_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()

    (
        service
        .get_demande_id_for_presentation
        .return_value
    ) = 4

    service.create_offre.return_value = (
        build_offre()
    )

    affectation_service = MagicMock()
    (
        affectation_service
        .hunter_can_access_demande
        .return_value
    ) = True

    payload = build_create_payload()

    with patch(
        "src.api.api.v1.endpoints.offres."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.offres import (
            create_offre,
        )

        result = create_offre(
            payload=payload,
            service=service,
            current_user=(
                build_chasseur_user(4)
            ),
        )

    assert result.id_offre == 10

    (
        affectation_service
        .hunter_can_access_demande
        .assert_called_once_with(
            demande_id=4,
            chasseur_id=4,
        )
    )

    service.create_offre.assert_called_once_with(
        payload,
        utilisateur="chasseur@example.com",
    )


def test_chasseur_cannot_create_for_cross_owner_presentation() -> None:
    service = MagicMock()
    service.session = MagicMock()

    (
        service
        .get_demande_id_for_presentation
        .return_value
    ) = 4

    affectation_service = MagicMock()
    (
        affectation_service
        .hunter_can_access_demande
        .return_value
    ) = False

    payload = build_create_payload()

    with patch(
        "src.api.api.v1.endpoints.offres."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.offres import (
            create_offre,
        )

        with pytest.raises(
            HTTPException
        ) as exc:
            create_offre(
                payload=payload,
                service=service,
                current_user=(
                    build_chasseur_user(99)
                ),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Resource not found"
    )

    service.create_offre.assert_not_called()


def test_chasseur_can_decide_accessible_offre() -> None:
    service = MagicMock()
    service.session = MagicMock()

    service.get_demande_id_for_offre.return_value = 4

    decided = build_offre(
        statut="ACCEPTEE"
    )
    service.decide_offre.return_value = decided

    affectation_service = MagicMock()
    (
        affectation_service
        .hunter_can_access_demande
        .return_value
    ) = True

    payload = OffreDecision(
        statut="ACCEPTEE",
        commentaire="Accepted",
    )

    with patch(
        "src.api.api.v1.endpoints.offres."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.offres import (
            decide_offre,
        )

        result = decide_offre(
            offre_id=10,
            payload=payload,
            service=service,
            current_user=(
                build_chasseur_user(4)
            ),
        )

    assert result.statut == "ACCEPTEE"

    service.decide_offre.assert_called_once_with(
        10,
        payload,
        utilisateur="chasseur@example.com",
    )


def test_chasseur_cannot_decide_cross_owner_offre() -> None:
    service = MagicMock()
    service.session = MagicMock()

    service.get_demande_id_for_offre.return_value = 4

    affectation_service = MagicMock()
    (
        affectation_service
        .hunter_can_access_demande
        .return_value
    ) = False

    payload = OffreDecision(
        statut="REFUSEE"
    )

    with patch(
        "src.api.api.v1.endpoints.offres."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.offres import (
            decide_offre,
        )

        with pytest.raises(
            HTTPException
        ) as exc:
            decide_offre(
                offre_id=10,
                payload=payload,
                service=service,
                current_user=(
                    build_chasseur_user(99)
                ),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Resource not found"
    )

    service.decide_offre.assert_not_called()


def test_chasseur_can_revise_accessible_offre() -> None:
    service = MagicMock()
    service.session = MagicMock()

    service.get_demande_id_for_offre.return_value = 4

    revised = build_offre(
        id_offre=11,
        numero_version=2,
    )
    service.revise_offre.return_value = revised

    affectation_service = MagicMock()
    (
        affectation_service
        .hunter_can_access_demande
        .return_value
    ) = True

    payload = OffreRevision(
        montant=Decimal("245000.00"),
        commentaire="Revised offer",
    )

    with patch(
        "src.api.api.v1.endpoints.offres."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.offres import (
            revise_offre,
        )

        result = revise_offre(
            offre_id=10,
            payload=payload,
            service=service,
            current_user=(
                build_chasseur_user(4)
            ),
        )

    assert result.id_offre == 11
    assert result.numero_version == 2

    service.revise_offre.assert_called_once_with(
        10,
        payload,
        utilisateur="chasseur@example.com",
    )


def test_chasseur_cannot_revise_cross_owner_offre() -> None:
    service = MagicMock()
    service.session = MagicMock()

    service.get_demande_id_for_offre.return_value = 4

    affectation_service = MagicMock()
    (
        affectation_service
        .hunter_can_access_demande
        .return_value
    ) = False

    payload = OffreRevision(
        montant=Decimal("245000.00"),
    )

    with patch(
        "src.api.api.v1.endpoints.offres."
        "DemandeAffectationService",
        return_value=affectation_service,
    ):
        from src.api.api.v1.endpoints.offres import (
            revise_offre,
        )

        with pytest.raises(
            HTTPException
        ) as exc:
            revise_offre(
                offre_id=10,
                payload=payload,
                service=service,
                current_user=(
                    build_chasseur_user(99)
                ),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Resource not found"
    )

    service.revise_offre.assert_not_called()