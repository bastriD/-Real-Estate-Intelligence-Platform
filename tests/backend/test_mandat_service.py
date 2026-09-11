from datetime import date
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from src.api.db.models.mandat import Mandat
from src.api.db.models.mandat_periode import MandatPeriode
from src.api.schemas.mandat import (
    MandatCreate,
    MandatRenew,
    MandatUpdate,
)
from src.api.services.mandat import (
    ChasseurNotFoundForMandatError,
    ClientNotFoundForMandatError,
    MandatAlreadyExistsError,
    MandatNotFoundError,
    MandatService,
    MandatValidationError,
)


TEST_USER_EMAIL = "admin.auth.test@example.com"


def build_mandat() -> Mandat:
    return Mandat(
        id_mandat=36,
        reference_mandat="API-TEST-MANDAT",
        type_mandat="EXCLUSIF",
        date_signature=date(2026, 8, 30),
        mode_signature="ELECTRONIQUE",
        date_debut=date(2026, 8, 30),
        date_fin=date(2027, 2, 28),
        statut="ACTIF",
        commentaire=None,
        id_client=1,
        id_chasseur=1,
    )


def build_create_payload() -> MandatCreate:
    return MandatCreate(
        reference_mandat="API-TEST-MANDAT",
        type_mandat="EXCLUSIF",
        date_signature=date(2026, 8, 30),
        mode_signature="ELECTRONIQUE",
        date_debut=date(2026, 8, 30),
        date_fin=date(2027, 2, 28),
        statut="ACTIF",
        id_client=1,
        id_chasseur=1,
    )


def build_initial_period() -> MandatPeriode:
    return MandatPeriode(
        id_mandat_periode=100,
        id_mandat=36,
        numero_periode=1,
        type_periode="INITIAL",
        date_debut=date(2026, 8, 30),
        date_fin=date(2027, 2, 28),
        date_renouvellement=None,
        commentaire=None,
        est_historique_legacy=False,
    )


def test_get_mandat_returns_existing_mandat() -> None:
    db = MagicMock()
    mandat = build_mandat()

    service = MandatService(db)
    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    result = service.get_mandat(36)

    assert result is mandat

    service.repository.get_by_id.assert_called_once_with(
        36
    )


def test_get_mandat_raises_when_missing() -> None:
    db = MagicMock()

    service = MandatService(db)
    service.repository.get_by_id = MagicMock(
        return_value=None
    )

    with pytest.raises(MandatNotFoundError):
        service.get_mandat(999)


def test_list_by_client_validates_client() -> None:
    db = MagicMock()
    db.scalar.return_value = 1

    service = MandatService(db)
    service.repository.list_by_client = MagicMock(
        return_value=[build_mandat()]
    )

    result = service.list_by_client(1)

    assert len(result) == 1
    assert result[0].id_client == 1

    db.scalar.assert_called_once()

    service.repository.list_by_client.assert_called_once_with(
        1
    )


def test_list_by_client_rejects_missing_client() -> None:
    db = MagicMock()
    db.scalar.return_value = None

    service = MandatService(db)

    with pytest.raises(
        ClientNotFoundForMandatError
    ):
        service.list_by_client(999)


def test_list_by_chasseur_validates_chasseur() -> None:
    db = MagicMock()
    db.scalar.return_value = 1

    service = MandatService(db)
    service.repository.list_by_chasseur = MagicMock(
        return_value=[build_mandat()]
    )

    result = service.list_by_chasseur(1)

    assert len(result) == 1
    assert result[0].id_chasseur == 1

    db.scalar.assert_called_once()

    service.repository.list_by_chasseur.assert_called_once_with(
        1
    )


def test_list_by_chasseur_rejects_missing_chasseur() -> None:
    db = MagicMock()
    db.scalar.return_value = None

    service = MandatService(db)

    with pytest.raises(
        ChasseurNotFoundForMandatError
    ):
        service.list_by_chasseur(999)


