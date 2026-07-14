"""Modelos de dominio para pedidos."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

class OrderStatus(StrEnum):
    """Estados básicos del pedido para futuras ampliaciones."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

@dataclass(slots=True)
class OrderDetail:
    """Detalle de un pedido asociado a un producto concreto."""
    id: UUID
    order_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

@dataclass(slots=True)
class Order:
    """Entidad de dominio para pedidos."""
    id: UUID
    user_id: UUID
    total: Decimal
    status: OrderStatus = OrderStatus.PENDING
    invoice_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    details: list[OrderDetail] = field(default_factory=list)