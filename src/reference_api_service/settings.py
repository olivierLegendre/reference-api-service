from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "reference-api-service"
    app_env: str = "dev"

    persistence_backend: str = Field(default="postgres", pattern="^(in_memory|postgres)$")
    postgres_dsn: str = "postgresql://postgres:postgres@localhost:5432/reference_api"
    postgres_auto_init: bool = True

    model_config = SettingsConfigDict(
        env_prefix="REFERENCE_API_",
        env_file=".env",
        extra="ignore",
    )
