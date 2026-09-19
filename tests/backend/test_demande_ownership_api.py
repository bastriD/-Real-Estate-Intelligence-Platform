from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.api.api.v1.endpoints.demandes import (
    create_revision,
    get_demande,
    get_demande_history,
    update_demande_status,
)
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.demande import (
    DemandeRevision,
    DemandeStatusUpdate,
    DemandeVersionRead,
)
from src.api.api.v1.endpoints.demandes import (
    create_revision,
    get_demande,
    get_demande_history,
    link_demande_mandat,
    update_demande_status,
)

from src.api.schemas.demande import (
    DemandeMandatLink,
    DemandeRevision,
    DemandeStatusUpdate,
    DemandeVersionRead,
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
        reference_demande="DEM-OWNERSHIP",
        date_creation=datetime(
            2026,
            9,
            11,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        statut="ACTIVE",
        id_client=id_client,
        id_mandat=None,
    )

def build_version() -> DemandeVersionRead:
    return DemandeVersionRead(
        id_demande_version=54,
        numero_version=1,
        date_version=datetime(
            2026,
            9,
            11,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        motif_modification="Ownership test",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=250000,
        budget_max=350000,
        surface_min=60,
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        active=True,
        id_demande=4,
        auteur_client_id=None,
        auteur_chasseur_id=4,
        auteur_systeme=False,
    )


def build_revision_payload() -> DemandeRevision:
    return DemandeRevision(
        motif_modification="Updated by hunter",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=260000,
        budget_max=360000,
        surface_min=65,
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon", "parking"],
        auteur_chasseur_id=4,
    )


def test_chasseur_can_get_assigned_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    demande_service.get_demande.return_value = build_demande()
    demande_service.get_current_version.return_value = build_version()
    affectation_service.hunter_can_access_demande.return_value = True

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        result = get_demande(
            demande_id=4,
            db=db,
            current_user=build_chasseur_user(4),
        )

    assert result.id_demande == 4

    affectation_service.hunter_can_access_demande.assert_called_once_with(
        demande_id=4,
        chasseur_id=4,
    )


def test_chasseur_cannot_get_other_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    affectation_service.hunter_can_access_demande.return_value = False

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            get_demande(
                demande_id=4,
                db=db,
                current_user=build_chasseur_user(5),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"

    demande_service.get_demande.assert_not_called()


def test_chasseur_without_identity_cannot_get_demande() -> None:
    db = MagicMock()

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService"
    ):
        with pytest.raises(HTTPException) as exc:
            get_demande(
                demande_id=4,
                db=db,
                current_user=build_chasseur_user(None),
            )

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Hunter identity is not available"
    )


def test_chasseur_can_read_assigned_demande_history() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    demande_service.get_history.return_value = (
        build_demande(),
        [build_version()],
    )
    affectation_service.hunter_can_access_demande.return_value = True

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        result = get_demande_history(
            demande_id=4,
            db=db,
            current_user=build_chasseur_user(4),
        )

    assert result.id_demande == 4
    assert len(result.versions) == 1


def test_chasseur_cannot_read_other_demande_history() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    affectation_service.hunter_can_access_demande.return_value = False

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            get_demande_history(
                demande_id=4,
                db=db,
                current_user=build_chasseur_user(5),
            )

    assert exc.value.status_code == 404

    demande_service.get_history.assert_not_called()


def test_chasseur_can_create_revision_for_assigned_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    payload = build_revision_payload()
    demande_service.create_revision.return_value = build_version()
    affectation_service.hunter_can_access_demande.return_value = True

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
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
            current_user=build_chasseur_user(4),
        )

    assert result.id_demande_version == 54

    demande_service.create_revision.assert_called_once_with(
        4,
        payload,
    )


def test_chasseur_cannot_create_revision_for_other_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    affectation_service.hunter_can_access_demande.return_value = False

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            create_revision(
                demande_id=4,
                payload=build_revision_payload(),
                db=db,
                current_user=build_chasseur_user(5),
            )

    assert exc.value.status_code == 404

    demande_service.create_revision.assert_not_called()


def test_chasseur_can_update_status_for_assigned_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    demande = build_demande()
    demande.statut = "SUSPENDUE"

    demande_service.update_status.return_value = demande
    affectation_service.hunter_can_access_demande.return_value = True

    payload = DemandeStatusUpdate(
        statut="SUSPENDUE"
    )

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        result = update_demande_status(
            demande_id=4,
            payload=payload,
            db=db,
            current_user=build_chasseur_user(4),
        )

    assert result.statut == "SUSPENDUE"


def test_chasseur_cannot_update_status_for_other_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    affectation_service.hunter_can_access_demande.return_value = False

    payload = DemandeStatusUpdate(
        statut="SUSPENDUE"
    )

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            update_demande_status(
                demande_id=4,
                payload=payload,
                db=db,
                current_user=build_chasseur_user(5),
            )

    assert exc.value.status_code == 404

    demande_service.update_status.assert_not_called()

def test_chasseur_list_is_scoped_to_accessible_demandes() -> None:
    db = MagicMock()
    demande_service = MagicMock()

    demande_service.list_demandes_for_chasseur.return_value = [
        build_demande()
    ]

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=demande_service,
    ):
        from src.api.api.v1.endpoints.demandes import list_demandes

        result = list_demandes(
            db=db,
            current_user=build_chasseur_user(4),
        )

    assert len(result) == 1
    assert result[0].id_demande == 4

    demande_service.list_demandes_for_chasseur.assert_called_once_with(
        4
    )
    demande_service.list_demandes.assert_not_called()


