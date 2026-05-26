"""Esquemas Pydantic para productos."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.product import ProductStatus


class ProductBaseRequest(BaseModel):
    """Datos comunes para crear y actualizar productos."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    sku: str = Field(min_length=3, max_length=64)
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        """Normaliza el SKU para mantener consistencia en la base."""

        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("El SKU es obligatorio")
        return normalized


class ProductCreateRequest(ProductBaseRequest):
    """Payload para crear un producto."""


class ProductUpdateRequest(ProductBaseRequest):
    """Payload para actualizar un producto completo."""


class ProductResponse(BaseModel):
    """Contrato público de un producto."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    price: Decimal
    stock: int
    sku: str
    status: ProductStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProductDeleteResponse(BaseModel):
    """Respuesta estándar al eliminar un producto."""

    message: str
    product_id: UUID


class ProductListResponse(BaseModel):
    """Respuesta estructurada para listados."""

    message: str
    data: list[ProductResponse]


class ProductItemResponse(BaseModel):
    """Respuesta estructurada para recursos únicos."""

    message: str
    data: ProductResponse
