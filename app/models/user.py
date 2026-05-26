"""Modelos de dominio para usuarios."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class UserRole(StrEnum):
    """Roles de negocio soportados por el módulo de usuarios."""

    ADMIN = "admin"
    CUSTOMER = "customer"


@dataclass(slots=True)
class User:
    """Entidad de dominio que representa un usuario en la capa de negocio."""

    id: UUID
    name: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
