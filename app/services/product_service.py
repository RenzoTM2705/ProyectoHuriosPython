"""Servicio de productos.

La capa de servicio valida reglas de negocio, orquesta el repositorio y traduce
errores de infraestructura a respuestas HTTP consistentes.
"""

from uuid import UUID

from fastapi import HTTPException, status

from app.models.product import Product
from app.repositories.product_repository import (
    ProductNotFoundError,
    ProductRepository,
    ProductRepositoryError,
)
from app.schemas.product import (
    ProductCreateRequest,
    ProductDeleteResponse,
    ProductItemResponse,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)


class ProductService:
    """Casos de uso para administrar productos."""

    def __init__(self, repository: ProductRepository | None = None) -> None:
        self.repository = repository or ProductRepository()

    def list_products(self) -> ProductListResponse:
        """Lista todos los productos con respuesta estructurada."""

        try:
            products = self.repository.list_all()
            return ProductListResponse(
                message="Productos obtenidos correctamente",
                data=[self._to_response(product) for product in products],
            )
        except ProductRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def get_product(self, product_id: UUID) -> ProductItemResponse:
        """Obtiene un producto por id."""

        try:
            product = self.repository.get_by_id(product_id)
            return ProductItemResponse(
                message="Producto obtenido correctamente",
                data=self._to_response(product),
            )
        except ProductNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except ProductRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def create_product(self, payload: ProductCreateRequest) -> ProductItemResponse:
        """Crea un producto nuevo."""

        try:
            product = self.repository.create(payload.model_dump(mode="json"))
            return ProductItemResponse(
                message="Producto creado correctamente",
                data=self._to_response(product),
            )
        except ProductRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def update_product(self, product_id: UUID, payload: ProductUpdateRequest) -> ProductItemResponse:
        """Actualiza completamente un producto existente."""

        try:
            product = self.repository.update(product_id, payload.model_dump(mode="json"))
            return ProductItemResponse(
                message="Producto actualizado correctamente",
                data=self._to_response(product),
            )
        except ProductNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except ProductRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def delete_product(self, product_id: UUID) -> ProductDeleteResponse:
        """Elimina un producto por id."""

        try:
            self.repository.delete(product_id)
            return ProductDeleteResponse(
                message="Producto eliminado correctamente",
                product_id=product_id,
            )
        except ProductNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except ProductRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def _to_response(self, product: Product) -> ProductResponse:
        """Convierte la entidad de dominio al contrato público."""

        return ProductResponse.model_validate(product)


def get_product_service() -> ProductService:
    """Dependency helper para FastAPI."""

    return ProductService()
