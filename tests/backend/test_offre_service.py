from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.db.models.offre import Offre
from src.api.schemas.offre import (
    OffreCreate,
    OffreDecision,
    OffreRevision,
)
from src.api.services.offre import (
    OffreNotFoundError,
    OffreService,
    OffreTransitionError,
    OffreValidationError,
    PresentationNotFoundForOffreError,
)


def make_offre(
    *,
    id_offre: int = 10,
    id_presentation: int = 19,
    numero_version: int = 1,
    montant: Decimal = Decimal("250000.00"),
    statut: str = "SOUMISE",
    date_decision: datetime | None = None,
) -> Offre:
    return Offre(
        id_offre=id_offre,
        id_presentation=id_presentation,
        numero_version=numero_version,
        montant=montant,
        date_offre=datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        date_expiration=None,
        date_decision=date_decision,
        statut=statut,
        commentaire=None,
        date_creation=datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )


def make_service() -> tuple[
    OffreService,
    MagicMock,
]:
    session = MagicMock()

    service = OffreService(session)
    service.repository = MagicMock()
    service.audit = MagicMock()

    return service, session


def test_get_offre_returns_existing_offre() -> None:
    service, _ = make_service()
    offre = make_offre()

    service.repository.get_by_id.return_value = offre

    result = service.get_offre(10)

    assert result is offre

    service.repository.get_by_id.assert_called_once_with(
        10
    )


def test_get_offre_raises_when_missing() -> None:
    service, _ = make_service()

    service.repository.get_by_id.return_value = None

    with pytest.raises(OffreNotFoundError):
        service.get_offre(999)


def test_missing_presentation_is_rejected() -> None:
    service, _ = make_service()

    (
        service.repository
        .get_demande_id_for_presentation
        .return_value
    ) = None

    with pytest.raises(
        PresentationNotFoundForOffreError
    ):
        service.get_demande_id_for_presentation(
            999
        )


def test_create_offre_success() -> None:
    service, session = make_service()

    (
        service.repository
        .get_demande_id_for_presentation
        .return_value
    ) = 7

    (
        service.repository
        .get_latest_for_presentation
        .return_value
    ) = None

    created = make_offre()

    service.repository.create.return_value = created

    payload = OffreCreate(
        id_presentation=19,
        montant=Decimal("250000.00"),
        commentaire="Initial offer",
    )

    result = service.create_offre(
        payload,
        utilisateur="admin@example.com",
    )

    assert result is created
    assert result.numero_version == 1
    assert result.statut == "SOUMISE"

    service.repository.create.assert_called_once()

    created_argument = (
        service.repository
        .create
        .call_args
        .args[0]
    )

    assert created_argument.id_presentation == 19
    assert created_argument.numero_version == 1
    assert (
        created_argument.montant
        == Decimal("250000.00")
    )
    assert created_argument.statut == "SOUMISE"

    service.audit.log_change.assert_called_once()

    audit_kwargs = (
        service.audit
        .log_change
        .call_args
        .kwargs
    )

    assert audit_kwargs["table_name"] == "offre"
    assert audit_kwargs["operation"] == "INSERT"
    assert audit_kwargs["utilisateur"] == (
        "admin@example.com"
    )

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(
        created
    )


def test_create_offre_rejects_existing_history() -> None:
    service, session = make_service()

    (
        service.repository
        .get_demande_id_for_presentation
        .return_value
    ) = 7

    (
        service.repository
        .get_latest_for_presentation
        .return_value
    ) = make_offre()

    payload = OffreCreate(
        id_presentation=19,
        montant=Decimal("260000.00"),
    )

    with pytest.raises(OffreValidationError):
        service.create_offre(payload)

    service.repository.create.assert_not_called()
    session.commit.assert_not_called()


@pytest.mark.parametrize(
    "target_status",
    [
        "ACCEPTEE",
        "REFUSEE",
        "RETIREE",
    ],
)
def test_decide_offre_success(
    target_status: str,
) -> None:
    service, session = make_service()

    offre = make_offre()

    (
        service.repository
        .get_by_id_for_update
        .return_value
    ) = offre

    service.repository.save.return_value = offre

    payload = OffreDecision(
        statut=target_status,
        commentaire="Decision recorded",
    )

    result = service.decide_offre(
        10,
        payload,
        utilisateur="admin@example.com",
    )

    assert result is offre
    assert result.statut == target_status
    assert result.date_decision is not None
    assert (
        result.commentaire
        == "Decision recorded"
    )

    (
        service.repository
        .get_by_id_for_update
        .assert_called_once_with(10)
    )

    service.repository.save.assert_called_once_with(
        offre
    )

    audit_kwargs = (
        service.audit
        .log_change
        .call_args
        .kwargs
    )

    assert audit_kwargs["operation"] == "UPDATE"
    assert (
        audit_kwargs["ancienne_valeur"]["statut"]
        == "SOUMISE"
    )
    assert (
        audit_kwargs["nouvelle_valeur"]["statut"]
        == target_status
    )

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(
        offre
    )


def test_decide_offre_missing_raises_not_found() -> None:
    service, session = make_service()

    (
        service.repository
        .get_by_id_for_update
        .return_value
    ) = None

    payload = OffreDecision(
        statut="ACCEPTEE"
    )

    with pytest.raises(OffreNotFoundError):
        service.decide_offre(
            999,
            payload,
        )

    session.commit.assert_not_called()


