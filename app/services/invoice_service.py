"""Servicio para la generación de facturas/boletas en formato PDF."""

from __future__ import annotations
import io
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.repositories.order_repository import OrderRepository, OrderNotFoundError, OrderRepositoryError
from app.repositories.storage_repository import StorageRepository, StorageRepositoryError
from app.schemas.invoice import InvoiceResponse

class InvoiceService:
    """Casos de uso para generación de PDFs y facturación."""

    def __init__(
        self, 
        order_repository: OrderRepository | None = None, 
        storage_repository: StorageRepository | None = None
    ) -> None:
        self.order_repository = order_repository or OrderRepository()
        self.storage_repository = storage_repository or StorageRepository()

    def get_or_generate_invoice(self, order_id: UUID) -> InvoiceResponse:
        """Devuelve la URL del PDF. Si no existe, la genera, sube a Supabase y la devuelve."""
        try:
            order = self.order_repository.get_by_id(order_id)
            
            if order.invoice_url:
                return InvoiceResponse(
                    message="Factura recuperada correctamente", 
                    invoice_url=order.invoice_url
                )

            # 1. Generar el PDF en memoria usando ReportLab
            pdf_buffer = io.BytesIO()
            p = canvas.Canvas(pdf_buffer, pagesize=letter)
            
            p.setFont("Helvetica-Bold", 18)
            p.drawString(50, 750, "Comprobante de Pago - Hurios Rally")
            
            p.setFont("Helvetica", 12)
            p.drawString(50, 720, f"N° de Orden: {order.id}")
            fecha_str = order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            p.drawString(50, 700, f"Fecha de emisión: {fecha_str}")
            p.drawString(50, 680, f"Estado: {order.status.value.upper()}")
            
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 640, "Descripción de la compra:")
            
            p.setFont("Helvetica", 11)
            y_position = 610
            for detail in order.details:
                line = f"- {detail.product_name} (x{detail.quantity}) | P.U: S/ {detail.unit_price} | Subtotal: S/ {detail.subtotal}"
                p.drawString(70, y_position, line)
                y_position -= 20
                if y_position < 50: # Control de salto de página básico
                    p.showPage()
                    p.setFont("Helvetica", 11)
                    y_position = 750
            
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y_position - 30, f"Total a Pagar: S/ {order.total}")
            
            p.showPage()
            p.save()
            
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()

            # 2. Subir el archivo al Bucket de Supabase Storage
            file_path = f"{order.id}/invoice.pdf"
            public_url = self.storage_repository.upload_file(
                bucket="invoices",
                file_path=file_path,
                file_bytes=pdf_bytes,
                content_type="application/pdf"
            )

            # 3. Guardar la URL en la tabla Orders
            self.order_repository.update_invoice_url(order.id, public_url)

            return InvoiceResponse(
                message="Factura generada y almacenada correctamente",
                invoice_url=public_url
            )

        except OrderNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except (OrderRepositoryError, StorageRepositoryError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

def get_invoice_service() -> InvoiceService:
    """Dependency helper para FastAPI."""
    return InvoiceService()