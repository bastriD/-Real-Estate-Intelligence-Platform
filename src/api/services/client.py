from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.client import Client
from src.api.repositories.client import ClientRepository
from src.api.schemas.client import ClientCreate, ClientUpdate


class ClientAlreadyExistsError(Exception):
    pass


class ClientNotFoundError(Exception):
    pass


class ClientService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ClientRepository(session)

    def list_clients(self) -> list[Client]:
        return self.repository.list_all()

    def get_client(self, client_id: int) -> Client:
        client = self.repository.get_by_id(client_id)

        if client is None:
            raise ClientNotFoundError(
                f"Client {client_id} not found"
            )

        return client

    def create_client(self, payload: ClientCreate) -> Client:
        existing_client = self.repository.get_by_email(
            str(payload.email)
        )

        if existing_client is not None:
            raise ClientAlreadyExistsError(
                f"Client with email {payload.email} already exists"
            )

        client = Client(
            nom=payload.nom,
            prenom=payload.prenom,
            email=str(payload.email),
            telephone=payload.telephone,
            ville=payload.ville,
            statut=payload.statut.value,
            consentement_contact=payload.consentement_contact,
        )

        try:
            client = self.repository.create(client)
            self.session.commit()

            return client

        except IntegrityError:
            self.session.rollback()

            raise ClientAlreadyExistsError(
                f"Client with email {payload.email} already exists"
            )

    def update_client(
        self,
        client_id: int,
        payload: ClientUpdate,
    ) -> Client:
        client = self.get_client(client_id)

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if "email" in update_data:
            email = str(update_data["email"])

            existing_client = self.repository.get_by_email(email)

            if (
                existing_client is not None
                and existing_client.id_client != client_id
            ):
                raise ClientAlreadyExistsError(
                    f"Client with email {email} already exists"
                )

            update_data["email"] = email

        if "statut" in update_data:
            update_data["statut"] = update_data["statut"].value

        for field_name, value in update_data.items():
            setattr(client, field_name, value)

        try:
            self.session.commit()
            self.session.refresh(client)

            return client

        except IntegrityError:
            self.session.rollback()
            raise ClientAlreadyExistsError(
                "Client update violates a uniqueness constraint"
            )

    def delete_client(self, client_id: int) -> None:
        client = self.get_client(client_id)

        self.repository.delete(client)
        self.session.commit()