@pytest.mark.parametrize(
    "current_status",
    [
        "ACCEPTEE",
        "REFUSEE",
        "RETIREE",
        "EXPIREE",
        "REVISEE",
    ],
)
def test_terminal_offre_cannot_be_decided(
    current_status: str,
) -> None:
    service, session = make_service()

    offre = make_offre(
        statut=current_status,
    )

    (
        service.repository
        .get_by_id_for_update
        .return_value
    ) = offre

    payload = OffreDecision(
        statut="REFUSEE"
    )

    with pytest.raises(OffreTransitionError):
        service.decide_offre(
            10,
            payload,
        )

    service.repository.save.assert_not_called()
    service.audit.log_change.assert_not_called()
    session.commit.assert_not_called()


def test_revision_creates_next_version() -> None:
    service, session = make_service()

    current = make_offre(
        id_offre=10,
        numero_version=1,
        montant=Decimal("250000.00"),
    )

    (
        service.repository
        .get_by_id_for_update
        .return_value
    ) = current

    (
        service.repository
        .get_latest_for_presentation
        .return_value
    ) = current

    service.repository.save.return_value = current

    def create_offre(offre: Offre) -> Offre:
        offre.id_offre = 11
        offre.date_offre = datetime(
            2026,
            9,
            20,
            13,
            0,
            tzinfo=timezone.utc,
        )
        offre.date_creation = datetime(
            2026,
            9,
            20,
            13,
            0,
            tzinfo=timezone.utc,
        )
        return offre

    service.repository.create.side_effect = (
        create_offre
    )

    payload = OffreRevision(
        montant=Decimal("245000.00"),
        commentaire="Revised amount",
    )

    result = service.revise_offre(
        10,
        payload,
        utilisateur="admin@example.com",
    )

    assert current.statut == "REVISEE"
    assert current.date_decision is not None

    assert result.id_offre == 11
    assert result.id_presentation == 19
    assert result.numero_version == 2
    assert (
        result.montant
        == Decimal("245000.00")
    )
    assert result.statut == "SOUMISE"
    assert result.date_decision is None

    (
        service.repository
        .get_latest_for_presentation
        .assert_called_once_with(
            19,
            for_update=True,
        )
    )

    service.repository.save.assert_called_once_with(
        current
    )
    service.repository.create.assert_called_once()

    assert service.audit.log_change.call_count == 2

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(
        result
    )


def test_only_latest_offre_can_be_revised() -> None:
    service, session = make_service()

    old_offre = make_offre(
        id_offre=10,
        numero_version=1,
    )

    latest = make_offre(
        id_offre=11,
        numero_version=2,
    )

    (
        service.repository
        .get_by_id_for_update
        .return_value
    ) = old_offre

    (
        service.repository
        .get_latest_for_presentation
        .return_value
    ) = latest

    payload = OffreRevision(
        montant=Decimal("245000.00"),
    )

    with pytest.raises(OffreTransitionError):
        service.revise_offre(
            10,
            payload,
        )

    service.repository.save.assert_not_called()
    service.repository.create.assert_not_called()
    service.audit.log_change.assert_not_called()
    session.commit.assert_not_called()


@pytest.mark.parametrize(
    "current_status",
    [
        "ACCEPTEE",
        "REFUSEE",
        "RETIREE",
        "EXPIREE",
        "REVISEE",
    ],
)
def test_terminal_offre_cannot_be_revised(
    current_status: str,
) -> None:
    service, session = make_service()

    current = make_offre(
        statut=current_status,
    )

    (
        service.repository
        .get_by_id_for_update
        .return_value
    ) = current

    (
        service.repository
        .get_latest_for_presentation
        .return_value
    ) = current

    payload = OffreRevision(
        montant=Decimal("245000.00"),
    )

    with pytest.raises(OffreTransitionError):
        service.revise_offre(
            10,
            payload,
        )

    service.repository.save.assert_not_called()
    service.repository.create.assert_not_called()
    session.commit.assert_not_called()


def test_create_integrity_error_rolls_back() -> None:
    service, session = make_service()

    (
        service.repository
        .get_demande_id_for_presentation
        .return_value
    ) = 7

    (
        service.repository
        .get_latest_for_presentation
        .return_value
    ) = None

    service.repository.create.side_effect = (
        IntegrityError(
            "insert",
            {},
            Exception("constraint"),
        )
    )

    payload = OffreCreate(
        id_presentation=19,
        montant=Decimal("250000.00"),
    )

    with pytest.raises(OffreValidationError):
        service.create_offre(payload)

    session.rollback.assert_called_once()
    session.commit.assert_not_called()


def test_revision_integrity_error_rolls_back() -> None:
    service, session = make_service()

    current = make_offre()

    (
        service.repository
        .get_by_id_for_update
        .return_value
    ) = current

    (
        service.repository
        .get_latest_for_presentation
        .return_value
    ) = current

    service.repository.save.return_value = current

    service.repository.create.side_effect = (
        IntegrityError(
            "insert",
            {},
            Exception("constraint"),
        )
    )

    payload = OffreRevision(
        montant=Decimal("245000.00"),
    )

    with pytest.raises(OffreValidationError):
        service.revise_offre(
            10,
            payload,
        )

    session.rollback.assert_called_once()
    session.commit.assert_not_called()