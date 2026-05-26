"""Preparación para seguridad y JWT.

Esta capa centraliza constantes y utilidades relacionadas con autenticación.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt

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
			headers={"WWW-Authenticate": "Bearer"},
		)

	return credentials.credentials


def decode_supabase_jwt(token: str) -> dict[str, object]:
	"""Valida la firma y expiración del JWT emitido por Supabase Auth."""

	try:
		claims = jwt.decode(
			token,
			JWT_SECRET_KEY,
			algorithms=[JWT_ALGORITHM],
			options={"verify_aud": False},
		)
	except ExpiredSignatureError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token expirado",
			headers={"WWW-Authenticate": "Bearer"},
		) from exc
	except JWTError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token inválido",
			headers={"WWW-Authenticate": "Bearer"},
		) from exc

	subject = claims.get("sub")
	if not subject:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token inválido",
			headers={"WWW-Authenticate": "Bearer"},
		)

	issuer = claims.get("iss")
	if settings.supabase_url and issuer:
		expected_issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1"
		if issuer != expected_issuer:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Token inválido",
				headers={"WWW-Authenticate": "Bearer"},
			)

	return claims


def get_authenticated_user_id(token: str = Depends(get_bearer_token)) -> UUID:
	"""Obtiene el identificador del usuario autenticado desde el JWT de Supabase."""

	claims = decode_supabase_jwt(token)
	try:
		return UUID(str(claims.get("sub")))
	except Exception as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token inválido",
			headers={"WWW-Authenticate": "Bearer"},
		) from exc
