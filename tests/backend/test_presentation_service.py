from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.db.models.presentation import Presentation
from src.api.schemas.presentation import (
    PresentationCreate,
    PresentationUpdate,
)
from src.api.services.presentation import (
    BienNotFoundForPresentationError,
    DemandeVersionNotFoundForPresentationError,
    PresentationAlreadyExistsError,
    PresentationDeleteConflictError,
    PresentationNotFoundError,
    PresentationService,
    PresentationValidationError,
)


def build_presentation() -> Presentation:
    return Presentation(
        id_presentation=19,
        id_demande_version=54,
        id_bien=13,
        score_matching=91.25,
        statut="PRESENTE",
        date_presentation=datetime(
            2026,
            8,
            30,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )


def test_list_presentations_returns_all() -> None:
    db = MagicMock()

    service = PresentationService(db)
    service.repository.list_all = MagicMock(
        return_value=[build_presentation()]
    )

    result = service.list_presentations()

    assert len(result) == 1
    assert result[0].id_presentation == 19

    service.repository.list_all.assert_called_once()


def test_list_presentations_by_demande_version() -> None:
    db = MagicMock()

    service = PresentationService(db)
    service.repository.list_by_demande_version = MagicMock(
        return_value=[build_presentation()]
    )

    result = service.list_presentations(
        demande_version_id=54
    )

    assert len(result) == 1

    service.repository.list_by_demande_version.assert_called_once_with(
        54
    )


def test_list_presentations_by_bien() -> None:
    db = MagicMock()

    service = PresentationService(db)
    service.repository.list_by_bien = MagicMock(
        return_value=[build_presentation()]
    )

    result = service.list_presentations(
        bien_id=13
    )

    assert len(result) == 1

    service.repository.list_by_bien.assert_called_once_with(
        13
    )


def test_get_presentation_returns_existing() -> None:
    db = MagicMock()
    presentation = build_presentation()

    service = PresentationService(db)
    service.repository.get_by_id = MagicMock(
        return_value=presentation
    )

    result = service.get_presentation(19)

    assert result is presentation

    service.repository.get_by_id.assert_called_once_with(
        19
    )


def test_get_presentation_raises_when_missing() -> None:
    db = MagicMock()

    service = PresentationService(db)
    service.repository.get_by_id = MagicMock(
        return_value=None
    )

    with pytest.raises(
        PresentationNotFoundError
    ):
        service.get_presentation(999)


def test_create_rejects_missing_demande_version() -> None:
    db = MagicMock()
    db.scalar.return_value = None

    service = PresentationService(db)

    payload = PresentationCreate(
        id_demande_version=999,
        id_bien=13,
        score_matching=91.25,
        statut="PRESENTE",
        date_presentation=datetime(
            2026,
            8,
            30,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(
        DemandeVersionNotFoundForPresentationError
    ):
        service.create_presentation(payload)


def test_create_rejects_missing_bien() -> None:
    db = MagicMock()

    db.scalar.return_value = 54

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    db.execute.return_value = execute_result

    service = PresentationService(db)

    payload = PresentationCreate(
        id_demande_version=54,
        id_bien=999,
        score_matching=91.25,
        statut="PRESENTE",
        date_presentation=datetime(
            2026,
            8,
            30,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(
        BienNotFoundForPresentationError
    ):
        service.create_presentation(payload)


def test_create_rejects_duplicate_presentation() -> None:
    db = MagicMock()

    db.scalar.return_value = 54

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = 1
    db.execute.return_value = execute_result

    service = PresentationService(db)

    service.repository.get_by_demande_and_bien = MagicMock(
        return_value=build_presentation()
    )

    payload = PresentationCreate(
        id_demande_version=54,
        id_bien=13,
        score_matching=91.25,
        statut="PRESENTE",
        date_presentation=datetime(
            2026,
            8,
            30,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(
        PresentationAlreadyExistsError
    ):
        service.create_presentation(payload)


def test_create_presentation_success() -> None:
    db = MagicMock()

    db.scalar.return_value = 54

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = 1
    db.execute.return_value = execute_result

    service = PresentationService(db)

    service.repository.get_by_demande_and_bien = MagicMock(
        return_value=None
    )

    created = build_presentation()

    service.repository.create = MagicMock(
        return_value=created
    )

    payload = PresentationCreate(
        id_demande_version=54,
        id_bien=13,
        score_matching=91.25,
        statut="PRESENTE",
        date_presentation=datetime(
            2026,
            8,
            30,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )

    result = service.create_presentation(payload)

    assert result is created
    assert result.id_demande_version == 54
    assert result.id_bien == 13
    assert result.score_matching == 91.25

    service.repository.create.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created)


def test_create_rolls_back_on_integrity_error() -> None:
    db = MagicMock()

    db.scalar.return_value = 54

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = 1
    db.execute.return_value = execute_result

    service = PresentationService(db)

    service.repository.get_by_demande_and_bien = MagicMock(
        return_value=None
    )

    service.repository.create = MagicMock(
        side_effect=IntegrityError(
            "statement",
            {},
            Exception("database constraint"),
        )
    )

    payload = PresentationCreate(
        id_demande_version=54,
        id_bien=13,
        score_matching=91.25,
        statut="PRESENTE",
        date_presentation=datetime(
            2026,
            8,
            30,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(
        PresentationValidationError
    ):
        service.create_presentation(payload)

    db.rollback.assert_called_once()


def test_update_presentation_success() -> None:
    db = MagicMock()
    presentation = build_presentation()

    service = PresentationService(db)
    service.repository.get_by_id = MagicMock(
        return_value=presentation
    )

    payload = PresentationUpdate(
        statut="RETENU",
        score_matching=95.0,
    )

    result = service.update_presentation(
        presentation_id=19,
        payload=payload,
    )

    assert result is presentation
    assert result.statut == "RETENU"
    assert result.score_matching == 95.0

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        presentation
    )


def test_update_rolls_back_on_integrity_error() -> None:
    db = MagicMock()
    presentation = build_presentation()

    service = PresentationService(db)
    service.repository.get_by_id = MagicMock(
        return_value=presentation
    )

    db.commit.side_effect = IntegrityError(
        "statement",
        {},
        Exception("database constraint"),
    )

    payload = PresentationUpdate(
        score_matching=95.0
    )

    with pytest.raises(
        PresentationValidationError
    ):
        service.update_presentation(
            presentation_id=19,
            payload=payload,
        )

    db.rollback.assert_called_once()


def test_delete_presentation_success() -> None:
    db = MagicMock()
    presentation = build_presentation()

    service = PresentationService(db)
    service.repository.get_by_id = MagicMock(
        return_value=presentation
    )
    service.repository.delete = MagicMock()

    service.delete_presentation(19)

    service.repository.delete.assert_called_once_with(
        presentation
    )
    db.commit.assert_called_once()


def test_delete_rolls_back_on_integrity_error() -> None:
    db = MagicMock()
    presentation = build_presentation()

    service = PresentationService(db)
    service.repository.get_by_id = MagicMock(
        return_value=presentation
    )

    service.repository.delete = MagicMock(
        side_effect=IntegrityError(
            "statement",
            {},
            Exception("foreign key constraint"),
        )
    )

    with pytest.raises(
        PresentationDeleteConflictError
    ):
        service.delete_presentation(19)

    db.rollback.assert_called_once()