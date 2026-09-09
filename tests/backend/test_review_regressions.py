from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy.engine import make_url

from src.api.core.config import Settings
from src.api.db.models.demande import Demande
from src.api.schemas.demande import DemandeCreate, DemandeRead
from src.api.services.demande import DemandeService, MandatNotFoundForDemandeError


def test_generated_pre_mandate_request_can_be_serialized():
    demande = Demande(
        id_demande=1, reference_demande="GENERATED-DEMANDE-1",
        date_creation=datetime.now(timezone.utc), statut="ACTIVE", id_mandat=None,
    )
    assert DemandeRead.model_validate(demande).id_mandat is None
    assert Demande.__table__.c.id_mandat.nullable


def test_create_pre_mandate_request_does_not_lookup_a_null_mandate():
    db = MagicMock()
    service = DemandeService(db)
    service.repository = MagicMock()
    service.repository.create_demande.side_effect = lambda demande: demande
    payload = DemandeCreate(motif_modification="Initial request", auteur_systeme=True)

    demande, _ = service.create_demande(payload)

    assert demande.id_mandat is None
    db.scalar.assert_not_called()
    db.commit.assert_called_once()


def test_explicit_unknown_mandate_still_rejected():
    db = MagicMock()
    db.scalar.return_value = None
    payload = DemandeCreate(
        id_mandat=999, motif_modification="Initial request", auteur_systeme=True,
    )
    with pytest.raises(MandatNotFoundForDemandeError):
        DemandeService(db).create_demande(payload)


def test_database_url_preserves_special_characters_in_credentials():
    settings = Settings(
        _env_file=None, postgres_user="review@user",
        postgres_password="test@password:/?#%", postgres_host="localhost",
        postgres_db="review", jwt_secret_key="test-only",
    )
    url = make_url(settings.database_url)
    assert url.username == "review@user"
    assert url.password == "test@password:/?#%"
    assert url.host == "localhost"
