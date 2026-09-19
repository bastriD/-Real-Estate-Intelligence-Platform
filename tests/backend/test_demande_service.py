from unittest.mock import MagicMock

import pytest

from src.api.db.models.demande import Demande, DemandeVersion
from src.api.schemas.demande import (
    DemandeCreate,
    DemandeRevision,
    DemandeStatusUpdate,
)
from src.api.services.demande import (
    ClientNotFoundForDemandeError,
    DemandeAlreadyExistsError,
    DemandeNotFoundError,
    DemandeService,
    DemandeValidationError,
)


def build_demande() -> Demande:
    return Demande(
        id_demande=4,
        reference_demande="LEGACY-DEMANDE-4",
        statut="ACTIVE",
        id_client=4,
        id_mandat=4,
    )


def build_version(
    numero_version: int = 1,
    active: bool = True,
) -> DemandeVersion:
    return DemandeVersion(
        id_demande_version=53,
        numero_version=numero_version,
        motif_modification="Initial version",
        ville="Nantes",
        code_postal="44200",
        type_bien="APPARTEMENT",
        budget_min=300000,
        budget_max=390000,
        surface_min=70,
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        active=active,
        id_demande=4,
        auteur_client_id=None,
        auteur_chasseur_id=4,
        auteur_systeme=False,
    )


def test_get_demande_returns_existing_demande() -> None:
    db = MagicMock()

    demande = build_demande()

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=demande
    )

    result = service.get_demande(4)

    assert result is demande

    service.repository.get_by_id.assert_called_once_with(
        4
    )


def test_get_demande_raises_when_missing() -> None:
    db = MagicMock()

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=None
    )

    with pytest.raises(DemandeNotFoundError):
        service.get_demande(999)


def test_get_current_version_returns_active_version() -> None:
    db = MagicMock()

    demande = build_demande()
    version = build_version()

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=demande
    )
    service.repository.get_current_version = MagicMock(
        return_value=version
    )

    result = service.get_current_version(4)

    assert result is version
    assert result.active is True


def test_get_current_version_rejects_missing_active_version() -> None:
    db = MagicMock()

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=build_demande()
    )
    service.repository.get_current_version = MagicMock(
        return_value=None
    )

    with pytest.raises(DemandeValidationError):
        service.get_current_version(4)


def test_create_demande_rejects_duplicate_reference() -> None:
    db = MagicMock()

    # Client 4 exists.
    # Mandat 4 belongs to client 4.
    db.scalar.side_effect = [4, 4]

    service = DemandeService(db)
    service.repository.get_by_reference = MagicMock(
        return_value=build_demande()
    )

    payload = DemandeCreate(
        reference_demande="LEGACY-DEMANDE-4",
        id_client=4,
        id_mandat=4,
        motif_modification="Initial request",
        auteur_systeme=True,
        ville="Nantes",
        budget_min=300000,
        budget_max=390000,
    )

    with pytest.raises(DemandeAlreadyExistsError):
        service.create_demande(payload)


def test_create_revision_preserves_history_and_increments_version() -> None:
    db = MagicMock()

    current = build_version(
        numero_version=1,
        active=True,
    )

    service = DemandeService(db)

    service.repository.get_by_id = MagicMock(
        return_value=build_demande()
    )

    service.repository.get_current_version = MagicMock(
        return_value=current
    )

    created_version = build_version(
        numero_version=2,
        active=True,
    )
    created_version.id_demande_version = 54
    created_version.code_postal = "44000"
    created_version.budget_max = 410000

    service.repository.create_version = MagicMock(
        return_value=created_version
    )

    db.scalar.return_value = 4

    payload = DemandeRevision(
        motif_modification=(
            "Runtime validation of immutable versioning"
        ),
        ville="Nantes",
        code_postal="44000",
        type_bien="APPARTEMENT",
        budget_min=300000,
        budget_max=410000,
        surface_min=70,
        nb_pieces_min=3,
        nb_chambres_min=2,
        dpe_max="D",
        criteres_souhaites=[
            "balcon",
            "parking",
        ],
        auteur_chasseur_id=4,
    )

    result = service.create_revision(
        demande_id=4,
        payload=payload,
    )

    assert current.numero_version == 1
    assert current.active is False

    assert result.numero_version == 2
    assert result.active is True
    assert result.id_demande == 4

    service.repository.get_current_version.assert_called_once_with(
        4,
        for_update=True,
    )

    db.flush.assert_called_once()
    service.repository.create_version.assert_called_once()
    db.commit.assert_called_once()


