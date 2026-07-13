"""Servicio de Storage. Valida archivos y orquesta la subida a Supabase."""

from __future__ import annotations
import os
from uuid import UUID
from fastapi import UploadFile, HTTPException, status
from app.repositories.storage_repository import StorageRepository, StorageRepositoryError
from app.schemas.storage import ImageUploadResponse, ImageDeleteResponse

class StorageService:
    """Casos de uso para el manejo de archivos e imágenes."""

    def __init__(self, repository: StorageRepository | None = None) -> None:
        self.repository = repository or StorageRepository()

    async def upload_product_image(self, product_id: UUID, file: UploadFile) -> ImageUploadResponse:
        """Valida y sube la imagen de un producto al bucket 'products'."""
        self._validate_image(file)
        try:
            file_bytes = await file.read()
            file_ext = os.path.splitext(file.filename)[1] or ".jpg"
            file_path = f"{product_id}/main_image{file_ext}"

            public_url = self.repository.upload_file(
                bucket="products",
                file_path=file_path,
                file_bytes=file_bytes,
                content_type=file.content_type
            )
            
            self.repository.update_product_image(product_id, public_url)
            
            return ImageUploadResponse(
                message="Imagen del producto subida correctamente",
                image_url=public_url
            )
        except StorageRepositoryError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
        finally:
            await file.close()

    async def upload_profile_image(self, user_id: UUID, file: UploadFile) -> ImageUploadResponse:
        """Valida y sube la imagen de perfil del usuario al bucket 'profiles'."""
        self._validate_image(file)
        try:
            file_bytes = await file.read()
            file_ext = os.path.splitext(file.filename)[1] or ".jpg"
            file_path = f"{user_id}/avatar{file_ext}"

            public_url = self.repository.upload_file(
                bucket="profiles",
                file_path=file_path,
                file_bytes=file_bytes,
                content_type=file.content_type
            )
            
            self.repository.update_user_image(user_id, public_url)
            
            return ImageUploadResponse(
                message="Imagen de perfil actualizada correctamente",
                image_url=public_url
            )
        except StorageRepositoryError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
        finally:
            await file.close()

    def delete_product_image(self, product_id: UUID) -> ImageDeleteResponse:
        """Elimina la imagen del producto del bucket y limpia la URL en la base de datos."""
        try:
            # Nota: Si el nombre del archivo es variable, podrías necesitar consultar 
            # la URL actual del producto para extraer la ruta exacta.
            # Para este diseño, asumimos el formato estándar.
            # En un entorno real, es mejor usar comodines o listar archivos del directorio del producto.
            
            # Eliminamos el directorio del producto (o archivos conocidos)
            self.repository.delete_file("products", f"{product_id}/main_image.jpg")
            self.repository.delete_file("products", f"{product_id}/main_image.png")
            
            self.repository.update_product_image(product_id, None)
            
            return ImageDeleteResponse(message="Imagen del producto eliminada correctamente")
        except StorageRepositoryError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    def _validate_image(self, file: UploadFile) -> None:
        """Valida que el archivo subido sea una imagen."""
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen válida (jpeg, png, webp, etc.)"
            )

def get_storage_service() -> StorageService:
    """Dependency helper para FastAPI."""
    return StorageService()