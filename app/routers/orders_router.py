"""Router público del módulo de pedidos."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.schemas.order import OrderCreateRequest, OrderItemResponse, OrderListResponse
from app.services.order_service import OrderService, get_order_service


orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.post("", response_model=OrderItemResponse)
def create_order(
    payload: OrderCreateRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderItemResponse:
    """Crea un pedido validando stock y calculando el total automáticamente."""

    return service.create_order(payload)


@orders_router.get("", response_model=OrderListResponse)
def list_orders(service: OrderService = Depends(get_order_service)) -> OrderListResponse:
    """Lista los pedidos existentes con sus detalles."""

    return service.list_orders()


@orders_router.get("/{order_id}", response_model=OrderItemResponse)
def get_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> OrderItemResponse:
    """Obtiene un pedido por su identificador."""

    return service.get_order(order_id)
