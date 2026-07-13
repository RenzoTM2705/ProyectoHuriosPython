"""Modelos de dominio para pagos."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

class PaymentMethod(StrEnum):
    """Métodos de pago soportados."""
    YAPE = "yape"
    CARD = "card"

class PaymentStatus(StrEnum):
    """Estados del ciclo de vida de un pago."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass(slots=True)
class Payment:
    """Entidad de dominio para pagos."""
    id: UUID
    order_id: UUID
    payment_method: PaymentMethod
    amount: Decimal
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime | None = None
    updated_at: datetime | None = None