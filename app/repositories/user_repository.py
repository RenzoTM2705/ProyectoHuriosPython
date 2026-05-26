"""Repositorio de usuarios sobre Supabase PostgreSQL.

La capa de infraestructura se encarga de hablar con la tabla `users` y de
convertir respuestas crudas del SDK en entidades de dominio limpias.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.user import User, UserRole
from app.repositories.base_repository import BaseRepository


class UserRepositoryError(Exception):
    """Error de acceso a la persistencia de usuarios."""


class UserNotFoundError(UserRepositoryError):
    """Señala que el usuario solicitado no existe."""


class UserRepository(BaseRepository):
    """Acceso a la tabla `users` gestionada por Supabase PostgreSQL."""

    table_name = "users"

    def list_all(self) -> list[User]:
        """Obtiene todos los usuarios ordenados por creación descendente."""

        try:
            response = self.client.table(self.table_name).select("*").order("created_at", desc=True).execute()
            return [self._to_user(row) for row in self._extract_rows(response)]
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise UserRepositoryError(self._normalize_error(exc)) from exc

    def get_by_id(self, user_id: UUID) -> User:
        """Busca un usuario por su identificador."""

        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("id", str(user_id))
                .limit(1)
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise UserNotFoundError(f"Usuario {user_id} no encontrado")
            return self._to_user(rows[0])
        except UserNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise UserRepositoryError(self._normalize_error(exc)) from exc

    def update(self, user_id: UUID, payload: dict[str, object]) -> User:
        """Actualiza un usuario y devuelve la versión persistida."""

        try:
            data = dict(payload)
            data["updated_at"] = datetime.now(UTC).isoformat()

            response = (
                self.client.table(self.table_name)
                .update(data)
                .eq("id", str(user_id))
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise UserNotFoundError(f"Usuario {user_id} no encontrado")
            return self._to_user(rows[0])
        except UserNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise UserRepositoryError(self._normalize_error(exc)) from exc

    def delete(self, user_id: UUID) -> None:
        """Elimina un usuario por su identificador."""

        try:
            response = (
                self.client.table(self.table_name)
                .delete()
                .eq("id", str(user_id))
                .execute()
            )
            rows = self._extract_rows(response)
            if not rows:
                raise UserNotFoundError(f"Usuario {user_id} no encontrado")
        except UserNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - dependencia externa
            raise UserRepositoryError(self._normalize_error(exc)) from exc

    def _to_user(self, row: Mapping[str, object]) -> User:
        """Convierte una fila de Supabase en una entidad de dominio."""

        return User(
            id=UUID(str(row.get("id"))),
            name=str(row.get("name", "")),
            email=str(row.get("email", "")),
            role=UserRole(str(row.get("role", UserRole.CUSTOMER))),
            is_active=bool(row.get("is_active", True)),
            created_at=self._parse_datetime(row.get("created_at")),
            updated_at=self._parse_datetime(row.get("updated_at")),
        )

    def _normalize_error(self, exc: Exception) -> str:
        """Genera un mensaje seguro para la capa de servicio."""

        return super()._normalize_error(exc, "Error inesperado en el repositorio de usuarios")
