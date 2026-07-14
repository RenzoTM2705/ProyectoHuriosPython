"""Router público del módulo de pedidos."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, require_admin_user, require_order_owner_or_admin
from app.models.auth import AuthenticatedUser
from app.schemas.order import OrderCreateRequest, OrderItemResponse, OrderListResponse
from app.schemas.invoice import InvoiceResponse
from app.services.order_service import OrderService, get_order_service
from app.services.invoice_service import InvoiceService, get_invoice_service


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


@orders_router.get("/{order_id}/invoice", response_model=InvoiceResponse, dependencies=[Depends(require_order_owner_or_admin)])
def get_order_invoice(
    order_id: UUID,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceResponse:
    """Obtiene o genera (si no existe) la factura/boleta PDF del pedido especificado."""
    return service.get_or_generate_invoice(order_id)