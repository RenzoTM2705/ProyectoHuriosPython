"""Servicio de usuarios.

Aquí viven las reglas de negocio y la traducción de excepciones de persistencia
en respuestas HTTP coherentes para la API.
"""

from uuid import UUID

from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.user_repository import UserNotFoundError, UserRepository, UserRepositoryError
from app.schemas.user import UserDeleteResponse, UserResponse, UserUpdateRequest


class UserService:
    """Casos de uso de usuarios para Hurios Rally."""

    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    def list_users(self) -> list[UserResponse]:
        """Devuelve todos los usuarios."""

        try:
            users = self.repository.list_all()
            return [self._to_response(user) for user in users]
        except UserRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def get_user(self, user_id: UUID) -> UserResponse:
        """Obtiene un usuario por id."""

        try:
            user = self.repository.get_by_id(user_id)
            return self._to_response(user)
        except UserNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except UserRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def update_user(self, user_id: UUID, payload: UserUpdateRequest) -> UserResponse:
        """Actualiza completamente un usuario existente."""

        try:
            updated_user = self.repository.update(user_id, payload.model_dump(mode="json"))
            return self._to_response(updated_user)
        except UserNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except UserRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def delete_user(self, user_id: UUID) -> UserDeleteResponse:
        """Elimina un usuario por su id."""

        try:
            self.repository.delete(user_id)
            return UserDeleteResponse(
                message="Usuario eliminado correctamente",
                user_id=user_id,
            )
        except UserNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except UserRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def _to_response(self, user: User) -> UserResponse:
        """Convierte la entidad de dominio a contrato público."""

        return UserResponse.model_validate(user)


def get_user_service() -> UserService:
    """Dependency helper para FastAPI."""

    return UserService()
