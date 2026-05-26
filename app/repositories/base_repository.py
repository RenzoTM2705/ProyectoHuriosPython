"""Contrato base para repositorios.

Centraliza la conexión reutilizable con Supabase y utilidades comunes de
normalización de datos para evitar duplicación en cada repositorio.
"""

from __future__ import annotations

from abc import ABC
from collections.abc import Mapping
from datetime import datetime

from app.config.supabase import get_supabase_client


class BaseRepository(ABC):
    """Clase base para repositorios de la capa de infraestructura."""

    def __init__(self, client=None) -> None:
        self.client = client or get_supabase_client()

    def _extract_rows(self, response) -> list[Mapping[str, object]]:
        """Extrae filas desde la respuesta del SDK de Supabase."""

        data = getattr(response, "data", None)
        if data is None:
            return []
        if isinstance(data, list):
            return [row for row in data if isinstance(row, Mapping)]
        if isinstance(data, Mapping):
            return [data]
        return []

    def _extract_payload(self, value, fallback_key: str) -> dict[str, object]:
        """Normaliza objetos o diccionarios devueltos por el SDK de Supabase."""

        if value is None:
            return {}

        if hasattr(value, "model_dump"):
            payload = value.model_dump()
            return payload if isinstance(payload, dict) else {}

        if hasattr(value, "dict"):
            payload = value.dict()
            return payload if isinstance(payload, dict) else {}

        if isinstance(value, Mapping):
            return dict(value)

        if hasattr(value, "__dict__"):
            return {
                key: field_value
                for key, field_value in vars(value).items()
                if not key.startswith("_")
            }

        return {fallback_key: value} if value else {}

    def _parse_datetime(self, value) -> datetime | None:
        """Convierte fechas ISO de Supabase a datetime."""

        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        text = str(value).replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            return None

    def _normalize_error(self, exc: Exception, fallback_message: str) -> str:
        """Genera un mensaje seguro y legible para la capa de servicio."""

        message = str(exc).strip()
        return message or fallback_message
