"""Servicio del carrito de compras.

Gestiona el cálculo de subtotales, la validación de stock y la asociación del
carrito al usuario autenticado proveniente del JWT de Supabase.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException, status

from app.models.cart import Cart
from app.models.product import Product
from app.repositories.cart_repository import CartNotFoundError, CartRepository, CartRepositoryError
from app.repositories.product_repository import ProductNotFoundError, ProductRepository, ProductRepositoryError
from app.schemas.cart import (
    CartActionResponse,
    CartAddItemRequest,
    CartItemResponse,
    CartResponse,
    CartViewResponse,
)


class CartService:
    """Casos de uso del carrito de compras."""

    def __init__(
        self,
        cart_repository: CartRepository | None = None,
        product_repository: ProductRepository | None = None,
    ) -> None:
        self.cart_repository = cart_repository or CartRepository()
        self.product_repository = product_repository or ProductRepository()

    def add_item(self, user_id: UUID, payload: CartAddItemRequest) -> CartViewResponse:
        """Agrega un producto al carrito del usuario autenticado."""

        try:
            cart = self.cart_repository.get_or_create_cart(user_id)
            product = self.product_repository.get_by_id(payload.product_id)
            existing_item = self.cart_repository.get_item_by_product_id(cart.id, product.id)

            current_quantity = existing_item.quantity if existing_item else 0
            new_quantity = current_quantity + payload.quantity

            if new_quantity > product.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para el producto {product.name}",
                )

            subtotal = self._money(product.price * Decimal(new_quantity))
            item_payload = {
                "cart_id": str(cart.id),
                "product_id": str(product.id),
                "product_name": product.name,
                "quantity": new_quantity,
                "unit_price": product.price,
                "subtotal": subtotal,
            }

            if existing_item is None:
                self.cart_repository.add_item(item_payload)
            else:
                self.cart_repository.update_item(existing_item.id, item_payload)

            return self._build_view(user_id, "Producto agregado al carrito correctamente")
        except ProductNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except (CartRepositoryError, ProductRepositoryError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def remove_item(self, user_id: UUID, product_id: UUID) -> CartViewResponse:
        """Elimina un producto del carrito del usuario autenticado."""

        try:
            cart = self.cart_repository.get_or_create_cart(user_id)
            self.cart_repository.delete_item_by_product_id(cart.id, product_id)
            return self._build_view(user_id, "Producto eliminado del carrito correctamente")
        except CartRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def get_cart(self, user_id: UUID) -> CartViewResponse:
        """Obtiene el carrito completo del usuario autenticado."""

        try:
            cart = self.cart_repository.get_or_create_cart(user_id)
            return CartViewResponse(
                message="Carrito obtenido correctamente",
                data=self._to_response(cart),
            )
        except CartRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def clear_cart(self, user_id: UUID) -> CartActionResponse:
        """Vacía por completo el carrito del usuario autenticado."""

        try:
            cart = self.cart_repository.get_or_create_cart(user_id)
            self.cart_repository.clear_cart(cart.id)
            self.cart_repository.update_cart_totals(cart.id, Decimal("0"), 0)
            return CartActionResponse(message="Carrito vaciado correctamente")
        except CartRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def _build_view(self, user_id: UUID, message: str) -> CartViewResponse:
        """Construye una vista limpia del carrito después de una mutación."""

        cart = self.cart_repository.get_or_create_cart(user_id)
        cart = self._recalculate_cart(cart)
        return CartViewResponse(message=message, data=self._to_response(cart))

    def _recalculate_cart(self, cart: Cart) -> Cart:
        """Recalcula totales y subtotales del carrito desde los items persistidos."""

        items = self.cart_repository.list_items(cart.id)
        total_amount = sum((item.subtotal for item in items), Decimal("0"))
        total_items = sum(item.quantity for item in items)
        return self.cart_repository.update_cart_totals(cart.id, self._money(total_amount), total_items)

    def _to_response(self, cart: Cart) -> CartResponse:
        """Convierte el modelo de dominio a contrato público."""

        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            total_amount=self._money(cart.total_amount),
            total_items=cart.total_items,
            created_at=cart.created_at,
            updated_at=cart.updated_at,
            items=[
                CartItemResponse(
                    id=item.id,
                    cart_id=item.cart_id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=self._money(item.unit_price),
                    subtotal=self._money(item.subtotal),
                )
                for item in cart.items
            ],
        )

    def _money(self, value: Decimal) -> Decimal:
        """Normaliza montos a dos decimales."""

        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_cart_service() -> CartService:
    """Dependency helper para FastAPI."""

    return CartService()
