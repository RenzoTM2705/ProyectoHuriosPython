"""Router público del módulo de usuarios."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.schemas.user import UserDeleteResponse, UserResponse, UserUpdateRequest
from app.services.user_service import UserService, get_user_service


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("", response_model=list[UserResponse])
def list_users(service: UserService = Depends(get_user_service)) -> list[UserResponse]:
    """Lista todos los usuarios almacenados en Supabase PostgreSQL."""

    return service.list_users()


@users_router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Obtiene un usuario por id."""

    return service.get_user(user_id)


@users_router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    payload: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Actualiza completamente un usuario existente."""

    return service.update_user(user_id, payload)


@users_router.delete("/{user_id}", response_model=UserDeleteResponse)
def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserDeleteResponse:
    """Elimina un usuario por id."""

    return service.delete_user(user_id)
