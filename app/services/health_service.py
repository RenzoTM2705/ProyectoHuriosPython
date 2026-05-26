"""Servicio de ejemplo para la capa de negocio.

La idea es que aquí viva la orquestación del caso de uso, sin depender
directamente del framework web.
"""

from app.repositories.health_repository import HealthRepository
from app.schemas.health import HealthResponse


class HealthService:
    """Caso de uso simple para el endpoint de salud."""

    def __init__(self, repository: HealthRepository | None = None) -> None:
        self.repository = repository or HealthRepository()

    def get_health(self) -> HealthResponse:
        """Construye la respuesta pública del health check."""

        data = self.repository.get_status()
        return HealthResponse(**data)


def get_health_service() -> HealthService:
    """Dependency injection helper para FastAPI."""

    return HealthService()
