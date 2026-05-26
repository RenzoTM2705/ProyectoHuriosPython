"""Router público del carrito de compras."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies.auth import require_cart_owner_or_admin, require_customer_or_admin_user
from app.models.auth import AuthenticatedUser
from app.schemas.cart import CartActionResponse, CartAddItemRequest, CartViewResponse
from app.services.cart_service import CartService, get_cart_service


cart_router = APIRouter(prefix="/cart", tags=["Cart"])


@cart_router.post("/add", response_model=CartViewResponse)
def add_item(
    payload: CartAddItemRequest,
    current_user: AuthenticatedUser = Depends(require_customer_or_admin_user),
    service: CartService = Depends(get_cart_service),
) -> CartViewResponse:
    """Agrega un producto al carrito del usuario autenticado."""

    return service.add_item(current_user.id, payload)


@cart_router.delete("/remove/{product_id}", response_model=CartViewResponse)
def remove_item(
    product_id: UUID,
    current_user: AuthenticatedUser = Depends(require_customer_or_admin_user),
    service: CartService = Depends(get_cart_service),
) -> CartViewResponse:
    """Elimina un producto del carrito del usuario autenticado."""

    return service.remove_item(current_user.id, product_id)


@cart_router.get("", response_model=CartViewResponse)
def get_cart(
    current_user: AuthenticatedUser = Depends(require_customer_or_admin_user),
    service: CartService = Depends(get_cart_service),
) -> CartViewResponse:
    """Obtiene el carrito completo del usuario autenticado."""

    return service.get_cart(current_user.id)


@cart_router.get("/{user_id}", response_model=CartViewResponse)
def get_cart_by_user(
    user_id: UUID,
    _current_user: AuthenticatedUser = Depends(require_cart_owner_or_admin),
    service: CartService = Depends(get_cart_service),
) -> CartViewResponse:
    """Obtiene el carrito de un usuario concreto si es dueño o admin."""

    return service.get_cart(user_id)


@cart_router.delete("/clear", response_model=CartActionResponse)
def clear_cart(
    current_user: AuthenticatedUser = Depends(require_customer_or_admin_user),
    service: CartService = Depends(get_cart_service),
) -> CartActionResponse:
    """Vacía por completo el carrito del usuario autenticado."""

    return service.clear_cart(current_user.id)


@cart_router.delete("/{user_id}/clear", response_model=CartActionResponse)
def clear_cart_by_user(
    user_id: UUID,
    _current_user: AuthenticatedUser = Depends(require_cart_owner_or_admin),
    service: CartService = Depends(get_cart_service),
) -> CartActionResponse:
    """Vacía el carrito de un usuario concreto si es dueño o admin."""

    return service.clear_cart(user_id)
