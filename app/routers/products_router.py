"""Router público del módulo de productos."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.schemas.product import (
    ProductCreateRequest,
    ProductDeleteResponse,
    ProductItemResponse,
    ProductListResponse,
    ProductUpdateRequest,
)
from app.services.product_service import ProductService, get_product_service


products_router = APIRouter(prefix="/products", tags=["Products"])


@products_router.get("", response_model=ProductListResponse)
def list_products(service: ProductService = Depends(get_product_service)) -> ProductListResponse:
    """Lista todos los productos almacenados en Supabase."""

    return service.list_products()


@products_router.get("/{product_id}", response_model=ProductItemResponse)
def get_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
) -> ProductItemResponse:
    """Obtiene un producto por id."""

    return service.get_product(product_id)


@products_router.post("", response_model=ProductItemResponse)
def create_product(
    payload: ProductCreateRequest,
    service: ProductService = Depends(get_product_service),
) -> ProductItemResponse:
    """Crea un producto nuevo."""

    return service.create_product(payload)


@products_router.put("/{product_id}", response_model=ProductItemResponse)
def update_product(
    product_id: UUID,
    payload: ProductUpdateRequest,
    service: ProductService = Depends(get_product_service),
) -> ProductItemResponse:
    """Actualiza completamente un producto existente."""

    return service.update_product(product_id, payload)


@products_router.delete("/{product_id}", response_model=ProductDeleteResponse)
def delete_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
) -> ProductDeleteResponse:
    """Elimina un producto por id."""

    return service.delete_product(product_id)
