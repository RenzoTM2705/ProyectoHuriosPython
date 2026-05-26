"""Esquemas Pydantic para el módulo de usuarios."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBaseRequest(BaseModel):
    """Datos comunes para validaciones de usuarios."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    role: UserRole


class UserUpdateRequest(UserBaseRequest):
    """Datos requeridos para un reemplazo completo vía PUT."""


class UserResponse(BaseModel):
    """Contrato público de usuario."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserDeleteResponse(BaseModel):
    """Respuesta estándar al eliminar un usuario."""

    message: str
    user_id: UUID
