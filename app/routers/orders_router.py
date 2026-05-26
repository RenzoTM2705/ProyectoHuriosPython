"""Router público del módulo de pedidos."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, require_admin_user, require_order_owner_or_admin
from app.models.auth import AuthenticatedUser
from app.schemas.order import OrderCreateRequest, OrderItemResponse, OrderListResponse
from app.services.order_service import OrderService, get_order_service


orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.post("", response_model=OrderItemResponse)
def create_order(
    payload: OrderCreateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderItemResponse:
    """Crea un pedido validando stock y calculando el total automáticamente."""

    return service.create_order(current_user.id, payload)


@orders_router.get("", response_model=OrderListResponse, dependencies=[Depends(require_admin_user)])
def list_orders(service: OrderService = Depends(get_order_service)) -> OrderListResponse:
    """Lista los pedidos existentes con sus detalles."""

    return service.list_orders()


@orders_router.get("/{order_id}", response_model=OrderItemResponse, dependencies=[Depends(require_order_owner_or_admin)])
def get_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> OrderItemResponse:
    """Obtiene un pedido por su identificador si pertenece al usuario o es admin."""

    return service.get_order(order_id)
