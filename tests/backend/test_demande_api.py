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

def build_client_user(
    id_client: int | None = 4,
) -> AuthenticatedUser:
    return AuthenticatedUser(
        id_utilisateur=20,
        email="client@example.com",
        role="CLIENT",
        id_client=id_client,
    )

def build_demande(
    id_client: int | None = 4,
):
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
        id_client=id_client,
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
        id_client=4,
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

def test_client_can_create_own_demande() -> None:
    db = MagicMock()
    service = MagicMock()

    payload = DemandeCreate(
        reference_demande="CLIENT-DEM-001",
        statut="ACTIVE",
        id_client=4,
        id_mandat=None,
        motif_modification="Created by client",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("250000"),
        budget_max=Decimal("350000"),
        surface_min=Decimal("60"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        auteur_client_id=4,
    )

    demande = build_demande(id_client=4)
    demande.id_mandat = None

    version = DemandeVersionRead(
        id_demande_version=100,
        numero_version=1,
        date_version=datetime(
            2026,
            9,
            19,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        motif_modification="Created by client",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("250000"),
        budget_max=Decimal("350000"),
        surface_min=Decimal("60"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        active=True,
        id_demande=4,
        auteur_client_id=4,
        auteur_chasseur_id=None,
        auteur_systeme=False,
    )

    service.create_demande.return_value = (
        demande,
        version,
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        result = create_demande(
            payload=payload,
            db=db,
            current_user=build_client_user(4),
        )

    assert result.id_demande == 4
    assert result.id_client == 4
    assert result.current_version.auteur_client_id == 4

    service.create_demande.assert_called_once_with(payload)

def test_client_cannot_create_demande_for_other_client() -> None:
    db = MagicMock()
    service = MagicMock()

    payload = DemandeCreate(
        reference_demande="CLIENT-FORGED-OWNER",
        statut="ACTIVE",
        id_client=5,
        id_mandat=None,
        motif_modification="Attempted forged ownership",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("250000"),
        budget_max=Decimal("350000"),
        surface_min=Decimal("60"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        auteur_client_id=4,
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande(
                payload=payload,
                db=db,
                # Authenticated identity is client 4,
                # but payload attempts ownership by client 5.
                current_user=build_client_user(4),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"

    service.create_demande.assert_not_called()

def test_client_cannot_create_demande_with_other_client_as_author() -> None:
    db = MagicMock()
    service = MagicMock()

    payload = DemandeCreate(
        reference_demande="CLIENT-FORGED-AUTHOR",
        statut="ACTIVE",
        id_client=4,
        id_mandat=None,
        motif_modification="Attempted forged authorship",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("250000"),
        budget_max=Decimal("350000"),
        surface_min=Decimal("60"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        # Owner is correctly client 4,
        # but authorship is forged as client 5.
        auteur_client_id=5,
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande(
                payload=payload,
                db=db,
                current_user=build_client_user(4),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"

    service.create_demande.assert_not_called()

def test_client_can_create_revision_for_own_demande() -> None:
    db = MagicMock()
    service = MagicMock()
    affectation_service = MagicMock()

    payload = DemandeRevision(
        motif_modification="Updated by client",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("260000"),
        budget_max=Decimal("360000"),
        surface_min=Decimal("65"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon", "parking"],
        auteur_client_id=4,
    )

    service.get_demande.return_value = build_demande(
        id_client=4
    )

    version = DemandeVersionRead(
        id_demande_version=101,
        numero_version=2,
        date_version=datetime(
            2026,
            9,
            19,
            12,
            30,
            tzinfo=timezone.utc,
        ),
        motif_modification="Updated by client",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("260000"),
        budget_max=Decimal("360000"),
        surface_min=Decimal("65"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon", "parking"],
        active=True,
        id_demande=4,
        auteur_client_id=4,
        auteur_chasseur_id=None,
        auteur_systeme=False,
    )

    service.create_revision.return_value = version

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        result = create_revision(
            demande_id=4,
            payload=payload,
            db=db,
            current_user=build_client_user(4),
        )

    assert result.id_demande_version == 101
    assert result.numero_version == 2
    assert result.auteur_client_id == 4

    service.create_revision.assert_called_once_with(
        4,
        payload,
    )

    affectation_service.hunter_can_access_demande.assert_not_called()

def test_client_cannot_create_revision_for_other_client_demande() -> None:
    db = MagicMock()
    service = MagicMock()
    affectation_service = MagicMock()

    payload = DemandeRevision(
        motif_modification="Unauthorized revision",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("260000"),
        budget_max=Decimal("360000"),
        surface_min=Decimal("65"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        auteur_client_id=5,
    )

    # Demand belongs to client 4.
    service.get_demande.return_value = build_demande(
        id_client=4
    )

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            create_revision(
                demande_id=4,
                payload=payload,
                db=db,
                current_user=build_client_user(5),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"

    service.create_revision.assert_not_called()
    affectation_service.hunter_can_access_demande.assert_not_called()

def test_client_cannot_create_revision_with_other_client_as_author() -> None:
    db = MagicMock()
    service = MagicMock()
    affectation_service = MagicMock()

    payload = DemandeRevision(
        motif_modification="Forged revision author",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("260000"),
        budget_max=Decimal("360000"),
        surface_min=Decimal("65"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        # Authenticated client will be 4.
        auteur_client_id=5,
    )

    # Client 4 legitimately owns the demand.
    service.get_demande.return_value = build_demande(
        id_client=4
    )

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            create_revision(
                demande_id=4,
                payload=payload,
                db=db,
                current_user=build_client_user(4),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"

    service.create_revision.assert_not_called()
    affectation_service.hunter_can_access_demande.assert_not_called()

def test_client_without_identity_cannot_create_demande() -> None:
    db = MagicMock()
    service = MagicMock()

    payload = DemandeCreate(
        reference_demande="CLIENT-NO-IDENTITY",
        statut="ACTIVE",
        id_client=4,
        id_mandat=None,
        motif_modification="Missing authenticated client identity",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=Decimal("250000"),
        budget_max=Decimal("350000"),
        surface_min=Decimal("60"),
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        auteur_client_id=4,
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=service,
    ):
        with pytest.raises(HTTPException) as exc:
            create_demande(
                payload=payload,
                db=db,
                current_user=build_client_user(None),
            )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Client identity is not available"

    service.create_demande.assert_not_called()