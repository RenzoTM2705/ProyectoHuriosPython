"""Repositorio de productos usando Supabase PostgreSQL.

La capa de infraestructura encapsula la tabla `products` y traduce datos crudos
del SDK a entidades del dominio.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.models.product import Product, ProductStatus
from app.repositories.base_repository import BaseRepository


class ProductRepositoryError(Exception):
    """Error de persistencia para productos."""


class ProductNotFoundError(ProductRepositoryError):
    """Señala que el producto solicitado no existe."""


class ProductRepository(BaseRepository):
    """Acceso a la tabla `products` de Supabase."""

    table_name = "products"

    def list_all(self) -> list[Product]:
        """Lista productos ordenados por creación descendente."""

        try:
            response = self.client.table(self.table_name).select("*").order("created_at", desc=True).execute()
            return [self._to_product(row) for row in self._extract_rows(response)]
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise ProductRepositoryError(self._normalize_error(exc)) from exc

    def get_by_id(self, product_id: UUID) -> Product:
        """Obtiene un producto por su identificador."""

        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("id", str(product_id))
                .limit(1)
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise ProductNotFoundError(f"Producto {product_id} no encontrado")
            return self._to_product(rows[0])
        except ProductNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise ProductRepositoryError(self._normalize_error(exc)) from exc

    def create(self, payload: dict[str, object]) -> Product:
        """Crea un producto y devuelve el registro persistido."""

        try:
            data = dict(payload)
            data.setdefault("id", str(uuid4()))
            data["created_at"] = datetime.now(UTC).isoformat()
            data["updated_at"] = datetime.now(UTC).isoformat()

            response = self.client.table(self.table_name).insert(data).execute()
            rows = self._extract_rows(response)
            if not rows:
                raise ProductRepositoryError("Supabase no devolvió el producto creado")
            return self._to_product(rows[0])
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise ProductRepositoryError(self._normalize_error(exc)) from exc

    def update(self, product_id: UUID, payload: dict[str, object]) -> Product:
        """Actualiza un producto existente."""

        try:
            data = dict(payload)
            data["updated_at"] = datetime.now(UTC).isoformat()

            response = (
                self.client.table(self.table_name)
                .update(data)
                .select("*")
                .eq("id", str(product_id))
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise ProductNotFoundError(f"Producto {product_id} no encontrado")
            return self._to_product(rows[0])
        except ProductNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise ProductRepositoryError(self._normalize_error(exc)) from exc

    def delete(self, product_id: UUID) -> None:
        """Elimina un producto por su identificador."""

        try:
            response = (
                self.client.table(self.table_name)
                .delete()
                .select("*")
                .eq("id", str(product_id))
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise ProductNotFoundError(f"Producto {product_id} no encontrado")
        except ProductNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise ProductRepositoryError(self._normalize_error(exc)) from exc

    def update_stock(self, product_id: UUID, new_stock: int) -> Product:
        """Actualiza el stock de un producto y devuelve el registro persistido."""

        try:
            response = (
                self.client.table(self.table_name)
                .update({"stock": new_stock, "updated_at": datetime.now(UTC).isoformat()})
                .select("*")
                .eq("id", str(product_id))
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise ProductNotFoundError(f"Producto {product_id} no encontrado")
            return self._to_product(rows[0])
        except ProductNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise ProductRepositoryError(self._normalize_error(exc)) from exc

    def _to_product(self, row: Mapping[str, object]) -> Product:
        """Convierte una fila de Supabase en un producto de dominio."""

        return Product(
            id=UUID(str(row.get("id"))),
            name=str(row.get("name", "")),
            description=row.get("description") if row.get("description") is not None else None,
            price=Decimal(str(row.get("price", "0"))),
            stock=int(row.get("stock", 0)),
            sku=str(row.get("sku", "")),
            status=ProductStatus(str(row.get("status", ProductStatus.ACTIVE))),
            created_at=self._parse_datetime(row.get("created_at")),
            updated_at=self._parse_datetime(row.get("updated_at")),
        )

    def _normalize_error(self, exc: Exception) -> str:
        """Genera un mensaje seguro y legible para la capa de servicio."""

        return super()._normalize_error(exc, "Error inesperado en el repositorio de productos")
