"""Servicio de pedidos.

Aquí se aplican las reglas de negocio: validación de stock, cálculo del total,
creación del pedido y manejo compensatorio ante fallos de persistencia.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException, status

from app.models.order import Order
from app.models.product import Product
from app.repositories.order_repository import OrderNotFoundError, OrderRepository, OrderRepositoryError
from app.repositories.product_repository import ProductNotFoundError, ProductRepository, ProductRepositoryError
from app.schemas.order import (
    OrderCreateRequest,
    OrderDetailResponse,
    OrderItemRequest,
    OrderItemResponse,
    OrderListResponse,
    OrderResponse,
)


@dataclass(slots=True)
class _ValidatedLine:
    """Representa una línea validada para el cálculo del pedido."""

    product: Product
    quantity: int


class OrderService:
    """Casos de uso para administrar pedidos."""

    def __init__(
        self,
        order_repository: OrderRepository | None = None,
        product_repository: ProductRepository | None = None,
    ) -> None:
        self.order_repository = order_repository or OrderRepository()
        self.product_repository = product_repository or ProductRepository()

    def list_orders(self) -> OrderListResponse:
        """Lista pedidos con detalle."""

        try:
            orders = self.order_repository.list_all()
            return OrderListResponse(
                message="Pedidos obtenidos correctamente",
                data=[self._to_response(order) for order in orders],
            )
        except OrderRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def get_order(self, order_id: UUID) -> OrderItemResponse:
        """Obtiene un pedido por su identificador."""

        try:
            order = self.order_repository.get_by_id(order_id)
            return OrderItemResponse(
                message="Pedido obtenido correctamente",
                data=self._to_response(order),
            )
        except OrderNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except OrderRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    def create_order(self, current_user_id: UUID, payload: OrderCreateRequest) -> OrderItemResponse:
        """Crea un pedido validando stock y calculando el total automáticamente."""

        validated_lines = self._validate_and_group_items(payload.items)
        stock_snapshot: dict[UUID, int] = {}
        created_order = None

        try:
            for line in validated_lines:
                stock_snapshot[line.product.id] = line.product.stock

            order_total = self._calculate_total(validated_lines)
            created_order = self.order_repository.create_order(
                {
                    "user_id": str(current_user_id),
                    "total": order_total,
                    "status": "pending",
                }
            )

            detail_payload = [
                {
                    "order_id": str(created_order.id),
                    "product_id": str(line.product.id),
                    "product_name": line.product.name,
                    "quantity": line.quantity,
                    "unit_price": line.product.price,
                    "subtotal": self._money(line.product.price * Decimal(line.quantity)),
                }
                for line in validated_lines
            ]

            details = self.order_repository.create_details(detail_payload)
            if len(details) != len(detail_payload):
                raise OrderRepositoryError("No se pudieron crear todos los detalles del pedido")

            for line in validated_lines:
                new_stock = line.product.stock - line.quantity
                self.product_repository.update_stock(line.product.id, new_stock)

            order = self.order_repository.get_by_id(created_order.id)
            order.details = details

            return OrderItemResponse(
                message="Pedido creado correctamente",
                data=self._to_response(order),
            )
        except (ProductNotFoundError, ProductRepositoryError) as exc:
            self._rollback_order(created_order, stock_snapshot)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except OrderRepositoryError as exc:
            self._rollback_order(created_order, stock_snapshot)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except HTTPException:
            self._rollback_order(created_order, stock_snapshot)
            raise
        except Exception as exc:  # pragma: no cover - fallback de seguridad
            self._rollback_order(created_order, stock_snapshot)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No fue posible crear el pedido",
            ) from exc

    def _validate_and_group_items(self, items: list[OrderItemRequest]) -> list[_ValidatedLine]:
        """Agrupa cantidades repetidas por producto y valida stock disponible."""

        grouped: dict[UUID, int] = defaultdict(int)
        for item in items:
            grouped[item.product_id] += item.quantity

        validated_lines: list[_ValidatedLine] = []
        for product_id, quantity in grouped.items():
            try:
                product = self.product_repository.get_by_id(product_id)
            except ProductNotFoundError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El producto {product_id} no existe",
                ) from exc
            except ProductRepositoryError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=str(exc),
                ) from exc

            if quantity > product.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para el producto {product.name}",
                )

            validated_lines.append(_ValidatedLine(product=product, quantity=quantity))

        return validated_lines

    def _calculate_total(self, validated_lines: list[_ValidatedLine]) -> Decimal:
        """Calcula el total del pedido con precisión monetaria."""

        total = sum((line.product.price * Decimal(line.quantity) for line in validated_lines), Decimal("0"))
        return self._money(total)

    def _money(self, value: Decimal) -> Decimal:
        """Normaliza valores monetarios a dos decimales."""

        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _rollback_order(self, order: Order | None, stock_snapshot: dict[UUID, int]) -> None:
        """Revierte efectos parciales cuando alguna operación falla.

        Supabase no está siendo usado aquí como transacción distribuida, así que
        la compensación explícita evita dejar stock o pedidos a medio camino.
        """

        if order is None:
            return

        try:
            self.order_repository.delete_details_by_order_id(order.id)
        except Exception:
            pass

        for product_id, original_stock in stock_snapshot.items():
            try:
                self.product_repository.update_stock(product_id, original_stock)
            except Exception:
                pass

        try:
            self.order_repository.delete_order(order.id)
        except Exception:
            pass

    def _to_response(self, order: Order) -> OrderResponse:
        """Convierte la entidad de dominio al contrato público."""

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total=self._money(order.total),
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
            details=[
                OrderDetailResponse(
                    id=detail.id,
                    order_id=detail.order_id,
                    product_id=detail.product_id,
                    product_name=detail.product_name,
                    quantity=detail.quantity,
                    unit_price=self._money(detail.unit_price),
                    subtotal=self._money(detail.subtotal),
                )
                for detail in order.details
            ],
        )


def get_order_service() -> OrderService:
    """Dependency helper para FastAPI."""

    return OrderService()
