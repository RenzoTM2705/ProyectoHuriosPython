"""Modelo de dominio para productos."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class ProductStatus(StrEnum):
    """Estados simples del producto para futuras extensiones."""

    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass(slots=True)
class Product:
    """Entidad de dominio para productos almacenados en Supabase."""

    id: UUID
    name: str
    description: str | None
    price: Decimal
    stock: int
    sku: str
    status: ProductStatus = ProductStatus.ACTIVE
    created_at: datetime | None = None
    updated_at: datetime | None = None
