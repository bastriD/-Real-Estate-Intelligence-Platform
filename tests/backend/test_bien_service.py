from unittest.mock import MagicMock

import pytest

from src.api.db.models.bien import Bien
from src.api.services.bien import (
    BienNotFoundError,
    BienService,
)


def build_bien() -> Bien:
    return Bien(
        id_bien=13,
        reference_externe="BIEN-TEST-13",
        titre="Appartement centre-ville",
        description="Bien de test",
        type_bien="APPARTEMENT",
        prix=350000,
        surface=75,
        nb_pieces=3,
        nb_chambres=2,
        dpe="D",
        ville="Annecy",
        code_postal="74000",
        statut="DISPONIBLE",
    )


def test_list_biens_returns_all() -> None:
    db = MagicMock()

    service = BienService(db)
    service.repository.list_all = MagicMock(
        return_value=[build_bien()]
    )

    result = service.list_biens()

    assert len(result) == 1
    assert result[0].id_bien == 13

    service.repository.list_all.assert_called_once()


def test_list_biens_by_ville() -> None:
    db = MagicMock()

    service = BienService(db)
    service.repository.list_by_ville = MagicMock(
        return_value=[build_bien()]
    )

    result = service.list_biens(
        ville="Annecy"
    )

    assert len(result) == 1

    service.repository.list_by_ville.assert_called_once_with(
        "Annecy"
    )


def test_list_biens_by_statut() -> None:
    db = MagicMock()

    service = BienService(db)
    service.repository.list_by_statut = MagicMock(
        return_value=[build_bien()]
    )

    result = service.list_biens(
        statut="DISPONIBLE"
    )

    assert len(result) == 1

    service.repository.list_by_statut.assert_called_once_with(
        "DISPONIBLE"
    )


def test_list_biens_by_type() -> None:
    db = MagicMock()

    service = BienService(db)
    service.repository.list_by_type = MagicMock(
        return_value=[build_bien()]
    )

    result = service.list_biens(
        type_bien="APPARTEMENT"
    )

    assert len(result) == 1

    service.repository.list_by_type.assert_called_once_with(
        "APPARTEMENT"
    )


def test_ville_filter_has_priority() -> None:
    db = MagicMock()

    service = BienService(db)

    service.repository.list_by_ville = MagicMock(
        return_value=[build_bien()]
    )
    service.repository.list_by_statut = MagicMock()
    service.repository.list_by_type = MagicMock()

    result = service.list_biens(
        ville="Annecy",
        statut="DISPONIBLE",
        type_bien="APPARTEMENT",
    )

    assert len(result) == 1

    service.repository.list_by_ville.assert_called_once_with(
        "Annecy"
    )
    service.repository.list_by_statut.assert_not_called()
    service.repository.list_by_type.assert_not_called()


def test_statut_filter_has_priority_over_type() -> None:
    db = MagicMock()

    service = BienService(db)

    service.repository.list_by_statut = MagicMock(
        return_value=[build_bien()]
    )
    service.repository.list_by_type = MagicMock()

    result = service.list_biens(
        statut="DISPONIBLE",
        type_bien="APPARTEMENT",
    )

    assert len(result) == 1

    service.repository.list_by_statut.assert_called_once_with(
        "DISPONIBLE"
    )
    service.repository.list_by_type.assert_not_called()


def test_get_bien_returns_existing_bien() -> None:
    db = MagicMock()
    bien = build_bien()

    service = BienService(db)
    service.repository.get_by_id = MagicMock(
        return_value=bien
    )

    result = service.get_bien(13)

    assert result is bien

    service.repository.get_by_id.assert_called_once_with(
        13
    )


def test_get_bien_raises_when_missing() -> None:
    db = MagicMock()

    service = BienService(db)
    service.repository.get_by_id = MagicMock(
        return_value=None
    )

    with pytest.raises(BienNotFoundError):
        service.get_bien(999)