"""Preparación para seguridad y JWT.

Esta capa existe para no mezclar constantes de seguridad con reglas de negocio.
"""

from app.config.settings import settings


JWT_SECRET_KEY = settings.jwt_secret_key
JWT_ALGORITHM = settings.jwt_algorithm
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes
