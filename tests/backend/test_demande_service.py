from unittest.mock import MagicMock

import pytest

from src.api.db.models.demande import Demande, DemandeVersion
from src.api.schemas.demande import (
    DemandeCreate,
    DemandeRevision,
    DemandeStatusUpdate,
)
from src.api.services.demande import (
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

    service = DemandeService(db)
    service.repository.get_by_reference = MagicMock(
        return_value=build_demande()
    )

    payload = DemandeCreate(
        reference_demande="LEGACY-DEMANDE-4",
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