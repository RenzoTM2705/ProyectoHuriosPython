"""Esquemas Pydantic para el módulo de almacenamiento (Storage)."""

from pydantic import BaseModel

class ImageUploadResponse(BaseModel):
    """Respuesta estructurada al subir una imagen."""
    message: str
    image_url: str

class ImageDeleteResponse(BaseModel):
    """Respuesta estructurada al eliminar una imagen."""
    message: str