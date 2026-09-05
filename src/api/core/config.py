from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Real Estate Intelligence API"
    app_version: str = "1.0.0"

    postgres_host: str = "real-estate-postgresql.real-estate.svc.cluster.local"
    postgres_port: int = 5432
    postgres_db: str = "real_estate"
    postgres_user: str = "real_estate_user"
    postgres_password: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()