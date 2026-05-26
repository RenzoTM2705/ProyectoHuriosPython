"""Configuración centralizada de la aplicación.

Usar una única fuente de verdad para variables de entorno facilita la
escalabilidad y evita valores dispersos por el código.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables de entorno consumidas por la API."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Empresa Backend API")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)

    supabase_url: str = Field(default="")
    supabase_key: str = Field(default="")

    database_url: str = Field(default="")

    # Preparación para autenticación JWT futura.
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)


@lru_cache
def get_settings() -> Settings:
    """Evita recrear la configuración en cada request."""

    return Settings()


settings = get_settings()
