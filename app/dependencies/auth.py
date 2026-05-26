"""Dependencias de autenticación y autorización.

Valida JWT de Supabase, resuelve el usuario autenticado desde la tabla de
usuarios y expone helpers reutilizables para control de acceso por rol y
propiedad del recurso.
"""

from __future__ import annotations

from typing import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.config.security import decode_supabase_jwt, get_bearer_token
from app.models.auth import AuthenticatedUser
from app.models.user import UserRole
from app.repositories.order_repository import OrderNotFoundError, OrderRepository, OrderRepositoryError
from app.repositories.user_repository import UserNotFoundError, UserRepository, UserRepositoryError


def get_current_user(token: str = Depends(get_bearer_token)) -> AuthenticatedUser:
    """Devuelve el usuario autenticado a partir del JWT de Supabase."""

    claims = decode_supabase_jwt(token)
    subject = claims.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = UserRepository().get_by_id(UUID(str(subject)))
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado",
        ) from exc
    except UserRepositoryError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        role=user.role,
        token=token,
        claims=claims,
    )


def require_role(*allowed_roles: UserRole) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    """Construye una dependencia para validar roles permitidos."""

    def dependency(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado",
            )
        return current_user

    return dependency


require_admin_user = require_role(UserRole.ADMIN)
require_customer_user = require_role(UserRole.CUSTOMER)
require_customer_or_admin_user = require_role(UserRole.ADMIN, UserRole.CUSTOMER)


def require_order_owner_or_admin(order_id: UUID, current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    """Permite acceso solo al dueño del pedido o a un administrador."""

    if current_user.role == UserRole.ADMIN:
        return current_user

    try:
        order = OrderRepository().get_by_id(order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado",
        ) from exc
    except OrderRepositoryError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado",
        )

    return current_user


def require_cart_owner_or_admin(user_id: UUID, current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    """Permite acceso solo al dueño del carrito o a un administrador."""

    if current_user.role == UserRole.ADMIN or current_user.id == user_id:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso denegado",
    )
