"""Esquemas Pydantic para el módulo de pagos."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.payment import PaymentMethod, PaymentStatus
from app.schemas.order import OrderItemRequest

class PaymentCheckoutRequest(BaseModel):
    """Payload para iniciar el proceso de checkout completo."""
    model_config = ConfigDict(extra="forbid")
    items: list[OrderItemRequest] = Field(min_length=1)
    payment_method: PaymentMethod

class PaymentProcessRequest(BaseModel):
    """Payload para procesar una transacción específica."""
    model_config = ConfigDict(extra="forbid")
    payment_id: UUID
    transaction_token: str = Field(min_length=5, description="Token de MercadoPago o Culqi")

class PaymentRefundRequest(BaseModel):
    """Payload para reembolsos."""
    model_config = ConfigDict(extra="forbid")
    payment_id: UUID
    reason: str = Field(min_length=10, max_length=255)

class PaymentResponse(BaseModel):
    """Contrato público de un pago."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    order_id: UUID
    payment_method: PaymentMethod
    amount: Decimal
    status: PaymentStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None

class PaymentListResponse(BaseModel):
    """Respuesta estructurada para el historial de pagos."""
    message: str
    data: list[PaymentResponse]

class PaymentItemResponse(BaseModel):
    """Respuesta estructurada para un pago único."""
    message: str
    data: PaymentResponse