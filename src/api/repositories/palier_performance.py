from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.palier_performance import PalierPerformance


class PalierPerformanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_parameters(
        self,
        id_parametres_remuneration: int,
        critere: str | None = None,
    ) -> list[PalierPerformance]:
        stmt = select(PalierPerformance).where(
            PalierPerformance.id_parametres_remuneration
            == id_parametres_remuneration
        )

        if critere is not None:
            stmt = stmt.where(PalierPerformance.critere == critere)

        stmt = stmt.order_by(
            PalierPerformance.critere,
            PalierPerformance.ordre,
        )

        return list(self.db.scalars(stmt).all())

    def get_note_for_value(
        self,
        id_parametres_remuneration: int,
        critere: str,
        value: int,
    ):
        stmt = (
            select(PalierPerformance)
            .where(
                PalierPerformance.id_parametres_remuneration
                == id_parametres_remuneration,
                PalierPerformance.critere == critere,
                (
                    PalierPerformance.borne_max.is_(None)
                    | (PalierPerformance.borne_max >= value)
                ),
            )
            .order_by(PalierPerformance.ordre)
            .limit(1)
        )

        palier = self.db.scalar(stmt)
        return None if palier is None else palier.note