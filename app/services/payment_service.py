"""Servicio de Pagos. Orquesta la validación de stock, generación de órdenes y transacciones financieras."""

from __future__ import annotations
from uuid import UUID
from fastapi import HTTPException, status
from app.models.payment import PaymentMethod, PaymentStatus
from app.repositories.payment_repository import PaymentRepository, PaymentRepositoryError, PaymentNotFoundError
from app.repositories.order_repository import OrderRepository
from app.schemas.payment import (
    PaymentCheckoutRequest,
    PaymentProcessRequest,
    PaymentRefundRequest,
    PaymentItemResponse,
    PaymentListResponse,
    PaymentResponse
)
from app.schemas.order import OrderCreateRequest
from app.services.order_service import OrderService

class PaymentService:
    """Casos de uso para el procesamiento de pagos."""

    def __init__(
        self, 
        payment_repository: PaymentRepository | None = None,
        order_service: OrderService | None = None,
        order_repository: OrderRepository | None = None
    ) -> None:
        self.repository = payment_repository or PaymentRepository()
        self.order_service = order_service or OrderService()
        self.order_repository = order_repository or OrderRepository()

    def checkout(self, user_id: UUID, payload: PaymentCheckoutRequest) -> PaymentItemResponse:
        """Crea la orden (validando/descontando stock) e inicializa el pago."""
        try:
            order_request = OrderCreateRequest(items=payload.items)
            order_result = self.order_service.create_order(user_id, order_request)
            
            payment_data = {
                "order_id": str(order_result.data.id),
                "payment_method": payload.payment_method.value,
                "amount": order_result.data.total,
                "status": PaymentStatus.PENDING.value
            }
            payment = self.repository.create(payment_data)

            return PaymentItemResponse(
                message="Checkout inicializado correctamente",
                data=self._to_response(payment)
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fallo crítico en el checkout: {str(exc)}"
            ) from exc

    def process_payment(self, payload: PaymentProcessRequest) -> PaymentItemResponse:
        """Procesa el pago con la pasarela y confirma la orden, generando la factura."""
        try:
            payment = self.repository.get_by_id(payload.payment_id)
            if payment.status != PaymentStatus.PENDING:
                raise HTTPException(status_code=400, detail="El pago ya fue procesado o cancelado")
            
            # Procesamiento de pasarela (Culqi/MercadoPago irían aquí)
            
            updated_payment = self.repository.update_status(payment.id, PaymentStatus.COMPLETED)
            
            # Actualizamos el estado a confirmado
            self.order_repository.client.table("orders").update({"status": "confirmed"}).eq("id", str(payment.order_id)).execute()

            # --- NUEVO: Generar el PDF automáticamente ---
            from app.services.invoice_service import InvoiceService
            invoice_service = InvoiceService(order_repository=self.order_repository)
            invoice_service.get_or_generate_invoice(payment.order_id)
            # ---------------------------------------------

            return PaymentItemResponse(
                message="Pago procesado exitosamente y factura generada",
                data=self._to_response(updated_payment)
            )
        except PaymentNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except PaymentRepositoryError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    def get_history(self, user_id: UUID) -> PaymentListResponse:
        """Devuelve el historial de pagos del usuario."""
        try:
            payments = self.repository.list_by_user(user_id)
            return PaymentListResponse(
                message="Historial de pagos recuperado",
                data=[self._to_response(p) for p in payments]
            )
        except PaymentRepositoryError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    def get_payment(self, payment_id: UUID) -> PaymentItemResponse:
        """Consulta un pago individual."""
        try:
            payment = self.repository.get_by_id(payment_id)
            return PaymentItemResponse(
                message="Pago obtenido correctamente",
                data=self._to_response(payment)
            )
        except PaymentNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    def refund_payment(self, payload: PaymentRefundRequest) -> PaymentItemResponse:
        """Procesa el reembolso de un pago."""
        try:
            payment = self.repository.get_by_id(payload.payment_id)
            if payment.status != PaymentStatus.COMPLETED:
                raise HTTPException(status_code=400, detail="Solo se pueden reembolsar pagos completados")
            
            updated_payment = self.repository.update_status(payment.id, PaymentStatus.REFUNDED)
            self.order_repository.client.table("orders").update({"status": "cancelled"}).eq("id", str(payment.order_id)).execute()

            return PaymentItemResponse(
                message="Reembolso procesado correctamente",
                data=self._to_response(updated_payment)
            )
        except PaymentNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    def _to_response(self, payment: Payment) -> PaymentResponse:
        return PaymentResponse.model_validate(payment)

def get_payment_service() -> PaymentService:
    return PaymentService()