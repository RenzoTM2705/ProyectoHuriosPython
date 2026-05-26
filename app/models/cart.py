"""Modelos de dominio para carrito de compras."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class CartItem:
    """Elemento individual de un carrito."""

    id: UUID
    cart_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


@dataclass(slots=True)
class Cart:
    """Carrito de compras asociado a un usuario autenticado."""

    id: UUID
    user_id: UUID
    total_amount: Decimal = Decimal("0")
    total_items: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    items: list[CartItem] = field(default_factory=list)
