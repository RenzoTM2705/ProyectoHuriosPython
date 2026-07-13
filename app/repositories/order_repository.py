"""Repositorio de pedidos sobre Supabase PostgreSQL."""

from __future__ import annotations
from datetime import UTC, datetime
from decimal import Decimal
from typing import Mapping
from uuid import UUID, uuid4

from app.models.order import Order, OrderDetail, OrderStatus
from app.repositories.base_repository import BaseRepository

class OrderRepositoryError(Exception):
    """Error de persistencia de pedidos."""

class OrderNotFoundError(OrderRepositoryError):
    """Señala que el pedido solicitado no existe."""

class OrderRepository(BaseRepository):
    """Acceso a las tablas `orders` y `order_details`."""
    orders_table = "orders"
    details_table = "order_details"

    def list_all(self) -> list[Order]:
        """Lista pedidos con sus detalles."""
        try:
            response = self.client.table(self.orders_table).select("*").order("created_at", desc=True).execute()
            orders = [self._to_order(row) for row in self._extract_rows(response)]
            return [self._attach_details(order) for order in orders]
        except Exception as exc:
            raise OrderRepositoryError(self._normalize_error(exc)) from exc

    def get_by_id(self, order_id: UUID) -> Order:
        """Obtiene un pedido por su identificador."""
        try:
            response = (
                self.client.table(self.orders_table)
                .select("*")
                .eq("id", str(order_id))
                .limit(1)
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise OrderNotFoundError(f"Pedido {order_id} no encontrado")
            return self._attach_details(self._to_order(rows[0]))
        except OrderNotFoundError:
            raise
        except Exception as exc:
            raise OrderRepositoryError(self._normalize_error(exc)) from exc

    def create_order(self, payload: dict[str, object]) -> Order:
        """Crea el encabezado del pedido."""
        try:
            data = dict(payload)
            data.setdefault("id", str(uuid4()))
            data["created_at"] = datetime.now(UTC).isoformat()
            data["updated_at"] = datetime.now(UTC).isoformat()
            response = self.client.table(self.orders_table).insert(data).execute()
            rows = self._extract_rows(response)
            if not rows:
                raise OrderRepositoryError("Supabase no devolvió el pedido creado")
            return self._to_order(rows[0])
        except Exception as exc:
            raise OrderRepositoryError(self._normalize_error(exc)) from exc

    def create_details(self, payload: list[dict[str, object]]) -> list[OrderDetail]:
        """Crea los detalles del pedido en lote."""
        try:
            response = self.client.table(self.details_table).insert(payload).execute()
            return [self._to_detail(row) for row in self._extract_rows(response)]
        except Exception as exc:
            raise OrderRepositoryError(self._normalize_error(exc)) from exc

    def get_details_by_order_id(self, order_id: UUID) -> list[OrderDetail]:
        """Obtiene los detalles asociados a un pedido."""
        try:
            response = (
                self.client.table(self.details_table)
                .select("*")
                .eq("order_id", str(order_id))
                .order("created_at", desc=False)
                .execute()
            )
            return [self._to_detail(row) for row in self._extract_rows(response)]
        except Exception as exc:
            raise OrderRepositoryError(self._normalize_error(exc)) from exc

    def update_invoice_url(self, order_id: UUID, invoice_url: str) -> None:
        """Actualiza la URL de la factura PDF generada."""
        try:
            self.client.table(self.orders_table).update({"invoice_url": invoice_url}).eq("id", str(order_id)).execute()
        except Exception as exc:
            raise OrderRepositoryError(self._normalize_error(exc)) from exc

    def delete_details_by_order_id(self, order_id: UUID) -> None:
        """Elimina todos los detalles de un pedido."""
        try:
            self.client.table(self.details_table).delete().eq("order_id", str(order_id)).execute()
        except Exception as exc:
            raise OrderRepositoryError(self._normalize_error(exc)) from exc

    def delete_order(self, order_id: UUID) -> None:
        """Elimina el pedido principal."""
        try:
            self.client.table(self.orders_table).delete().eq("id", str(order_id)).execute()
        except Exception as exc:
            raise OrderRepositoryError(self._normalize_error(exc)) from exc

    def _attach_details(self, order: Order) -> Order:
        """Carga los detalles y devuelve el pedido completo."""
        order.details = self.get_details_by_order_id(order.id)
        return order

    def _to_order(self, row: Mapping[str, object]) -> Order:
        """Convierte una fila de Supabase en un pedido del dominio."""
        return Order(
            id=UUID(str(row.get("id"))),
            user_id=UUID(str(row.get("user_id"))),
            total=Decimal(str(row.get("total", "0"))),
            status=OrderStatus(str(row.get("status", OrderStatus.PENDING))),
            invoice_url=str(row.get("invoice_url", "")) if row.get("invoice_url") else None,
            created_at=self._parse_datetime(row.get("created_at")),
            updated_at=self._parse_datetime(row.get("updated_at")),
        )

    def _to_detail(self, row: Mapping[str, object]) -> OrderDetail:
        """Convierte una fila de Supabase en un detalle de pedido."""
        return OrderDetail(
            id=UUID(str(row.get("id"))),
            order_id=UUID(str(row.get("order_id"))),
            product_id=UUID(str(row.get("product_id"))),
            product_name=str(row.get("product_name", "")),
            quantity=int(row.get("quantity", 0)),
            unit_price=Decimal(str(row.get("unit_price", "0"))),
            subtotal=Decimal(str(row.get("subtotal", "0"))),
        )

    def _normalize_error(self, exc: Exception) -> str:
        """Genera un mensaje seguro y legible para la capa de servicio."""
        return super()._normalize_error(exc, "Error inesperado en el repositorio de pedidos")