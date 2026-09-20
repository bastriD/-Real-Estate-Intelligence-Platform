import json
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.db.models.audit_log import AuditLog
from src.api.db.models.offre import Offre
from src.api.schemas.offre import (
    OffreCreate,
    OffreDecision,
    OffreRevision,
)
from src.api.services.offre import (
    OffreService,
    OffreValidationError,
)


def make_offre(
    *,
    id_offre=42,
    numero_version=1,
    montant=Decimal("250000.00"),
    statut="SOUMISE",
    commentaire="Initial offer",
):
    return Offre(
        id_offre=id_offre,
        id_presentation=19,
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
        date_decision=None,
        statut=statut,
        commentaire=commentaire,
        date_creation=datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )


def setup_service():
    db = MagicMock()

    service = OffreService(db)

    assert service.audit.session is db
    assert service.audit.repository.session is db

    return db, service


def get_audits(db):
    return [
        call.args[0]
        for call in db.add.call_args_list
        if isinstance(
            call.args[0],
            AuditLog,
        )
    ]


def test_create_writes_audit_before_single_commit():
    db, service = setup_service()

    created = make_offre()

    service.repository.get_demande_id_for_presentation = (
        MagicMock(return_value=4)
    )

    service.repository.get_latest_for_presentation = (
        MagicMock(return_value=None)
    )

    service.repository.create = MagicMock(
        return_value=created
    )

    payload = OffreCreate(
        id_presentation=19,
        montant=Decimal("250000.00"),
        commentaire="Initial offer",
    )

    result = service.create_offre(
        payload,
        utilisateur="hunter@example.com",
    )

    assert result is created

    audits = get_audits(db)

    assert len(audits) == 1

    audit = audits[0]

    assert audit.table_name == "offre"
    assert audit.schema_name == "real_estate"
    assert audit.operation == "INSERT"
    assert audit.record_id == "42"
    assert (
        audit.utilisateur
        == "hunter@example.com"
    )

    assert audit.contexte["source"] == "api"
    assert (
        audit.contexte["action"]
        == "create_offre"
    )

    assert audit.ancienne_valeur is None

    snapshot = audit.nouvelle_valeur

    assert snapshot["id_offre"] == 42
    assert snapshot["id_presentation"] == 19
    assert snapshot["numero_version"] == 1
    assert snapshot["montant"] == "250000.00"
    assert snapshot["statut"] == "SOUMISE"
    assert (
        snapshot["commentaire"]
        == "Initial offer"
    )

    json.dumps(snapshot)

    db.commit.assert_called_once()
    db.rollback.assert_not_called()

    names = [
        call[0]
        for call in db.method_calls
    ]

    assert max(
        index
        for index, name in enumerate(names)
        if name == "add"
    ) < names.index("commit")


def test_decision_writes_before_and_after_snapshots():
    db, service = setup_service()

    offre = make_offre()

    service.repository.get_by_id_for_update = (
        MagicMock(return_value=offre)
    )

    service.repository.save = MagicMock(
        return_value=offre
    )

    payload = OffreDecision(
        statut="ACCEPTEE",
        commentaire="Seller accepted",
    )

    result = service.decide_offre(
        42,
        payload,
        utilisateur="hunter@example.com",
    )

    assert result is offre
    assert offre.statut == "ACCEPTEE"
    assert offre.date_decision is not None
    assert (
        offre.commentaire
        == "Seller accepted"
    )

    audits = get_audits(db)

    assert len(audits) == 1

    audit = audits[0]

    assert audit.table_name == "offre"
    assert audit.schema_name == "real_estate"
    assert audit.operation == "UPDATE"
    assert audit.record_id == "42"
    assert (
        audit.utilisateur
        == "hunter@example.com"
    )

    assert audit.contexte["source"] == "api"
    assert (
        audit.contexte["action"]
        == "decide_offre"
    )

    assert (
        audit.ancienne_valeur["statut"]
        == "SOUMISE"
    )

    assert (
        audit.ancienne_valeur[
            "date_decision"
        ]
        is None
    )

    assert (
        audit.nouvelle_valeur["statut"]
        == "ACCEPTEE"
    )

    assert (
        audit.nouvelle_valeur[
            "date_decision"
        ]
        is not None
    )

    assert (
        audit.nouvelle_valeur[
            "commentaire"
        ]
        == "Seller accepted"
    )

    json.dumps(audit.ancienne_valeur)
    json.dumps(audit.nouvelle_valeur)

    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_revision_writes_update_and_insert_audits_before_commit():
    db, service = setup_service()

    current = make_offre()

    revised = make_offre(
        id_offre=43,
        numero_version=2,
        montant=Decimal("245000.00"),
        statut="SOUMISE",
        commentaire="Revised offer",
    )

    service.repository.get_by_id_for_update = (
        MagicMock(return_value=current)
    )

    service.repository.get_latest_for_presentation = (
        MagicMock(return_value=current)
    )

    service.repository.save = MagicMock(
        return_value=current
    )

    service.repository.create = MagicMock(
        return_value=revised
    )

    payload = OffreRevision(
        montant=Decimal("245000.00"),
        commentaire="Revised offer",
    )

    result = service.revise_offre(
        42,
        payload,
        utilisateur="hunter@example.com",
    )

    assert result is revised

    assert current.statut == "REVISEE"
    assert current.date_decision is not None

    assert revised.numero_version == 2
    assert revised.statut == "SOUMISE"

    audits = get_audits(db)

    assert len(audits) == 2

    update_audit = audits[0]
    insert_audit = audits[1]

    assert update_audit.table_name == "offre"
    assert update_audit.schema_name == "real_estate"
    assert update_audit.operation == "UPDATE"
    assert update_audit.record_id == "42"
    assert (
        update_audit.utilisateur
        == "hunter@example.com"
    )

    assert (
        update_audit.contexte["source"]
        == "api"
    )
    assert (
        update_audit.contexte["action"]
        == "revise_offre"
    )

    assert (
        update_audit.ancienne_valeur[
            "statut"
        ]
        == "SOUMISE"
    )

    assert (
        update_audit.nouvelle_valeur[
            "statut"
        ]
        == "REVISEE"
    )

    assert insert_audit.table_name == "offre"
    assert insert_audit.schema_name == "real_estate"
    assert insert_audit.operation == "INSERT"
    assert insert_audit.record_id == "43"
    assert (
        insert_audit.utilisateur
        == "hunter@example.com"
    )

    assert (
        insert_audit.contexte["source"]
        == "api"
    )
    assert (
        insert_audit.contexte["action"]
        == "revise_offre"
    )

    assert insert_audit.ancienne_valeur is None

    assert (
        insert_audit.nouvelle_valeur[
            "numero_version"
        ]
        == 2
    )

    assert (
        insert_audit.nouvelle_valeur[
            "montant"
        ]
        == "245000.00"
    )

    assert (
        insert_audit.nouvelle_valeur[
            "statut"
        ]
        == "SOUMISE"
    )

    json.dumps(
        update_audit.ancienne_valeur
    )
    json.dumps(
        update_audit.nouvelle_valeur
    )
    json.dumps(
        insert_audit.nouvelle_valeur
    )

    db.commit.assert_called_once()
    db.rollback.assert_not_called()

    names = [
        call[0]
        for call in db.method_calls
    ]

    assert max(
        index
        for index, name in enumerate(names)
        if name == "add"
    ) < names.index("commit")