def test_chasseur_without_identity_cannot_list_demandes() -> None:
    db = MagicMock()

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService"
    ):
        from src.api.api.v1.endpoints.demandes import list_demandes

        with pytest.raises(HTTPException) as exc:
            list_demandes(
                db=db,
                current_user=build_chasseur_user(None),
            )

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Hunter identity is not available"
    )


def test_admin_list_remains_unrestricted() -> None:
    db = MagicMock()
    demande_service = MagicMock()

    demande_service.list_demandes.return_value = [
        build_demande()
    ]

    admin_user = AuthenticatedUser(
        id_utilisateur=1,
        email="admin@example.com",
        role="ADMIN",
    )

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=demande_service,
    ):
        from src.api.api.v1.endpoints.demandes import list_demandes

        result = list_demandes(
            db=db,
            current_user=admin_user,
        )

    assert len(result) == 1

    demande_service.list_demandes.assert_called_once()
    demande_service.list_demandes_for_chasseur.assert_not_called()

def test_client_can_get_own_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    demande_service.get_demande.return_value = build_demande(
        id_client=4
    )
    demande_service.get_current_version.return_value = build_version()

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        result = get_demande(
            demande_id=4,
            db=db,
            current_user=build_client_user(4),
        )

    assert result.id_demande == 4
    assert result.id_client == 4

    demande_service.get_demande.assert_called()
    affectation_service.hunter_can_access_demande.assert_not_called()

def test_client_cannot_get_other_client_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    # Demand belongs to client 4.
    demande_service.get_demande.return_value = build_demande(
        id_client=4
    )

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            get_demande(
                demande_id=4,
                db=db,
                # Authenticated client 5 attempts to access client 4's demand.
                current_user=build_client_user(5),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"

    demande_service.get_current_version.assert_not_called()
    affectation_service.hunter_can_access_demande.assert_not_called()

def test_client_can_read_own_demande_history() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    demande_service.get_demande.return_value = build_demande(
        id_client=4
    )
    demande_service.get_history.return_value = (
        build_demande(id_client=4),
        [build_version()],
    )

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        result = get_demande_history(
            demande_id=4,
            db=db,
            current_user=build_client_user(4),
        )

    assert result.id_demande == 4
    assert result.id_client == 4
    assert len(result.versions) == 1

    demande_service.get_history.assert_called_once_with(4)
    affectation_service.hunter_can_access_demande.assert_not_called()


def test_client_cannot_read_other_client_demande_history() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    # Demand 4 belongs to client 4.
    demande_service.get_demande.return_value = build_demande(
        id_client=4
    )

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            get_demande_history(
                demande_id=4,
                db=db,
                current_user=build_client_user(5),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"

    demande_service.get_history.assert_not_called()
    affectation_service.hunter_can_access_demande.assert_not_called()

def test_client_list_is_scoped_to_owned_demandes() -> None:
    db = MagicMock()
    demande_service = MagicMock()

    demande_service.list_demandes_for_client.return_value = [
        build_demande(id_client=4)
    ]

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=demande_service,
    ):
        from src.api.api.v1.endpoints.demandes import list_demandes

        result = list_demandes(
            db=db,
            current_user=build_client_user(4),
        )

    assert len(result) == 1
    assert result[0].id_demande == 4
    assert result[0].id_client == 4

    demande_service.list_demandes_for_client.assert_called_once_with(4)
    demande_service.list_demandes.assert_not_called()
    demande_service.list_demandes_for_chasseur.assert_not_called()

def test_client_without_identity_cannot_list_demandes() -> None:
    db = MagicMock()
    demande_service = MagicMock()

    with patch(
        "src.api.api.v1.endpoints.demandes.DemandeService",
        return_value=demande_service,
    ):
        from src.api.api.v1.endpoints.demandes import list_demandes

        with pytest.raises(HTTPException) as exc:
            list_demandes(
                db=db,
                current_user=build_client_user(None),
            )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Client identity is not available"

    demande_service.list_demandes.assert_not_called()
    demande_service.list_demandes_for_client.assert_not_called()
    demande_service.list_demandes_for_chasseur.assert_not_called()

def test_chasseur_can_link_mandat_for_assigned_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    demande = build_demande(id_client=4)
    demande.id_mandat = 18

    demande_service.link_mandat.return_value = demande
    affectation_service.hunter_can_access_demande.return_value = True

    payload = DemandeMandatLink(
        id_mandat=18,
    )

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        result = link_demande_mandat(
            demande_id=4,
            payload=payload,
            db=db,
            current_user=build_chasseur_user(4),
        )

    assert result.id_demande == 4
    assert result.id_mandat == 18
    assert result.id_client == 4

    affectation_service.hunter_can_access_demande.assert_called_once_with(
        demande_id=4,
        chasseur_id=4,
    )

    demande_service.link_mandat.assert_called_once_with(
        demande_id=4,
        mandat_id=18,
    )
def test_chasseur_cannot_link_mandat_for_other_demande() -> None:
    db = MagicMock()
    demande_service = MagicMock()
    affectation_service = MagicMock()

    affectation_service.hunter_can_access_demande.return_value = False

    payload = DemandeMandatLink(
        id_mandat=18,
    )

    with (
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeService",
            return_value=demande_service,
        ),
        patch(
            "src.api.api.v1.endpoints.demandes.DemandeAffectationService",
            return_value=affectation_service,
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            link_demande_mandat(
                demande_id=4,
                payload=payload,
                db=db,
                current_user=build_chasseur_user(5),
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Resource not found"

    affectation_service.hunter_can_access_demande.assert_called_once_with(
        demande_id=4,
        chasseur_id=5,
    )

    demande_service.link_mandat.assert_not_called()