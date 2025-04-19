from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General
    project_name: str
    skip_auth: bool  # Temporary, for easy disabling of auth during development
    max_file_size: int

    # Auth0
    auth0_domain: str
    auth0_api_audience: str
    auth0_issuer: str
    auth0_algorithms: str

    # Postgres
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


settings = Settings()
