"""Compatibilidad para utilidades de seguridad existentes.

El proyecto usa ahora app.utils.jwt_handler como fuente de verdad para JWT.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends

from app.utils.jwt_handler import decode_token, oauth2_scheme, verify_token


def get_bearer_token(token: str = Depends(oauth2_scheme)) -> str:
	"""Expone el token Bearer para módulos que aún lo consumen directamente."""

	return token


def decode_supabase_jwt(token: str) -> dict[str, object]:
	"""Compatibilidad hacia atrás para código existente."""

	return decode_token(token)


def get_authenticated_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
	"""Obtiene el identificador del usuario autenticado desde el JWT."""

	claims = verify_token(token)
	return UUID(str(claims.get("sub")))
