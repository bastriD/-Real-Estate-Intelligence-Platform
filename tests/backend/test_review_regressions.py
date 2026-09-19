from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy.engine import make_url

from src.api.core.config import Settings
from src.api.db.models.demande import Demande
from src.api.schemas.demande import DemandeCreate, DemandeRead
from src.api.services.demande import DemandeService, MandatNotFoundForDemandeError


def test_create_pre_mandate_request_does_not_lookup_a_null_mandate():
    db = MagicMock()
    db.scalar.return_value = 1

    service = DemandeService(db)
    service.repository = MagicMock()
    service.repository.create_demande.side_effect = lambda demande: demande

    payload = DemandeCreate(
        id_client=1,
        motif_modification="Initial request",
        auteur_systeme=True,
    )

    demande, _ = service.create_demande(payload)

    assert demande.id_mandat is None

    # One scalar lookup is expected for client ownership validation.
    # No second lookup must occur for a NULL mandate.
    assert db.scalar.call_count == 1

    db.commit.assert_called_once()


def test_explicit_unknown_mandate_still_rejected():
    db = MagicMock()

    # First scalar: client exists.
    # Second scalar: explicit mandate 999 does not exist.
    db.scalar.side_effect = [1, None]

    payload = DemandeCreate(
        id_client=1,
        id_mandat=999,
        motif_modification="Initial request",
        auteur_systeme=True,
    )

    with pytest.raises(MandatNotFoundForDemandeError):
        DemandeService(db).create_demande(payload)

    assert db.scalar.call_count == 2

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
