"""Repositorio de ejemplo para validar la estructura por capas."""

from app.repositories.base_repository import BaseRepository


class HealthRepository(BaseRepository):
    """Repositorio mínimo que luego podrá consultar infraestructura real."""

    def get_status(self) -> dict[str, str]:
        """Devuelve información estática mientras no exista backend persistente."""

        return {
            "status": "ok",
            "message": "Servicio saludable y listo para integraciones futuras",
        }
