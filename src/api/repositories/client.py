from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.client import Client


class ClientRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Client]:
        statement = (
            select(Client)
            .order_by(Client.id_client)
        )

        return list(
            self.session.scalars(statement).all()
        )

    def get_by_id(self, client_id: int) -> Client | None:
        statement = (
            select(Client)
            .where(Client.id_client == client_id)
        )

        return self.session.scalar(statement)

    def get_by_email(self, email: str) -> Client | None:
        statement = (
            select(Client)
            .where(Client.email == email)
        )

        return self.session.scalar(statement)

    def create(self, client: Client) -> Client:
        self.session.add(client)
        self.session.flush()
        self.session.refresh(client)

        return client

    def delete(self, client: Client) -> None:
        self.session.delete(client)
        self.session.flush()