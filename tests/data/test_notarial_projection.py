from unittest.mock import MagicMock

from database.olap.notarial_projection import load_notarial_projection


def test_projection_aggregates_each_movement_once_and_upserts_snapshot():
    cursor = MagicMock()
    load_notarial_projection(cursor)
    sql = cursor.execute.call_args.args[0]
    assert "GROUP BY id_dossier_notarial" in sql
    assert "ON CONFLICT (id_dossier_source) DO UPDATE" in sql
    assert "nature = 'COLLECTE_NOTAIRE'" in sql
    assert "nature = 'RECEPTION_ENTREPRISE'" in sql
    assert "reference_document" not in sql
    assert "email" not in sql
