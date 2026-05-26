"""Esquemas Pydantic para pedidos."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemRequest(BaseModel):
    """Item individual solicitado dentro de un pedido."""

    model_config = ConfigDict(extra="forbid")

    product_id: UUID
    quantity: int = Field(gt=0)


class OrderCreateRequest(BaseModel):
    """Datos requeridos para crear un pedido."""

    model_config = ConfigDict(extra="forbid")

    items: list[OrderItemRequest] = Field(min_length=1)


class OrderDetailResponse(BaseModel):
    """Detalle público de un pedido."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    """Contrato público de un pedido."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    total: Decimal
    status: OrderStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None
    details: list[OrderDetailResponse]


class OrderListResponse(BaseModel):
    """Respuesta estructurada para listados de pedidos."""

    message: str
    data: list[OrderResponse]


class OrderItemResponse(BaseModel):
    """Respuesta estructurada para un pedido individual."""

    message: str
    data: OrderResponse
