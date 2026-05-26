"""Modelo base de dominio.

Aquí vivirán las entidades del negocio, separadas de los esquemas de API.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class BaseDomainModel:
    """Entidad base reutilizable en el dominio."""

    id: UUID = field(default_factory=uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None
