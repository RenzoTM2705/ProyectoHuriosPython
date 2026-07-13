"""Esquemas Pydantic para la gestión de facturas y comprobantes."""

from pydantic import BaseModel

class InvoiceResponse(BaseModel):
    """Respuesta estructurada para la URL del comprobante en PDF."""
    message: str
    invoice_url: str