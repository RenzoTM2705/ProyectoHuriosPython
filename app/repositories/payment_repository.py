"""Repositorio de pagos usando Supabase PostgreSQL."""

from __future__ import annotations
from datetime import UTC, datetime
from decimal import Decimal
from typing import Mapping
from uuid import UUID, uuid4
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.repositories.base_repository import BaseRepository

class PaymentRepositoryError(Exception):
    """Error de persistencia en pagos."""

class PaymentNotFoundError(PaymentRepositoryError):
    """Señala que el pago no existe."""

class PaymentRepository(BaseRepository):
    """Acceso a la tabla `payments`."""
    table_name = "payments"

    def create(self, payload: dict[str, object]) -> Payment:
        """Registra una nueva intención de pago en la base de datos."""
        try:
            data = dict(payload)
            data.setdefault("id", str(uuid4()))
            data["created_at"] = datetime.now(UTC).isoformat()
            data["updated_at"] = datetime.now(UTC).isoformat()
            
            response = self.client.table(self.table_name).insert(data).execute()
            rows = self._extract_rows(response)
            if not rows:
                raise PaymentRepositoryError("Supabase no devolvió el pago creado")
            return self._to_payment(rows[0])
        except Exception as exc:
            raise PaymentRepositoryError(self._normalize_error(exc)) from exc

    def get_by_id(self, payment_id: UUID) -> Payment:
        """Obtiene un pago específico."""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", str(payment_id)).limit(1).execute()
            rows = self._extract_rows(response)
            if not rows:
                raise PaymentNotFoundError(f"Pago {payment_id} no encontrado")
            return self._to_payment(rows[0])
        except PaymentNotFoundError:
            raise
        except Exception as exc:
            raise PaymentRepositoryError(self._normalize_error(exc)) from exc

    def update_status(self, payment_id: UUID, status: PaymentStatus) -> Payment:
        """Actualiza el estado de la transacción."""
        try:
            response = (
                self.client.table(self.table_name)
                .update({"status": status.value, "updated_at": datetime.now(UTC).isoformat()})
                .eq("id", str(payment_id))
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise PaymentNotFoundError(f"Pago {payment_id} no encontrado")
            return self._to_payment(rows[0])
        except PaymentNotFoundError:
            raise
        except Exception as exc:
            raise PaymentRepositoryError(self._normalize_error(exc)) from exc

    def list_by_user(self, user_id: UUID) -> list[Payment]:
        """Lista el historial de pagos haciendo un join con orders para filtrar por usuario."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*, orders!inner(user_id)")
                .eq("orders.user_id", str(user_id))
                .order("created_at", desc=True)
                .execute()
            )
            return [self._to_payment(row) for row in self._extract_rows(response)]
        except Exception as exc:
            raise PaymentRepositoryError(self._normalize_error(exc)) from exc

    def _to_payment(self, row: Mapping[str, object]) -> Payment:
        """Convierte una fila cruda a la entidad de dominio."""
        return Payment(
            id=UUID(str(row.get("id"))),
            order_id=UUID(str(row.get("order_id"))),
            payment_method=PaymentMethod(str(row.get("payment_method"))),
            amount=Decimal(str(row.get("amount", "0"))),
            status=PaymentStatus(str(row.get("status", PaymentStatus.PENDING))),
            created_at=self._parse_datetime(row.get("created_at")),
            updated_at=self._parse_datetime(row.get("updated_at")),
        )

    def _normalize_error(self, exc: Exception) -> str:
        return super()._normalize_error(exc, "Error inesperado en el repositorio de pagos")