def test_update_status_success() -> None:
    db = MagicMock()

    demande = build_demande()

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=demande
    )

    payload = DemandeStatusUpdate(
        statut="SUSPENDUE"
    )

    result = service.update_status(
        demande_id=4,
        payload=payload,
    )

    assert result.statut == "SUSPENDUE"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(demande)


def test_create_pre_mandat_demande_with_client_owner() -> None:
    db = MagicMock()

    # Client 4 exists.
    db.scalar.return_value = 4

    service = DemandeService(db)

    service.repository.get_by_reference = MagicMock(
        return_value=None
    )

    created_demande = Demande(
        id_demande=100,
        reference_demande="API-DEMANDE-100",
        statut="ACTIVE",
        id_client=4,
        id_mandat=None,
    )

    service.repository.create_demande = MagicMock(
        return_value=created_demande
    )

    created_version = DemandeVersion(
        id_demande_version=200,
        numero_version=1,
        motif_modification="Initial client request",
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=200000,
        budget_max=300000,
        surface_min=50,
        nb_pieces_min=2,
        nb_chambres_min=1,
        dpe_max="D",
        criteres_souhaites=["balcon"],
        active=True,
        id_demande=100,
        auteur_client_id=4,
        auteur_chasseur_id=None,
        auteur_systeme=False,
    )

    service.repository.create_version = MagicMock(
        return_value=created_version
    )

    payload = DemandeCreate(
        reference_demande="API-DEMANDE-100",
        id_client=4,
        id_mandat=None,
        motif_modification="Initial client request",
        auteur_client_id=4,
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_min=200000,
        budget_max=300000,
        surface_min=50,
        nb_pieces_min=2,
        nb_chambres_min=1,
        dpe_max="D",
        criteres_souhaites=["balcon"],
    )

    demande, version = service.create_demande(payload)

    assert demande.id_client == 4
    assert demande.id_mandat is None

    assert version.id_demande == 100
    assert version.auteur_client_id == 4
    assert version.auteur_chasseur_id is None
    assert version.auteur_systeme is False

    service.repository.create_demande.assert_called_once()
    service.repository.create_version.assert_called_once()
    db.commit.assert_called_once()


def test_create_demande_rejects_unknown_client() -> None:
    db = MagicMock()

    # Client 999 does not exist.
    db.scalar.return_value = None

    service = DemandeService(db)

    service.repository.create_demande = MagicMock()
    service.repository.create_version = MagicMock()

    payload = DemandeCreate(
        reference_demande="API-DEMANDE-UNKNOWN-CLIENT",
        id_client=999,
        id_mandat=None,
        motif_modification="Initial client request",
        auteur_client_id=999,
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_max=300000,
    )

    with pytest.raises(
        ClientNotFoundForDemandeError
    ):
        service.create_demande(payload)

    service.repository.create_demande.assert_not_called()
    service.repository.create_version.assert_not_called()
    db.commit.assert_not_called()

def test_create_demande_rejects_cross_client_mandat() -> None:
    db = MagicMock()

    # Client 4 exists.
    # Mandat 18 belongs to client 5.
    db.scalar.side_effect = [4, 5]

    service = DemandeService(db)

    service.repository.create_demande = MagicMock()
    service.repository.create_version = MagicMock()

    payload = DemandeCreate(
        reference_demande="API-DEMANDE-CROSS-CLIENT",
        id_client=4,
        id_mandat=18,
        motif_modification="Initial client request",
        auteur_client_id=4,
        ville="Montpellier",
        code_postal="34000",
        type_bien="APPARTEMENT",
        budget_max=300000,
    )

    with pytest.raises(
        DemandeValidationError,
        match="Demande client does not match mandat client",
    ):
        service.create_demande(payload)

    service.repository.create_demande.assert_not_called()
    service.repository.create_version.assert_not_called()
    db.commit.assert_not_called()