def test_list_periods_returns_contractual_history() -> None:
    db = MagicMock()
    mandat = build_mandat()
    periode = build_initial_period()

    service = MandatService(db)

    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    service.repository.list_periods = MagicMock(
        return_value=[periode]
    )

    result = service.list_periods(36)

    assert result == [periode]

    service.repository.get_by_id.assert_called_once_with(
        36
    )

    service.repository.list_periods.assert_called_once_with(
        36
    )


def test_create_mandat_rejects_duplicate_reference() -> None:
    db = MagicMock()

    service = MandatService(db)

    service.repository.get_by_reference = MagicMock(
        return_value=build_mandat()
    )

    payload = build_create_payload()

    with pytest.raises(
        MandatAlreadyExistsError
    ):
        service.create_mandat(payload)


def test_create_mandat_success() -> None:
    db = MagicMock()

    service = MandatService(db)

    service.repository.get_by_reference = MagicMock(
        return_value=None
    )

    db.scalar.side_effect = [1, 1]

    created = build_mandat()

    service.repository.create = MagicMock(
        return_value=created
    )

    def create_period_side_effect(
        periode: MandatPeriode,
    ) -> MandatPeriode:
        periode.id_mandat_periode = 101
        return periode

    service.repository.create_period = MagicMock(
        side_effect=create_period_side_effect
    )

    service.audit.log_change = MagicMock()

    payload = build_create_payload()

    result = service.create_mandat(
        payload,
        utilisateur=TEST_USER_EMAIL,
    )

    assert result is created

    assert (
        result.reference_mandat
        == "API-TEST-MANDAT"
    )

    assert db.scalar.call_count == 2

    service.repository.create.assert_called_once()

    service.repository.create_period.assert_called_once()

    created_period = (
        service.repository
        .create_period
        .call_args
        .args[0]
    )

    assert created_period.id_mandat == 36
    assert created_period.numero_periode == 1
    assert created_period.type_periode == "INITIAL"

    assert (
        created_period.date_debut
        == date(2026, 8, 30)
    )

    assert (
        created_period.date_fin
        == date(2027, 2, 28)
    )

    assert created_period.date_renouvellement is None

    assert (
        created_period.est_historique_legacy
        is False
    )

    assert service.audit.log_change.call_count == 2

    first_audit_call = (
        service.audit.log_change.call_args_list[0]
    )

    assert (
        first_audit_call.kwargs["table_name"]
        == "mandat"
    )

    assert (
        first_audit_call.kwargs["operation"]
        == "INSERT"
    )

    assert (
        first_audit_call.kwargs["record_id"]
        == 36
    )

    assert (
        first_audit_call.kwargs["utilisateur"]
        == TEST_USER_EMAIL
    )

    assert (
        first_audit_call.kwargs["nouvelle_valeur"]
        == {
            "id_mandat": 36,
            "reference_mandat": "API-TEST-MANDAT",
            "type_mandat": "EXCLUSIF",
            "date_signature": "2026-08-30",
            "mode_signature": "ELECTRONIQUE",
            "date_debut": "2026-08-30",
            "date_fin": "2027-02-28",
            "statut": "ACTIF",
            "commentaire": None,
            "id_client": 1,
            "id_chasseur": 1,
        }
    )

    assert (
        first_audit_call.kwargs["contexte"]
        == {
            "source": "api",
            "action": "create_mandat",
        }
    )

    second_audit_call = (
        service.audit.log_change.call_args_list[1]
    )

    assert (
        second_audit_call.kwargs["table_name"]
        == "mandat_periode"
    )

    assert (
        second_audit_call.kwargs["operation"]
        == "INSERT"
    )

    assert (
        second_audit_call.kwargs["record_id"]
        == 101
    )

    assert (
        second_audit_call.kwargs["utilisateur"]
        == TEST_USER_EMAIL
    )

    assert (
        second_audit_call.kwargs["nouvelle_valeur"][
            "id_mandat"
        ]
        == 36
    )

    assert (
        second_audit_call.kwargs["nouvelle_valeur"][
            "numero_periode"
        ]
        == 1
    )

    assert (
        second_audit_call.kwargs["nouvelle_valeur"][
            "type_periode"
        ]
        == "INITIAL"
    )

    assert (
        second_audit_call.kwargs["nouvelle_valeur"][
            "date_debut"
        ]
        == "2026-08-30"
    )

    assert (
        second_audit_call.kwargs["nouvelle_valeur"][
            "date_fin"
        ]
        == "2027-02-28"
    )

    assert (
        second_audit_call.kwargs["contexte"]
        == {
            "source": "api",
            "action": (
                "create_initial_mandat_period"
            ),
            "id_mandat": 36,
        }
    )

    db.commit.assert_called_once()


