"""Esquemas Pydantic para carrito de compras."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CartAddItemRequest(BaseModel):
    """Payload para agregar productos al carrito."""

    model_config = ConfigDict(extra="forbid")

    product_id: UUID
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    """Representación pública de un item del carrito."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cart_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class CartResponse(BaseModel):
    """Representación pública del carrito."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    total_amount: Decimal
    total_items: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    items: list[CartItemResponse]


class CartViewResponse(BaseModel):
    """Respuesta estructurada del carrito."""

    message: str
    data: CartResponse


class CartActionResponse(BaseModel):
    """Respuesta estructurada para acciones del carrito."""

    message: str
    data: CartResponse | None = None
