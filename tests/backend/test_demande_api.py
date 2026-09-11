from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.api.v1.endpoints.demandes import (
    create_demande,
    create_revision,
    get_demande,
    get_demande_history,
    list_demandes,
    update_demande_status,
)
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.demande import (
    DemandeCreate,
    DemandeHistory,
    DemandeRevision,
    DemandeStatusUpdate,
    DemandeVersionRead,
    DemandeWithCurrentVersion,
)
from src.api.services.demande import (
    ChasseurNotFoundForDemandeError,
    ClientNotFoundForDemandeError,
    DemandeAlreadyExistsError,
    DemandeNotFoundError,
    DemandeValidationError,
    MandatNotFoundForDemandeError,
)


def build_admin_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id_utilisateur=1,
        email="admin@example.com",
        role="ADMIN",
    )


def build_demande():
    return SimpleNamespace(
        id_demande=4,
        reference_demande="DEM-API-TEST",
        date_creation=datetime(
            2026,
            8,
            30,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        statut="ACTIVE",
        id_mandat=1,
    )


def build_version(
    numero_version: int = 1,
    active: bool = True,
) -> DemandeVersionRead:
    return DemandeVersionRead(
        id_demande_version=54,
        numero_version=numero_version,
        date_version=datetime(
            2026,
            8,
            30,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        motif_modification="API test",
        ville="Nantes",
        code_postal="44000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("300000"),
        budget_max=Decimal("410000"),
        surface_min=Decimal("70"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=[
            "balcon",
            "parking",
        ],
        active=active,
        id_demande=4,
        auteur_client_id=None,
        auteur_chasseur_id=4,
        auteur_systeme=False,
    )


def build_create_payload() -> DemandeCreate:
    return DemandeCreate(
        reference_demande="DEM-API-TEST",
        statut="ACTIVE",
        id_mandat=1,
        motif_modification="Initial creation",
        ville="Nantes",
        code_postal="44000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("300000"),
        budget_max=Decimal("410000"),
        surface_min=Decimal("70"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=[
            "balcon",
            "parking",
        ],
        auteur_chasseur_id=4,
    )


def build_revision_payload() -> DemandeRevision:
    return DemandeRevision(
        motif_modification="Updated criteria",
        ville="Nantes",
        code_postal="44000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("320000"),
        budget_max=Decimal("430000"),
        surface_min=Decimal("75"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=[
            "balcon",
            "parking",
        ],
        auteur_chasseur_id=4,
    )


def test_list_demandes_returns_all() -> None:
    db = MagicMock()
    service = MagicMock()
    service.list_demandes.return_value = [
        build_demande()
    ]

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        result = list_demandes(
            db=db,
            current_user=build_admin_user(),
        )

    assert len(result) == 1
    assert result[0].id_demande == 4

    service.list_demandes.assert_called_once()


def test_get_demande_success() -> None:
    db = MagicMock()
    service = MagicMock()

    service.get_demande.return_value = build_demande()
    service.get_current_version.return_value = (
        build_version()
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        result = get_demande(
            demande_id=4,
            db=db,
            current_user=build_admin_user(),
        )

    assert isinstance(
        result,
        DemandeWithCurrentVersion,
    )
    assert result.id_demande == 4
    assert result.reference_demande == "DEM-API-TEST"
    assert result.current_version.numero_version == 1

    service.get_demande.assert_called_once_with(4)
    service.get_current_version.assert_called_once_with(4)


def test_get_demande_returns_404_when_missing() -> None:
    db = MagicMock()
    service = MagicMock()

    service.get_demande.side_effect = (
        DemandeNotFoundError(
            "Demande 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            get_demande(
                demande_id=999,
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Demande 999 not found"
    )


def test_get_demande_returns_409_when_no_active_version() -> None:
    db = MagicMock()
    service = MagicMock()

    service.get_demande.return_value = build_demande()
    service.get_current_version.side_effect = (
        DemandeValidationError(
            "Demande 4 has no active version"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            get_demande(
                demande_id=4,
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 409
    assert exc.value.detail == (
        "Demande 4 has no active version"
    )


def test_get_demande_history_success() -> None:
    db = MagicMock()
    service = MagicMock()

    version_1 = build_version(
        numero_version=1,
        active=False,
    )
    version_2 = build_version(
        numero_version=2,
        active=True,
    )

    service.get_history.return_value = (
        build_demande(),
        [
            version_1,
            version_2,
        ],
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        result = get_demande_history(
            demande_id=4,
            db=db,
            current_user=build_admin_user(),
        )

    assert isinstance(
        result,
        DemandeHistory,
    )
    assert result.id_demande == 4
    assert len(result.versions) == 2
    assert result.versions[0].numero_version == 1
    assert result.versions[1].numero_version == 2

    service.get_history.assert_called_once_with(4)


def test_get_demande_history_returns_404() -> None:
    db = MagicMock()
    service = MagicMock()

    service.get_history.side_effect = (
        DemandeNotFoundError(
            "Demande 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            get_demande_history(
                demande_id=999,
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Demande 999 not found"
    )


def test_create_demande_success() -> None:
    db = MagicMock()
    service = MagicMock()

    demande = build_demande()
    version = build_version()

    service.create_demande.return_value = (
        demande,
        version,
    )

    payload = build_create_payload()

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        result = create_demande(
            payload=payload,
            db=db,
            current_user=build_admin_user(),
        )

    assert isinstance(
        result,
        DemandeWithCurrentVersion,
    )
    assert result.id_demande == 4
    assert result.current_version.id_demande_version == 54

    service.create_demande.assert_called_once_with(
        payload
    )


def test_create_demande_returns_409_for_duplicate() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_demande.side_effect = (
        DemandeAlreadyExistsError(
            "Demande already exists"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande(
                payload=build_create_payload(),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 409
    assert exc.value.detail == (
        "Demande already exists"
    )


def test_create_demande_returns_404_for_missing_mandat() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_demande.side_effect = (
        MandatNotFoundForDemandeError(
            "Mandat 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande(
                payload=build_create_payload(),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Mandat 999 not found"
    )


def test_create_demande_returns_404_for_missing_client() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_demande.side_effect = (
        ClientNotFoundForDemandeError(
            "Client 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande(
                payload=build_create_payload(),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404


def test_create_demande_returns_404_for_missing_chasseur() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_demande.side_effect = (
        ChasseurNotFoundForDemandeError(
            "Chasseur 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande(
                payload=build_create_payload(),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404


def test_create_demande_returns_422_for_validation_error() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_demande.side_effect = (
        DemandeValidationError(
            "Database constraint violation"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande(
                payload=build_create_payload(),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 422
    assert exc.value.detail == (
        "Database constraint violation"
    )


def test_create_revision_success() -> None:
    db = MagicMock()
    service = MagicMock()

    version = build_version(
        numero_version=2,
        active=True,
    )

    service.create_revision.return_value = version

    payload = build_revision_payload()

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        result = create_revision(
            demande_id=4,
            payload=payload,
            db=db,
            current_user=build_admin_user(),
        )

    assert result is version
    assert result.numero_version == 2
    assert result.active is True

    service.create_revision.assert_called_once_with(
        4,
        payload,
    )


def test_create_revision_returns_404_for_missing_demande() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_revision.side_effect = (
        DemandeNotFoundError(
            "Demande 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_revision(
                demande_id=999,
                payload=build_revision_payload(),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404


def test_create_revision_returns_404_for_missing_client() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_revision.side_effect = (
        ClientNotFoundForDemandeError(
            "Client 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_revision(
                demande_id=4,
                payload=build_revision_payload(),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404


def test_create_revision_returns_404_for_missing_chasseur() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_revision.side_effect = (
        ChasseurNotFoundForDemandeError(
            "Chasseur 999 not found"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_revision(
                demande_id=4,
                payload=build_revision_payload(),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404


def test_create_revision_returns_422_for_validation_error() -> None:
    db = MagicMock()
    service = MagicMock()

    service.create_revision.side_effect = (
        DemandeValidationError(
            "Revision violates constraint"
        )
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_revision(
                demande_id=4,
                payload=build_revision_payload(),
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 422
    assert exc.value.detail == (
        "Revision violates constraint"
    )


def test_update_demande_status_success() -> None:
    db = MagicMock()
    service = MagicMock()

    demande = build_demande()
    demande.statut = "SUSPENDUE"

    service.update_status.return_value = demande

    payload = DemandeStatusUpdate(
        statut="SUSPENDUE"
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        result = update_demande_status(
            demande_id=4,
            payload=payload,
            db=db,
            current_user=build_admin_user(),
        )

    assert result.statut == "SUSPENDUE"

    service.update_status.assert_called_once_with(
        4,
        payload,
    )


def test_update_demande_status_returns_404() -> None:
    db = MagicMock()
    service = MagicMock()

    service.update_status.side_effect = (
        DemandeNotFoundError(
            "Demande 999 not found"
        )
    )

    payload = DemandeStatusUpdate(
        statut="SUSPENDUE"
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            update_demande_status(
                demande_id=999,
                payload=payload,
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Demande 999 not found"
    )


def test_update_demande_status_returns_422() -> None:
    db = MagicMock()
    service = MagicMock()

    service.update_status.side_effect = (
        DemandeValidationError(
            "Status update violates constraint"
        )
    )

    payload = DemandeStatusUpdate(
        statut="SUSPENDUE"
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            update_demande_status(
                demande_id=4,
                payload=payload,
                db=db,
                current_user=build_admin_user(),
            )

    assert exc.value.status_code == 422
    assert exc.value.detail == (
        "Status update violates constraint"
    )