"""Preparación para seguridad y JWT.

Esta capa centraliza constantes y utilidades relacionadas con autenticación.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings


JWT_SECRET_KEY = settings.jwt_secret_key
JWT_ALGORITHM = settings.jwt_algorithm
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes


bearer_scheme = HTTPBearer(auto_error=False)


def get_bearer_token(
	credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
	"""Extrae un token Bearer para proteger rutas futuras.

	Se deja disponible desde ahora para no duplicar lógica cuando se agreguen
	endpoints protegidos con JWT de Supabase.
	"""

	if credentials is None or credentials.scheme.lower() != "bearer":
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token Bearer ausente o inválido",
		)

	return credentials.credentials