def test_create_mandat_rejects_invalid_dates() -> None:
    with pytest.raises(
        ValidationError,
        match=(
            "date_fin must be greater than or equal "
            "to date_debut"
        ),
    ):
        MandatCreate(
            reference_mandat="INVALID-DATES",
            type_mandat="EXCLUSIF",
            date_signature=date(2026, 8, 30),
            mode_signature="ELECTRONIQUE",
            date_debut=date(2026, 12, 31),
            date_fin=date(2026, 8, 30),
            statut="ACTIF",
            id_client=1,
            id_chasseur=1,
        )


def test_create_mandat_rejects_period_not_six_months() -> None:
    db = MagicMock()

    service = MandatService(db)

    service.repository.get_by_reference = MagicMock(
        return_value=None
    )

    db.scalar.side_effect = [1, 1]

    payload = MandatCreate(
        reference_mandat="INVALID-DURATION",
        type_mandat="EXCLUSIF",
        date_signature=date(2026, 8, 30),
        mode_signature="ELECTRONIQUE",
        date_debut=date(2026, 8, 30),
        date_fin=date(2027, 2, 27),
        statut="ACTIF",
        id_client=1,
        id_chasseur=1,
    )

    with pytest.raises(
        MandatValidationError,
        match="exactly 6 calendar months",
    ):
        service.create_mandat(payload)


def test_create_mandat_requires_start_on_signature_date() -> None:
    db = MagicMock()

    service = MandatService(db)

    service.repository.get_by_reference = MagicMock(
        return_value=None
    )

    db.scalar.side_effect = [1, 1]

    payload = MandatCreate(
        reference_mandat="INVALID-START",
        type_mandat="EXCLUSIF",
        date_signature=date(2026, 8, 30),
        mode_signature="ELECTRONIQUE",
        date_debut=date(2026, 9, 1),
        date_fin=date(2027, 3, 1),
        statut="ACTIF",
        id_client=1,
        id_chasseur=1,
    )

    with pytest.raises(
        MandatValidationError,
        match="must start on its signature date",
    ):
        service.create_mandat(payload)


