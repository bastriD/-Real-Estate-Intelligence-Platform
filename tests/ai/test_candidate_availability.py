import sqlite3

from src.ai.matching.repository import load_candidate_biens


class SQLiteCursor:
    """Run the repository's portable SELECT against real rows, without a server."""

    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, parameters):
        self.result = self.connection.execute(sql.replace("%s", "?"), parameters)

    def fetchall(self):
        return [dict(row) for row in self.result.fetchall()]


class SQLiteConnection:
    def __init__(self, connection):
        self.connection = connection

    def cursor(self, **kwargs):
        return SQLiteCursor(self.connection)


def test_matching_excludes_sold_expired_and_unavailable_properties():
    with sqlite3.connect(":memory:") as db:
        db.row_factory = sqlite3.Row
        db.execute("ATTACH DATABASE ':memory:' AS real_estate")
        db.execute("""CREATE TABLE real_estate.bien (
            id_bien INTEGER, reference_externe TEXT, type_bien TEXT, ville TEXT,
            code_postal TEXT, latitude REAL, longitude REAL, prix REAL,
            surface REAL, nb_pieces INTEGER, nb_chambres INTEGER, dpe TEXT,
            statut TEXT, id_source INTEGER
        )""")
        for i, status in enumerate(["ACTIF", "VENDU", "EXPIRE", "INDISPONIBLE"], 1):
            db.execute("""INSERT INTO real_estate.bien
                (id_bien, type_bien, ville, prix, surface, statut)
                VALUES (?, 'APPARTEMENT', 'Nantes', 200000, 60, ?)""", (i, status))
        result = load_candidate_biens(SQLiteConnection(db), {
            "ville": "Nantes", "type_bien": "APPARTEMENT",
            "budget_max": 300000, "surface_min": 50,
        })
        assert result["id_bien"].tolist() == [1]
