"""Router público del módulo de pagos."""

from uuid import UUID
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user, require_admin_user
from app.models.auth import AuthenticatedUser
from app.schemas.payment import (
    PaymentCheckoutRequest,
    PaymentProcessRequest,
    PaymentRefundRequest,
    PaymentItemResponse,
    PaymentListResponse
)
from app.services.payment_service import PaymentService, get_payment_service

payment_router = APIRouter(prefix="/payments", tags=["Payments"])

@payment_router.post("/checkout", response_model=PaymentItemResponse)
def checkout(
    payload: PaymentCheckoutRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentItemResponse:
    """Valida stock, crea la orden, descuenta inventario e inicializa el pago."""
    return service.checkout(current_user.id, payload)

@payment_router.post("/process", response_model=PaymentItemResponse)
def process_payment(
    payload: PaymentProcessRequest,
    _current_user: AuthenticatedUser = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentItemResponse:
    """Procesa la transacción y confirma la orden."""
    return service.process_payment(payload)

@payment_router.get("/history", response_model=PaymentListResponse)
def get_history(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentListResponse:
    """Obtiene el historial de pagos del usuario autenticado."""
    return service.get_history(current_user.id)

@payment_router.get("/{payment_id}", response_model=PaymentItemResponse)
def get_payment(
    payment_id: UUID,
    _current_user: AuthenticatedUser = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentItemResponse:
    """Consulta los detalles de un pago específico."""
    return service.get_payment(payment_id)

@payment_router.post("/refund", response_model=PaymentItemResponse, dependencies=[Depends(require_admin_user)])
def refund_payment(
    payload: PaymentRefundRequest,
    service: PaymentService = Depends(get_payment_service),
) -> PaymentItemResponse:
    """(Admin) Reembolsa un pago procesado y cancela la orden."""
    return service.refund_payment(payload)