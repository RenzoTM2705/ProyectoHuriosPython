"""Modelos de dominio para autenticación."""

from dataclasses import dataclass, field
from uuid import UUID

from app.models.user import UserRole


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


@dataclass(slots=True)
class AuthenticatedUser:
    """Usuario autenticado resuelto desde el JWT y el perfil interno."""

    id: UUID
    email: str
    role: UserRole
    token: str | None = None
    claims: dict[str, object] = field(default_factory=dict)
