"""Servicio de autenticación.

Esta capa valida reglas de negocio de alto nivel y traduce errores de
infraestructura a respuestas HTTP adecuadas.
"""

from fastapi import HTTPException, status

from app.models.auth import AuthSessionData
from app.repositories.auth_repository import AuthRepository, AuthRepositoryError
from app.schemas.auth import AuthCredentialsRequest, AuthResponse, AuthTokenResponse, AuthUserResponse


class AuthService:
    """Casos de uso de autenticación para Hurios Rally."""

    def __init__(self, repository: AuthRepository | None = None) -> None:
        self.repository = repository or AuthRepository()

    def register(self, payload: AuthCredentialsRequest) -> AuthResponse:
        """Registra un usuario con Supabase Auth."""

        try:
            session = self.repository.register(payload.email, payload.password)
            return self._build_response(
                message="Usuario registrado correctamente",
                session=session,
            )
        except AuthRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    def login(self, payload: AuthCredentialsRequest) -> AuthResponse:
        """Inicia sesión y devuelve el JWT emitido por Supabase."""

        try:
            session = self.repository.login(payload.email, payload.password)
            if not session.access_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Supabase no devolvió un token de acceso",
                )
            return self._build_response(
                message="Autenticación exitosa",
                session=session,
            )
        except AuthRepositoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc

    def _build_response(self, message: str, session: AuthSessionData) -> AuthResponse:
        """Traduce el modelo de dominio a un contrato público de la API."""

        user = AuthUserResponse.model_validate(session.user)
        tokens = None

        if session.access_token:
            tokens = AuthTokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type=session.token_type,
                expires_in=session.expires_in,
            )

        return AuthResponse(message=message, user=user, tokens=tokens)


def get_auth_service() -> AuthService:
    """Dependency helper para FastAPI."""

    return AuthService()