def test_update_mandat_success() -> None:
    db = MagicMock()
    mandat = build_mandat()

    service = MandatService(db)

    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    service.audit.log_change = MagicMock()

    payload = MandatUpdate(
        statut="SUSPENDU",
        commentaire="Runtime update validation",
    )

    result = service.update_mandat(
        mandat_id=36,
        payload=payload,
        utilisateur=TEST_USER_EMAIL,
    )

    assert result is mandat
    assert result.statut == "SUSPENDU"

    assert (
        result.commentaire
        == "Runtime update validation"
    )

    service.audit.log_change.assert_called_once_with(
        table_name="mandat",
        operation="UPDATE",
        record_id=36,
        utilisateur=TEST_USER_EMAIL,
        ancienne_valeur={
            "id_mandat": 36,
            "reference_mandat": "API-TEST-MANDAT",
            "type_mandat": "EXCLUSIF",
            "date_signature": "2026-08-30",
            "mode_signature": "ELECTRONIQUE",
            "date_debut": "2026-08-30",
            "date_fin": "2027-02-28",
            "statut": "ACTIF",
            "commentaire": None,
            "id_client": 1,
            "id_chasseur": 1,
        },
        nouvelle_valeur={
            "id_mandat": 36,
            "reference_mandat": "API-TEST-MANDAT",
            "type_mandat": "EXCLUSIF",
            "date_signature": "2026-08-30",
            "mode_signature": "ELECTRONIQUE",
            "date_debut": "2026-08-30",
            "date_fin": "2027-02-28",
            "statut": "SUSPENDU",
            "commentaire": (
                "Runtime update validation"
            ),
            "id_client": 1,
            "id_chasseur": 1,
        },
        contexte={
            "source": "api",
            "action": "update_mandat",
        },
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(mandat)


@pytest.mark.parametrize(
    "field_name,value",
    [
        (
            "date_signature",
            date(2026, 9, 1),
        ),
        (
            "date_debut",
            date(2026, 9, 1),
        ),
        (
            "date_fin",
            date(2027, 3, 1),
        ),
    ],
)
def test_update_rejects_contractual_lifecycle_fields(
    field_name: str,
    value: date,
) -> None:
    db = MagicMock()
    mandat = build_mandat()

    service = MandatService(db)

    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    payload = MandatUpdate(
        **{
            field_name: value,
        }
    )

    with pytest.raises(
        MandatValidationError,
        match=(
            "Contractual lifecycle fields "
            "cannot be modified"
        ),
    ):
        service.update_mandat(
            mandat_id=36,
            payload=payload,
        )


def test_update_rejects_duplicate_reference() -> None:
    db = MagicMock()

    mandat = build_mandat()

    other_mandat = build_mandat()
    other_mandat.id_mandat = 99
    other_mandat.reference_mandat = "OTHER-REF"

    service = MandatService(db)

    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    service.repository.get_by_reference = MagicMock(
        return_value=other_mandat
    )

    payload = MandatUpdate(
        reference_mandat="OTHER-REF"
    )

    with pytest.raises(
        MandatAlreadyExistsError
    ):
        service.update_mandat(
            mandat_id=36,
            payload=payload,
        )


def test_renew_mandat_success() -> None:
    db = MagicMock()

    mandat = build_mandat()
    previous_period = build_initial_period()

    service = MandatService(db)

    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    service.repository.get_latest_period = MagicMock(
        return_value=previous_period
    )

    def create_period_side_effect(
        periode: MandatPeriode,
    ) -> MandatPeriode:
        periode.id_mandat_periode = 101
        return periode

    service.repository.create_period = MagicMock(
        side_effect=create_period_side_effect
    )

    service.audit.log_change = MagicMock()

    payload = MandatRenew(
        date_renouvellement=date(2027, 2, 28),
        commentaire="Renewed with client approval",
    )

    renewed_mandat, new_period = (
        service.renew_mandat(
            mandat_id=36,
            payload=payload,
            utilisateur=TEST_USER_EMAIL,
        )
    )

    assert renewed_mandat is mandat

    assert new_period.id_mandat_periode == 101
    assert new_period.id_mandat == 36
    assert new_period.numero_periode == 2

    assert (
        new_period.type_periode
        == "RENOUVELLEMENT"
    )

    assert (
        new_period.date_debut
        == date(2027, 2, 28)
    )

    assert (
        new_period.date_fin
        == date(2027, 8, 28)
    )

    assert (
        new_period.date_renouvellement
        == date(2027, 2, 28)
    )

    assert (
        new_period.commentaire
        == "Renewed with client approval"
    )

    assert (
        new_period.est_historique_legacy
        is False
    )

    assert (
        mandat.date_debut
        == date(2027, 2, 28)
    )

    assert (
        mandat.date_fin
        == date(2027, 8, 28)
    )

    service.repository.get_latest_period.assert_called_once_with(
        36
    )

    service.repository.create_period.assert_called_once()

    assert service.audit.log_change.call_count == 2

    period_audit = (
        service.audit.log_change.call_args_list[0]
    )

    assert (
        period_audit.kwargs["table_name"]
        == "mandat_periode"
    )

    assert (
        period_audit.kwargs["operation"]
        == "INSERT"
    )

    assert (
        period_audit.kwargs["record_id"]
        == 101
    )

    assert (
        period_audit.kwargs["contexte"]
        == {
            "source": "api",
            "action": "renew_mandat",
            "id_mandat": 36,
        }
    )

    mandat_audit = (
        service.audit.log_change.call_args_list[1]
    )

    assert (
        mandat_audit.kwargs["table_name"]
        == "mandat"
    )

    assert (
        mandat_audit.kwargs["operation"]
        == "UPDATE"
    )

    assert (
        mandat_audit.kwargs["ancienne_valeur"][
            "date_debut"
        ]
        == "2026-08-30"
    )

    assert (
        mandat_audit.kwargs["ancienne_valeur"][
            "date_fin"
        ]
        == "2027-02-28"
    )

    assert (
        mandat_audit.kwargs["nouvelle_valeur"][
            "date_debut"
        ]
        == "2027-02-28"
    )

    assert (
        mandat_audit.kwargs["nouvelle_valeur"][
            "date_fin"
        ]
        == "2027-08-28"
    )

    assert (
        mandat_audit.kwargs["contexte"]
        == {
            "source": "api",
            "action": "renew_mandat",
            "numero_periode": 2,
        }
    )

    db.commit.assert_called_once()

    assert db.refresh.call_count == 2

    db.refresh.assert_any_call(
        mandat
    )

    db.refresh.assert_any_call(
        new_period
    )


def test_renew_mandat_rejects_missing_contractual_period() -> None:
    db = MagicMock()

    mandat = build_mandat()

    service = MandatService(db)

    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    service.repository.get_latest_period = MagicMock(
        return_value=None
    )

    payload = MandatRenew(
        date_renouvellement=date(2027, 2, 28)
    )

    with pytest.raises(
        MandatValidationError,
        match=(
            "has no contractual period to renew"
        ),
    ):
        service.renew_mandat(
            mandat_id=36,
            payload=payload,
        )


@pytest.mark.parametrize(
    "source_date,months,expected_date",
    [
        (
            date(2026, 8, 30),
            6,
            date(2027, 2, 28),
        ),
        (
            date(2026, 8, 31),
            6,
            date(2027, 2, 28),
        ),
        (
            date(2027, 8, 31),
            6,
            date(2028, 2, 29),
        ),
        (
            date(2026, 1, 31),
            1,
            date(2026, 2, 28),
        ),
        (
            date(2028, 1, 31),
            1,
            date(2028, 2, 29),
        ),
    ],
)
def test_add_calendar_months(
    source_date: date,
    months: int,
    expected_date: date,
) -> None:
    assert (
        MandatService._add_calendar_months(
            source_date,
            months,
        )
        == expected_date
    )


def test_delete_mandat_success() -> None:
    db = MagicMock()
    mandat = build_mandat()

    service = MandatService(db)

    service.repository.get_by_id = MagicMock(
        return_value=mandat
    )

    service.repository.delete = MagicMock()
    service.audit.log_change = MagicMock()

    service.delete_mandat(
        36,
        utilisateur=TEST_USER_EMAIL,
    )

    service.repository.delete.assert_called_once_with(
        mandat
    )

    service.audit.log_change.assert_called_once_with(
        table_name="mandat",
        operation="DELETE",
        record_id=36,
        utilisateur=TEST_USER_EMAIL,
        ancienne_valeur={
            "id_mandat": 36,
            "reference_mandat": "API-TEST-MANDAT",
            "type_mandat": "EXCLUSIF",
            "date_signature": "2026-08-30",
            "mode_signature": "ELECTRONIQUE",
            "date_debut": "2026-08-30",
            "date_fin": "2027-02-28",
            "statut": "ACTIF",
            "commentaire": None,
            "id_client": 1,
            "id_chasseur": 1,
        },
        contexte={
            "source": "api",
            "action": "delete_mandat",
        },
    )

    db.commit.assert_called_once()