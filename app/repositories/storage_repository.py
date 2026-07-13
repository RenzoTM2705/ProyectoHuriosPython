"""Repositorio de Storage usando Supabase."""

from __future__ import annotations
from uuid import UUID
from app.repositories.base_repository import BaseRepository

class StorageRepositoryError(Exception):
    """Error de persistencia en Supabase Storage."""

class StorageRepository(BaseRepository):
    """Acceso a los Buckets de Supabase y actualización de URLs en PostgreSQL."""

    def upload_file(self, bucket: str, file_path: str, file_bytes: bytes, content_type: str) -> str:
        """Sube un archivo a un bucket de Supabase y devuelve la URL pública."""
        try:
            self.client.storage.from_(bucket).upload(
                file=file_bytes,
                path=file_path,
                file_options={"content-type": content_type, "x-upsert": "true"}
            )
            return self.client.storage.from_(bucket).get_public_url(file_path)
        except Exception as exc:
            raise StorageRepositoryError(self._normalize_error(exc, f"Error al subir archivo al bucket {bucket}")) from exc

    def delete_file(self, bucket: str, file_path: str) -> None:
        """Elimina un archivo de un bucket de Supabase."""
        try:
            self.client.storage.from_(bucket).remove([file_path])
        except Exception as exc:
            raise StorageRepositoryError(self._normalize_error(exc, f"Error al eliminar archivo del bucket {bucket}")) from exc

    def update_product_image(self, product_id: UUID, image_url: str | None) -> None:
        """Actualiza la URL de la imagen de un producto en la base de datos."""
        try:
            self.client.table("products").update({"image_url": image_url}).eq("id", str(product_id)).execute()
        except Exception as exc:
            raise StorageRepositoryError(self._normalize_error(exc, "Error al actualizar la imagen del producto")) from exc

    def update_user_image(self, user_id: UUID, image_url: str | None) -> None:
        """Actualiza la URL de la imagen de perfil de un usuario en la base de datos."""
        try:
            self.client.table("users").update({"image_url": image_url}).eq("id", str(user_id)).execute()
        except Exception as exc:
            raise StorageRepositoryError(self._normalize_error(exc, "Error al actualizar la imagen del usuario")) from exc