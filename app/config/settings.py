"""Configuración centralizada de la aplicación.

La aplicación carga las variables desde .env, valida las obligatorias y expone
una única instancia para evitar valores hardcodeados o dispersos por el código.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class SettingsError(RuntimeError):
    """Señala variables de entorno ausentes o inválidas."""


def _require_env(name: str) -> str:
    """Obtiene una variable obligatoria y falla rápido si no existe."""

    value = os.getenv(name, "").strip()
    if not value:
        raise SettingsError(f"Falta la variable obligatoria: {name}")
    return value


def _get_int_env(name: str, default: str) -> int:
    """Lee una variable entera y valida que el valor sea numérico."""

    raw_value = os.getenv(name, default).strip()
    try:
        return int(raw_value)
    except ValueError as exc:
        raise SettingsError(f"La variable {name} debe ser un número entero") from exc


def _get_bool_env(name: str, default: str = "false") -> bool:
    """Lee una variable booleana usando valores típicos de entorno."""

    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    """Variables de entorno consumidas por la API."""

    app_name: str
    app_version: str
    environment: str
    debug: bool
    supabase_url: str
    supabase_key: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int


@lru_cache
def get_settings() -> Settings:
    """Carga y valida la configuración una sola vez por proceso."""

    return Settings(
        app_name=os.getenv("APP_NAME", "Hurios Rally API"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=_get_bool_env("DEBUG", "true"),
        supabase_url=_require_env("SUPABASE_URL"),
        supabase_key=_require_env("SUPABASE_KEY"),
        jwt_secret=_require_env("JWT_SECRET"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256") or "HS256",
        access_token_expire_minutes=_get_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", "60"),
    )


settings = get_settings()
