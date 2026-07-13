"""Router para la gestión de archivos e imágenes en Supabase Storage."""

from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File
from app.dependencies.auth import get_current_user, require_admin_user
from app.models.auth import AuthenticatedUser
from app.schemas.storage import ImageUploadResponse, ImageDeleteResponse
from app.services.storage_service import StorageService, get_storage_service

storage_router = APIRouter(tags=["Storage"])

@storage_router.post("/products/{product_id}/image", response_model=ImageUploadResponse, dependencies=[Depends(require_admin_user)])
async def upload_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    service: StorageService = Depends(get_storage_service),
) -> ImageUploadResponse:
    """Sube o actualiza la imagen principal de un producto (Requiere rol Admin)."""
    return await service.upload_product_image(product_id, file)

@storage_router.delete("/products/{product_id}/image", response_model=ImageDeleteResponse, dependencies=[Depends(require_admin_user)])
def delete_product_image(
    product_id: UUID,
    service: StorageService = Depends(get_storage_service),
) -> ImageDeleteResponse:
    """Elimina la imagen de un producto y limpia su URL (Requiere rol Admin)."""
    return service.delete_product_image(product_id)

@storage_router.post("/users/profile/image", response_model=ImageUploadResponse)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StorageService = Depends(get_storage_service),
) -> ImageUploadResponse:
    """Sube o actualiza la imagen de perfil del usuario autenticado."""
    return await service.upload_profile_image(current_user.id, file)