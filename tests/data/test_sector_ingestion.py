"""Offline cross-layer contracts; SQL execution is verified by runtime SQL/dbt checks."""

import json
from unittest.mock import MagicMock

import pytest

from database.seeds import generer_annonces as generator
from database.seeds import load_raw_generated_data as raw_loader
from database.seeds import load_staging_to_oltp as property_loader
from database.seeds import sector_contract as sectors
from database.seeds import transform_raw_to_staging as transformer


@pytest.fixture
def catalogue():
    return sectors.index_catalogue([
        dict(id_secteur=71, pays="France", ville="Montpellier", quartier="Écusson", code_postal="34000"),
        dict(id_secteur=99, pays="France", ville="Montpellier", quartier="Port Marianne", code_postal="34000"),
    ])


def connection():
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = conn.cursor.return_value
    return conn


def test_codes_do_not_depend_on_local_ids_and_preserve_neighbourhood(catalogue):
    first, second = catalogue.values()
    assert first["secteur_code"] != second["secteur_code"]
    assert sectors.sector_code(dict(first, id_secteur=200)) == first["secteur_code"]
    assert sectors.sector_code(dict(first, quartier="  E\u0301CUSSON ")) == first["secteur_code"]
    with pytest.raises(RuntimeError, match="Ambiguous"):
        sectors.index_catalogue([first, dict(first, id_secteur=200)])


def test_resolution_never_guesses_a_neighbourhood_from_postcode(catalogue):
    row = dict(reference="A", ville="Montpellier", code_postal="34000")
    assert sectors.resolve_sector(row, catalogue) is None
    for sector in catalogue.values():
        assert sectors.resolve_sector(dict(row, secteur_code=sector["secteur_code"]), catalogue) == sector["id_secteur"]
    with pytest.raises(ValueError, match="Unknown or inactive"):
        sectors.resolve_sector(dict(row, secteur_code="not-known"), catalogue)
    with pytest.raises(ValueError, match="ville conflicts"):
        sectors.resolve_sector(dict(row, ville="Lyon", secteur_code=next(iter(catalogue))), catalogue)
    with pytest.raises(ValueError, match="code_postal conflicts"):
        sectors.resolve_sector(dict(row, code_postal="34090", secteur_code=next(iter(catalogue))), catalogue)


