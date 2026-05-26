"""Router público del carrito de compras."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.config.security import get_authenticated_user_id
from app.schemas.cart import CartActionResponse, CartAddItemRequest, CartViewResponse
from app.services.cart_service import CartService, get_cart_service


cart_router = APIRouter(prefix="/cart", tags=["Cart"])


@cart_router.post("/add", response_model=CartViewResponse)
def add_item(
    payload: CartAddItemRequest,
    user_id: UUID = Depends(get_authenticated_user_id),
    service: CartService = Depends(get_cart_service),
) -> CartViewResponse:
    """Agrega un producto al carrito del usuario autenticado."""

    return service.add_item(user_id, payload)


@cart_router.delete("/remove/{product_id}", response_model=CartViewResponse)
def remove_item(
    product_id: UUID,
    user_id: UUID = Depends(get_authenticated_user_id),
    service: CartService = Depends(get_cart_service),
) -> CartViewResponse:
    """Elimina un producto del carrito del usuario autenticado."""

    return service.remove_item(user_id, product_id)


@cart_router.get("", response_model=CartViewResponse)
def get_cart(
    user_id: UUID = Depends(get_authenticated_user_id),
    service: CartService = Depends(get_cart_service),
) -> CartViewResponse:
    """Obtiene el carrito completo del usuario autenticado."""

    return service.get_cart(user_id)


@cart_router.delete("/clear", response_model=CartActionResponse)
def clear_cart(
    user_id: UUID = Depends(get_authenticated_user_id),
    service: CartService = Depends(get_cart_service),
) -> CartActionResponse:
    """Vacía por completo el carrito del usuario autenticado."""

    return service.clear_cart(user_id)