@pytest.mark.parametrize(
    "operation",
    [
        "CREATE",
        "DECISION",
        "REVISION",
    ],
)
@pytest.mark.parametrize(
    "integrity_error",
    [True, False],
)
def test_audit_failure_rolls_back_without_committing(
    operation,
    integrity_error,
):
    db, service = setup_service()

    failure = (
        IntegrityError(
            "INSERT audit",
            {},
            Exception("failure"),
        )
        if integrity_error
        else RuntimeError("audit failed")
    )

    service.audit.log_change = MagicMock(
        side_effect=failure
    )

    if operation == "CREATE":
        service.repository.get_demande_id_for_presentation = (
            MagicMock(return_value=4)
        )

        service.repository.get_latest_for_presentation = (
            MagicMock(return_value=None)
        )

        service.repository.create = MagicMock(
            return_value=make_offre()
        )

        action = lambda: service.create_offre(
            OffreCreate(
                id_presentation=19,
                montant=Decimal(
                    "250000.00"
                ),
            ),
            utilisateur=(
                "hunter@example.com"
            ),
        )

    elif operation == "DECISION":
        offre = make_offre()

        service.repository.get_by_id_for_update = (
            MagicMock(return_value=offre)
        )

        service.repository.save = MagicMock(
            return_value=offre
        )

        action = lambda: service.decide_offre(
            42,
            OffreDecision(
                statut="REFUSEE"
            ),
            utilisateur=(
                "hunter@example.com"
            ),
        )

    else:
        current = make_offre()

        revised = make_offre(
            id_offre=43,
            numero_version=2,
            montant=Decimal(
                "245000.00"
            ),
        )

        service.repository.get_by_id_for_update = (
            MagicMock(return_value=current)
        )

        service.repository.get_latest_for_presentation = (
            MagicMock(return_value=current)
        )

        service.repository.save = MagicMock(
            return_value=current
        )

        service.repository.create = MagicMock(
            return_value=revised
        )

        action = lambda: service.revise_offre(
            42,
            OffreRevision(
                montant=Decimal(
                    "245000.00"
                ),
            ),
            utilisateur=(
                "hunter@example.com"
            ),
        )

    expected = (
        OffreValidationError
        if integrity_error
        else RuntimeError
    )

    with pytest.raises(expected):
        action()

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_snapshot_is_json_serializable():
    offre = make_offre()

    snapshot = OffreService._offre_snapshot(
        offre
    )

    assert snapshot["id_offre"] == 42
    assert snapshot["id_presentation"] == 19
    assert snapshot["numero_version"] == 1
    assert snapshot["montant"] == "250000.00"

    assert snapshot["date_offre"] == (
        "2026-09-20T12:00:00+00:00"
    )

    assert snapshot["date_decision"] is None
    assert snapshot["statut"] == "SOUMISE"

    json.dumps(snapshot)