def test_generator_csv_json_raw_staging_round_trip(tmp_path, monkeypatch, catalogue):
    # Execute the real generator main, redirecting only its output root and args.
    exported = tmp_path / "secteurs.json"
    exported.write_text(json.dumps(list(catalogue.values())), encoding="utf-8")
    monkeypatch.setattr(generator, "__file__", str(tmp_path / "database/seeds/generer_annonces.py"))
    monkeypatch.setattr("sys.argv", ["generator", "-r", "2", "--min-annonces", "2", "--max-annonces", "2",
                                    "--secteurs-catalogue", str(exported)])
    generator.main()
    root = tmp_path / "database/fixtures/annonces"
    searches = raw_loader.read_csv(root / "recherches.csv")
    adverts = raw_loader.read_csv(root / "annonces.csv")
    by_ref = {row["reference"]: row for row in searches}
    assert len(searches) == 2 and len(adverts) == 4
    for csv_row in adverts:
        raw = {target: csv_row.get(source) for source, target in raw_loader.ANNONCES_MAPPING.items()}
        raw.update(raw_id=1, ingestion_batch="test", source_file="annonces.csv")
        staged = transformer.transform_annonce(raw)
        assert staged["quality_valid"], staged["quality_errors"]
        search_csv = by_ref[csv_row["recherche_ref"]]
        search_raw = {name: search_csv.get(name) for name in raw_loader.RECHERCHES_COLUMNS}
        search_raw.update(raw_id=1, ingestion_batch="test", source_file="recherches.csv")
        staged_search = transformer.transform_recherche(search_raw)
        assert staged_search["quality_valid"], staged_search["quality_errors"]
        assert sectors.resolve_sector(staged, catalogue) == sectors.resolve_sector(staged_search, catalogue)
        staged_conn = connection()
        transformer.upsert_recherches(staged_conn, [staged_search])
        transformer.upsert_annonces(staged_conn, [staged])
        for call in staged_conn.cursor.return_value.executemany.call_args_list:
            sql, values = call.args
            assert values[0]["secteur_code"] == staged["secteur_code"]
            assert "%(secteur_code)s" in sql and "secteur_code = EXCLUDED.secteur_code" in sql
        assert staged["latitude"] is None and staged["longitude"] is None
        files = [json.loads(path.read_text(encoding="utf-8")) for path in (root / "json").glob("*.json")]
        assert next(row for row in files if row["reference"] == csv_row["reference"])["secteur_code"] == staged["secteur_code"]

    conn = connection()
    monkeypatch.setattr(raw_loader, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(raw_loader, "RECHERCHES_CSV", root / "recherches.csv")
    monkeypatch.setattr(raw_loader, "ANNONCES_CSV", root / "annonces.csv")
    monkeypatch.setattr(raw_loader, "batch_already_loaded", lambda *args: False)
    raw_loader.load_recherches(conn, "test")
    raw_loader.load_annonces(conn, "test")
    for call in conn.cursor.return_value.executemany.call_args_list:
        sql, values = call.args
        assert "secteur_code" in sql
        assert sql.count("%s") == len(values[0])
        assert any(value in catalogue for value in values[0] if isinstance(value, str))


def test_legacy_files_without_sector_still_transform():
    search = generator.generer_recherche(1)
    advert = generator.aplatir(generator.generer_annonce_correspondante(search))
    raw = {target: advert.get(source) for source, target in raw_loader.ANNONCES_MAPPING.items()}
    raw.update(raw_id=1, ingestion_batch="old", source_file="old.csv")
    staged = transformer.transform_annonce(raw)
    assert staged["secteur_code"] is None
    assert sectors.resolve_sector(staged, {}) is None


def test_property_assignment_follows_location_upsert_in_same_transaction(monkeypatch, catalogue):
    conn = connection()
    conn.cursor.return_value.fetchone.return_value = (1,)
    monkeypatch.setattr(property_loader, "load_catalogue", lambda conn: catalogue)
    first = next(iter(catalogue.values()))
    row = dict(reference="AN-1", ville=first["ville"], code_postal=first["code_postal"], secteur_code=first["secteur_code"])
    property_loader.upsert_biens(conn, [row], 42)
    calls = conn.cursor.return_value.executemany.call_args_list
    assert "INSERT INTO real_estate.bien" in calls[0].args[0]
    assert "UPDATE real_estate.bien SET id_secteur" in calls[1].args[0]
    assert calls[1].args[1] == [(71, 42, "AN-1")]
    conn.commit.assert_not_called()  # Outer loader owns the atomic transaction.


def test_unknown_code_fails_before_property_writes(monkeypatch, catalogue):
    conn = connection()
    monkeypatch.setattr(property_loader, "load_catalogue", lambda conn: catalogue)
    with pytest.raises(ValueError):
        property_loader.upsert_biens(conn, [dict(reference="A", secteur_code="missing")], 42)
    conn.cursor.return_value.executemany.assert_not_called()


@pytest.mark.parametrize("previous", [[], [(71,)]])
def test_search_assignment_can_be_replayed(previous):
    conn = connection()
    conn.cursor.return_value.fetchall.return_value = previous
    sectors.link_search_sector(conn, 100, 71)
    assert conn.cursor.return_value.execute.call_args.args[1] == (100, 71)


def test_replay_does_not_replace_versioned_search_sectors():
    conn = connection()
    conn.cursor.return_value.fetchall.return_value = [(99,)]
    with pytest.raises(ValueError, match="new search reference"):
        sectors.link_search_sector(conn, 100, 71)
    assert conn.cursor.return_value.execute.call_count == 1


def test_legacy_replay_does_not_erase_reviewed_assignments():
    conn = connection()
    sectors.link_search_sector(conn, 100, None)
    sectors.assign_property_sectors(conn, [dict(reference="A", id_secteur=None)], 42)
    conn.cursor.assert_not_called()


def test_inactive_sectors_are_not_exported_or_resolved():
    conn = connection()
    conn.cursor.return_value.fetchall.return_value = []
    assert sectors.load_catalogue(conn) == {}
    assert "WHERE actif = TRUE" in conn.cursor.return_value.execute.call_args.args[0]


def test_generator_refuses_an_empty_explicit_catalogue(tmp_path, monkeypatch):
    path = tmp_path / "empty.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["generator", "--secteurs-catalogue", str(path)])
    with pytest.raises(ValueError, match="vide"):
        generator.main()


def test_schema_check_stops_before_generation_when_migration_is_missing():
    conn = connection()
    conn.cursor.return_value.fetchone.return_value = (False,)
    with pytest.raises(RuntimeError, match="migration 018"):
        sectors.check_schema(conn)
    assert conn.cursor.return_value.execute.call_count == 1


def test_export_uses_read_only_connection_and_excludes_local_ids(tmp_path, monkeypatch, catalogue):
    import psycopg

    conn = connection()
    conn.__enter__.return_value = conn
    monkeypatch.setattr(psycopg, "connect", lambda **kwargs: conn)
    monkeypatch.setattr(sectors, "check_schema", lambda conn: None)
    monkeypatch.setattr(sectors, "load_catalogue", lambda conn: catalogue)
    for name in ("HOST", "PORT", "DB", "USER", "PASSWORD"):
        monkeypatch.setenv("POSTGRES_" + name, "test-only")
    path = tmp_path / "catalogue.json"
    sectors.export_catalogue(path)
    rows = json.loads(path.read_text(encoding="utf-8"))
    assert len(rows) == 2
    assert conn.read_only is True
    assert all("id_secteur" not in row for row in rows)
    assert {row["secteur_code"] for row in rows} == set(catalogue)


def test_schema_only_mode_never_loads_or_exports_catalogue(monkeypatch):
    conn = connection()
    conn.__enter__.return_value = conn
    monkeypatch.setattr(sectors, "database_connection", lambda: conn)
    checked = MagicMock()
    forbidden = MagicMock(side_effect=AssertionError("Standard mode must not load sectors"))
    monkeypatch.setattr(sectors, "check_schema", checked)
    monkeypatch.setattr(sectors, "load_catalogue", forbidden)
    monkeypatch.setattr(sectors, "export_catalogue", forbidden)
    sectors.main(["--check-schema"])
    checked.assert_called_once_with(conn)
    forbidden.assert_not_called()


def test_standard_cli_generates_original_files_without_catalogue(tmp_path, monkeypatch):
    monkeypatch.setattr(generator, "__file__", str(tmp_path / "database/seeds/generer_annonces.py"))
    monkeypatch.setattr("sys.argv", ["generator", "-r", "2", "--min-annonces", "2", "--max-annonces", "2"])
    generator.main()
    root = tmp_path / "database/fixtures/annonces"
    searches = raw_loader.read_csv(root / "recherches.csv")
    adverts = raw_loader.read_csv(root / "annonces.csv")
    assert len(searches) == 2 and len(adverts) == 4
    assert all(not row.get("secteur_code") for row in searches + adverts)
    assert len(list((root / "json").glob("*.json"))) == 4
    assert not (root / "secteurs.json").exists()


def test_standard_property_load_does_not_require_catalogue(monkeypatch):
    conn = connection()
    conn.cursor.return_value.fetchone.return_value = (1,)
    forbidden = MagicMock(side_effect=AssertionError("No sector evidence to resolve"))
    monkeypatch.setattr(property_loader, "load_catalogue", forbidden)
    property_loader.upsert_biens(conn, [dict(reference="AN-legacy")], 42)
    forbidden.assert_not_called()
    assert conn.cursor.return_value.executemany.call_count == 1
