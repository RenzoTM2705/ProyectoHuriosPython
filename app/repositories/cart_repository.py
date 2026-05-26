"""Repositorio de carrito sobre Supabase PostgreSQL."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.models.cart import Cart, CartItem
from app.repositories.base_repository import BaseRepository


class CartRepositoryError(Exception):
    """Error de persistencia para el carrito."""


class CartNotFoundError(CartRepositoryError):
    """Señala que el carrito solicitado no existe."""


class CartRepository(BaseRepository):
    """Acceso a las tablas `carts` y `cart_items`."""

    carts_table = "carts"
    items_table = "cart_items"

    def get_or_create_cart(self, user_id: UUID) -> Cart:
        """Devuelve el carrito del usuario o lo crea si no existe."""

        cart = self.get_cart_by_user_id(user_id)
        if cart is not None:
            return cart
        return self.create_cart(user_id)

    def get_cart_by_user_id(self, user_id: UUID) -> Cart | None:
        """Busca el carrito de un usuario."""

        try:
            response = (
                self.client.table(self.carts_table)
                .select("*")
                .eq("user_id", str(user_id))
                .limit(1)
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                return None
            return self._attach_items(self._to_cart(rows[0]))
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise CartRepositoryError(self._normalize_error(exc)) from exc

    def create_cart(self, user_id: UUID) -> Cart:
        """Crea un carrito vacío para un usuario."""

        try:
            now = datetime.now(UTC).isoformat()
            payload = {
                "id": str(uuid4()),
                "user_id": str(user_id),
                "total_amount": Decimal("0"),
                "total_items": 0,
                "created_at": now,
                "updated_at": now,
            }
            response = self.client.table(self.carts_table).insert(payload).execute()
            rows = self._extract_rows(response)
            if not rows:
                raise CartRepositoryError("Supabase no devolvió el carrito creado")
            return self._attach_items(self._to_cart(rows[0]))
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise CartRepositoryError(self._normalize_error(exc)) from exc

    def get_item_by_product_id(self, cart_id: UUID, product_id: UUID) -> CartItem | None:
        """Busca un producto dentro del carrito."""

        try:
            response = (
                self.client.table(self.items_table)
                .select("*")
                .eq("cart_id", str(cart_id))
                .eq("product_id", str(product_id))
                .limit(1)
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                return None
            return self._to_item(rows[0])
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise CartRepositoryError(self._normalize_error(exc)) from exc

    def list_items(self, cart_id: UUID) -> list[CartItem]:
        """Lista los items de un carrito."""

        try:
            response = (
                self.client.table(self.items_table)
                .select("*")
                .eq("cart_id", str(cart_id))
                .order("created_at", desc=False)
                .execute()
            )
            return [self._to_item(row) for row in self._extract_rows(response)]
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise CartRepositoryError(self._normalize_error(exc)) from exc

    def add_item(self, payload: dict[str, object]) -> CartItem:
        """Inserta un item en el carrito."""

        try:
            data = dict(payload)
            data.setdefault("id", str(uuid4()))
            data["created_at"] = datetime.now(UTC).isoformat()
            data["updated_at"] = datetime.now(UTC).isoformat()

            response = self.client.table(self.items_table).insert(data).execute()
            rows = self._extract_rows(response)
            if not rows:
                raise CartRepositoryError("Supabase no devolvió el item creado")
            return self._to_item(rows[0])
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise CartRepositoryError(self._normalize_error(exc)) from exc

    def update_item(self, item_id: UUID, payload: dict[str, object]) -> CartItem:
        """Actualiza un item del carrito."""

        try:
            data = dict(payload)
            data["updated_at"] = datetime.now(UTC).isoformat()
            response = (
                self.client.table(self.items_table)
                .update(data)
                .select("*")
                .eq("id", str(item_id))
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise CartNotFoundError(f"Item {item_id} no encontrado")
            return self._to_item(rows[0])
        except CartNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise CartRepositoryError(self._normalize_error(exc)) from exc

    def delete_item_by_product_id(self, cart_id: UUID, product_id: UUID) -> None:
        """Elimina un item por producto dentro de un carrito."""

        try:
            self.client.table(self.items_table).delete().eq("cart_id", str(cart_id)).eq("product_id", str(product_id)).execute()
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise CartRepositoryError(self._normalize_error(exc)) from exc

    def clear_cart(self, cart_id: UUID) -> None:
        """Elimina todos los items del carrito."""

        try:
            self.client.table(self.items_table).delete().eq("cart_id", str(cart_id)).execute()
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise CartRepositoryError(self._normalize_error(exc)) from exc

    def update_cart_totals(self, cart_id: UUID, total_amount: Decimal, total_items: int) -> Cart:
        """Actualiza los totales del carrito."""

        try:
            response = (
                self.client.table(self.carts_table)
                .update(
                    {
                        "total_amount": total_amount,
                        "total_items": total_items,
                        "updated_at": datetime.now(UTC).isoformat(),
                    }
                )
                .select("*")
                .eq("id", str(cart_id))
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise CartNotFoundError(f"Carrito {cart_id} no encontrado")
            return self._attach_items(self._to_cart(rows[0]))
        except CartNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise CartRepositoryError(self._normalize_error(exc)) from exc

    def _attach_items(self, cart: Cart) -> Cart:
        """Carga los items y devuelve el carrito completo."""

        cart.items = self.list_items(cart.id)
        return cart

    def _to_cart(self, row: Mapping[str, object]) -> Cart:
        """Convierte una fila de Supabase en un carrito de dominio."""

        return Cart(
            id=UUID(str(row.get("id"))),
            user_id=UUID(str(row.get("user_id"))),
            total_amount=Decimal(str(row.get("total_amount", "0"))),
            total_items=int(row.get("total_items", 0)),
            created_at=self._parse_datetime(row.get("created_at")),
            updated_at=self._parse_datetime(row.get("updated_at")),
        )

    def _to_item(self, row: Mapping[str, object]) -> CartItem:
        """Convierte una fila de Supabase en un item de carrito."""

        return CartItem(
            id=UUID(str(row.get("id"))),
            cart_id=UUID(str(row.get("cart_id"))),
            product_id=UUID(str(row.get("product_id"))),
            product_name=str(row.get("product_name", "")),
            quantity=int(row.get("quantity", 0)),
            unit_price=Decimal(str(row.get("unit_price", "0"))),
            subtotal=Decimal(str(row.get("subtotal", "0"))),
        )

    def _normalize_error(self, exc: Exception) -> str:
        """Genera un mensaje seguro y legible para la capa de servicio."""

        return super()._normalize_error(exc, "Error inesperado en el repositorio del carrito")
