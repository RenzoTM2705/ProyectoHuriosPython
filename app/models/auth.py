"""Modelos de dominio para autenticación."""

from dataclasses import dataclass


@dataclass(slots=True)
class AuthUser:
    """Representa un usuario autenticado o registrado."""

    id: str
    email: str
    created_at: str | None = None
    confirmed_at: str | None = None


@dataclass(slots=True)
class AuthSessionData:
    """Datos de sesión devueltos por Supabase Auth."""

    user: AuthUser
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None
