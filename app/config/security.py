"""Preparación para seguridad y JWT.

Esta capa centraliza constantes y utilidades relacionadas con autenticación.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from app.config.settings import settings


JWT_SECRET_KEY = settings.jwt_secret_key
JWT_ALGORITHM = settings.jwt_algorithm
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes


bearer_scheme = HTTPBearer(auto_error=False)


def get_bearer_token(
	credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
	"""Extrae un token Bearer para proteger rutas futuras."""

	if credentials is None or credentials.scheme.lower() != "bearer":
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token Bearer ausente o inválido",
		)

	return credentials.credentials


def get_authenticated_user_id(token: str = Depends(get_bearer_token)) -> UUID:
	"""Obtiene el identificador del usuario autenticado desde el JWT de Supabase.

	Se usa el claim `sub`, que Supabase emite como identificador del usuario.
	La validación se mantiene ligera en esta base para no acoplarla al secreto
	operativo de Supabase; la verificación de firma puede añadirse luego.
	"""

	try:
		claims = jwt.get_unverified_claims(token)
		subject = claims.get("sub")
		if not subject:
			raise ValueError("El token no contiene el claim sub")
		return UUID(str(subject))
	except Exception as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token JWT inválido o no autenticado",
		) from exc
