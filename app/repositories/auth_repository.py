"""Repositorio de autenticación con Supabase Auth.

La responsabilidad de esta capa es hablar con Supabase y normalizar el resultado
para la capa de servicio. No decide qué error HTTP devolver.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.config.supabase import get_supabase_client
from app.models.auth import AuthSessionData, AuthUser
from app.repositories.base_repository import BaseRepository


class AuthRepositoryError(Exception):
    """Error de acceso a la infraestructura de autenticación."""


class AuthRepository(BaseRepository):
    """Acceso a Supabase Auth para registro e inicio de sesión."""

    def __init__(self, client=None) -> None:
        self.client = client or get_supabase_client()

    def register(self, email: str, password: str) -> AuthSessionData:
        """Registra un usuario en Supabase Auth."""

        try:
            response = self.client.auth.sign_up({"email": email, "password": password})
            return self._to_session_data(response)
        except Exception as exc:  # pragma: no cover - normalización de error externo
            raise AuthRepositoryError(self._normalize_error(exc)) from exc

    def login(self, email: str, password: str) -> AuthSessionData:
        """Autentica un usuario y devuelve la sesión emitida por Supabase."""

        try:
            response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            return self._to_session_data(response)
        except Exception as exc:  # pragma: no cover - normalización de error externo
            raise AuthRepositoryError(self._normalize_error(exc)) from exc

    def _to_session_data(self, response) -> AuthSessionData:
        """Convierte la respuesta cruda de Supabase en un modelo de dominio."""

        user_payload = self._extract_payload(getattr(response, "user", None), "user")
        session_payload = self._extract_payload(getattr(response, "session", None), "session")

        if not user_payload:
            raise AuthRepositoryError("Supabase no devolvió información del usuario")

        user = AuthUser(
            id=str(user_payload.get("id", "")),
            email=str(user_payload.get("email", "")),
            created_at=user_payload.get("created_at"),
            confirmed_at=user_payload.get("confirmed_at"),
        )

        return AuthSessionData(
            user=user,
            access_token=session_payload.get("access_token") if session_payload else None,
            refresh_token=session_payload.get("refresh_token") if session_payload else None,
            token_type=session_payload.get("token_type", "bearer") if session_payload else "bearer",
            expires_in=session_payload.get("expires_in") if session_payload else None,
        )

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

    def _normalize_error(self, exc: Exception) -> str:
        """Genera un mensaje seguro y legible para la capa de servicio."""

        message = str(exc).strip()
        return message or "Error inesperado durante la autenticación"
