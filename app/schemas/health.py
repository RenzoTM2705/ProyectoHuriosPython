"""Esquemas relacionados con el endpoint de salud."""

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Respuesta estándar para comprobar disponibilidad."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    message: str
