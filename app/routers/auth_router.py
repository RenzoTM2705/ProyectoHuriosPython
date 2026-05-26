"""Router de autenticación pública."""

from fastapi import APIRouter, Depends

from app.schemas.auth import AuthCredentialsRequest, AuthResponse
from app.services.auth_service import AuthService, get_auth_service


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=AuthResponse)
def register(
    payload: AuthCredentialsRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Registra un usuario en Supabase Auth."""

    return service.register(payload)


@auth_router.post("/login", response_model=AuthResponse)
def login(
    payload: AuthCredentialsRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Autentica un usuario y devuelve el JWT emitido por Supabase."""

    return service.login(payload)
