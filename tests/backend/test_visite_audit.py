import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.db.models.audit_log import AuditLog
from src.api.db.models.visite import Visite
from src.api.schemas.visite import VisiteCreate, VisiteUpdate
from src.api.services.visite import (
    VisiteDeleteConflictError,
    VisiteService,
    VisiteValidationError,
)


def make_visite():
    return Visite(
        id_visite=42, id_presentation=19,
        date_visite=datetime(2026, 9, 9, 14, tzinfo=timezone.utc),
        statut="PLANIFIEE", compte_rendu=None, note=None, photos=["before.jpg"],
    )


def setup_service():
    db = MagicMock()
    db.scalar.return_value = 19
    visite = make_visite()
    service = VisiteService(db)
    service.repository.get_by_id = MagicMock(return_value=visite)
    # Assign the database-generated ID, leaving the actual repository/audit
    # methods in place to verify they use the same session.
    def assign_id():
        for call in db.add.call_args_list:
            if isinstance(call.args[0], Visite):
                call.args[0].id_visite = 42
    db.flush.side_effect = assign_id
    return db, service, visite


def mutate(service, operation):
    if operation == "INSERT":
        return service.create_visite(VisiteCreate(
            id_presentation=19, date_visite=make_visite().date_visite,
            photos=["before.jpg"],
        ), utilisateur="hunter@example.com")
    if operation == "UPDATE":
        return service.update_visite(42, VisiteUpdate(
            statut="REALISEE", compte_rendu="Completed", note=4,
            photos=["after.jpg"],
        ), utilisateur="hunter@example.com")
    return service.delete_visite(42, utilisateur="hunter@example.com")


@pytest.mark.parametrize("operation", ["INSERT", "UPDATE", "DELETE"])
def test_mutation_writes_json_snapshot_and_actor_before_single_commit(operation):
    db, service, visite = setup_service()
    assert service.audit.session is db
    assert service.audit.repository.session is db
    mutate(service, operation)
    audits = [c.args[0] for c in db.add.call_args_list if isinstance(c.args[0], AuditLog)]
    assert len(audits) == 1
    audit = audits[0]
    assert audit.table_name == "visite"
    assert audit.schema_name == "real_estate"
    assert audit.operation == operation
    assert audit.record_id == "42"
    assert audit.utilisateur == "hunter@example.com"
    action = {"INSERT": "create", "UPDATE": "update", "DELETE": "delete"}[operation]
    assert audit.contexte == {"source": "api", "action": f"{action}_visite"}
    db.commit.assert_called_once()
    db.rollback.assert_not_called()
    names = [c[0] for c in db.method_calls]
    assert max(i for i, name in enumerate(names) if name == "add") < names.index("commit")
    if operation == "INSERT":
        assert audit.ancienne_valeur is None
        snapshot = audit.nouvelle_valeur
    else:
        snapshot = audit.ancienne_valeur
        assert snapshot["statut"] == "PLANIFIEE"
        assert snapshot["photos"] == ["before.jpg"]
    assert snapshot["id_visite"] == 42
    assert snapshot["id_presentation"] == 19
    assert snapshot["date_visite"] == "2026-09-09T14:00:00+00:00"
    json.dumps(snapshot)
    if operation == "UPDATE":
        assert audit.nouvelle_valeur["statut"] == "REALISEE"
        assert audit.nouvelle_valeur["note"] == 4
        assert audit.nouvelle_valeur["compte_rendu"] == "Completed"
        assert audit.nouvelle_valeur["photos"] == ["after.jpg"]
    if operation == "DELETE":
        assert audit.nouvelle_valeur is None
        db.delete.assert_called_once_with(visite)


@pytest.mark.parametrize("operation", ["INSERT", "UPDATE", "DELETE"])
@pytest.mark.parametrize("integrity_error", [True, False])
def test_audit_failure_rolls_back_without_committing(operation, integrity_error):
    db, service, _ = setup_service()
    failure = IntegrityError("INSERT audit", {}, Exception("failure")) if integrity_error else RuntimeError("audit failed")
    service.audit.log_change = MagicMock(side_effect=failure)
    expected = (VisiteDeleteConflictError if operation == "DELETE" else VisiteValidationError) if integrity_error else RuntimeError
    with pytest.raises(expected):
        mutate(service, operation)
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_snapshot_does_not_retain_mutable_photo_list():
    visite = make_visite()
    snapshot = VisiteService._visite_snapshot(visite)
    visite.photos.append("later.jpg")
    assert snapshot["photos"] == ["before.jpg"]