def test_link_mandat_to_pre_mandat_demande() -> None:
    db = MagicMock()

    demande = Demande(
        id_demande=100,
        reference_demande="API-DEMANDE-100",
        statut="ACTIVE",
        id_client=4,
        id_mandat=None,
    )

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=demande
    )

    # Mandat 18 belongs to client 4.
    db.scalar.return_value = 4

    result = service.link_mandat(
        demande_id=100,
        mandat_id=18,
    )

    assert result is demande
    assert result.id_client == 4
    assert result.id_mandat == 18

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(demande)

def test_link_mandat_rejects_cross_client_mandat() -> None:
    db = MagicMock()

    demande = Demande(
        id_demande=100,
        reference_demande="API-DEMANDE-100",
        statut="ACTIVE",
        id_client=4,
        id_mandat=None,
    )

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=demande
    )

    # Mandat 18 belongs to client 5,
    # while the demande belongs to client 4.
    db.scalar.return_value = 5

    with pytest.raises(
        DemandeValidationError,
        match="Demande client does not match mandat client",
    ):
        service.link_mandat(
            demande_id=100,
            mandat_id=18,
        )

    assert demande.id_mandat is None
    db.commit.assert_not_called()

def test_link_mandat_rejects_cross_client_mandat() -> None:
    db = MagicMock()

    demande = Demande(
        id_demande=100,
        reference_demande="API-DEMANDE-100",
        statut="ACTIVE",
        id_client=4,
        id_mandat=None,
    )

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=demande
    )

    # Mandat 18 belongs to client 5,
    # while the demande belongs to client 4.
    db.scalar.return_value = 5

    with pytest.raises(
        DemandeValidationError,
        match="Demande client does not match mandat client",
    ):
        service.link_mandat(
            demande_id=100,
            mandat_id=18,
        )

    assert demande.id_mandat is None
    db.commit.assert_not_called()

def test_link_mandat_rejects_ownerless_demande() -> None:
    db = MagicMock()

    demande = Demande(
        id_demande=200,
        reference_demande=None,
        statut="ACTIVE",
        id_client=None,
        id_mandat=None,
    )

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=demande
    )

    with pytest.raises(
        DemandeValidationError,
        match="Demande has no client owner",
    ):
        service.link_mandat(
            demande_id=200,
            mandat_id=18,
        )

    assert demande.id_mandat is None
    db.scalar.assert_not_called()
    db.commit.assert_not_called()

def test_link_same_mandat_is_idempotent() -> None:
    db = MagicMock()

    demande = Demande(
        id_demande=100,
        reference_demande="API-DEMANDE-100",
        statut="ACTIVE",
        id_client=4,
        id_mandat=18,
    )

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=demande
    )

    result = service.link_mandat(
        demande_id=100,
        mandat_id=18,
    )

    assert result is demande
    assert result.id_mandat == 18

    # No database mutation is necessary.
    db.scalar.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

def test_link_mandat_rejects_relink_to_different_mandat() -> None:
    db = MagicMock()

    demande = Demande(
        id_demande=100,
        reference_demande="API-DEMANDE-100",
        statut="ACTIVE",
        id_client=4,
        id_mandat=18,
    )

    service = DemandeService(db)
    service.repository.get_by_id = MagicMock(
        return_value=demande
    )

    with pytest.raises(
        DemandeValidationError,
        match="Demande is already linked to another mandat",
    ):
        service.link_mandat(
            demande_id=100,
            mandat_id=19,
        )

    assert demande.id_mandat == 18

    db.scalar.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()