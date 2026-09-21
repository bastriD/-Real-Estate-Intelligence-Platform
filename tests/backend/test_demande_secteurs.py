from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError

from src.api.db.models.demande import Demande, DemandeVersion
from src.api.db.models.demande_version_secteur import DemandeVersionSecteur
from src.api.repositories.demande import DemandeRepository
from src.api.schemas.demande import DemandeCreate, DemandeRevision, DemandeVersionRead
from src.api.services.demande import DemandeService, DemandeValidationError


def payload(**overrides):
    return dict(motif_modification="Search update", auteur_systeme=True,
        ville="Montpellier", secteur_ids=[1, 3], criteres_souhaites=["terrasse ou jardin"]) | overrides


def service_setup():
    db = MagicMock()
    service = DemandeService(db)
    service._ensure_client_exists = MagicMock()
    service._validate_author = MagicMock()
    service.repository = MagicMock()
    service.repository.get_by_reference.return_value = None
    service.repository.create_demande.return_value = Demande(id_demande=10, id_client=2)
    service.repository.create_version.side_effect = lambda version: version
    service.repository.get_current_version.return_value = DemandeVersion(
        id_demande_version=7, id_demande=10, numero_version=1, active=True,
        secteur_links=[DemandeVersionSecteur(id_secteur=8)])
    db.scalars.return_value.all.return_value = [
        SimpleNamespace(id_secteur=value, ville="Montpellier") for value in [1, 3]]
    return service, db


@pytest.mark.parametrize("values", [[1, 1], [0], [-2], list(range(1, 102))])
def test_invalid_sector_identifiers_rejected(values):
    with pytest.raises(ValidationError):
        DemandeRevision(**payload(secteur_ids=values))


def test_create_persists_alternative_sectors_with_version():
    service, db = service_setup()
    _, version = service.create_demande(DemandeCreate(id_client=2, **payload()))
    assert version.secteur_ids == [1, 3]
    assert version.criteres_souhaites == ["terrasse ou jardin"]
    assert version.numero_version == 1
    db.commit.assert_called_once()


@pytest.mark.parametrize("values", [[1, 3], []])
def test_revision_replaces_sectors_without_mutating_history(values):
    service, db = service_setup()
    previous = service.repository.get_current_version.return_value
    current = service.create_revision(10, DemandeRevision(**payload(secteur_ids=values)))
    assert current.secteur_ids == values
    assert previous.secteur_ids == [8]
    assert current.numero_version == 2 and previous.active is False
    db.commit.assert_called_once()


@pytest.mark.parametrize("rows", [[], [SimpleNamespace(id_secteur=1, ville="Montpellier")],
    [SimpleNamespace(id_secteur=1, ville="Lyon"), SimpleNamespace(id_secteur=3, ville="Montpellier")]])
def test_unknown_inactive_or_cross_city_sectors_rejected_before_revision(rows):
    service, db = service_setup()
    db.scalars.return_value.all.return_value = rows
    with pytest.raises(DemandeValidationError):
        service.create_revision(10, DemandeRevision(**payload()))
    assert service.repository.get_current_version.return_value.active is True
    service.repository.create_version.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize("operation", ["create", "revise"])
@pytest.mark.parametrize("error", [RuntimeError("storage unavailable"), IntegrityError("insert", {}, Exception())])
def test_link_storage_failure_rolls_back_parent_and_version(operation, error):
    service, db = service_setup()
    service.repository.create_version.side_effect = error
    with pytest.raises((RuntimeError, DemandeValidationError)):
        if operation == "create":
            service.create_demande(DemandeCreate(id_client=2, **payload()))
        else:
            service.create_revision(10, DemandeRevision(**payload()))
    db.rollback.assert_called_once()
    db.commit.assert_not_called()


def test_read_schema_exposes_sectors_and_original_source():
    version = DemandeVersion(id_demande_version=1, id_demande=2, numero_version=1,
        date_version=datetime.now(timezone.utc), motif_modification="Imported", active=True,
        auteur_systeme=True, auteur_client_id=None, auteur_chasseur_id=None,
        description_recherche_legacy="T3 Ecusson ou Beaux-Arts", criteres_souhaites=[],
        secteur_links=[DemandeVersionSecteur(id_secteur=1), DemandeVersionSecteur(id_secteur=3)])
    result = DemandeVersionRead.model_validate(version)
    assert result.secteur_ids == [1, 3]
    assert result.description_recherche_legacy == version.description_recherche_legacy


def test_repository_eager_loads_versioned_sectors_without_joining_lock():
    db = MagicMock()
    repo = DemandeRepository(db)
    repo.get_current_version(2, for_update=True)
    statement = db.scalar.call_args.args[0]
    query = str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
    assert "FOR UPDATE" in query and "JOIN" not in query
    assert len(statement._with_options) == 1
    repo.list_versions(2)
    assert len(db.scalars.call_args.args[0]._with_options) == 1
