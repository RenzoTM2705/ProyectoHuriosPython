"""Router de autenticación pública."""

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.auth import AuthenticatedUser
from app.schemas.auth import AuthCredentialsRequest, AuthResponse, CurrentUserResponse
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
    """Autentica un usuario y devuelve el JWT emitido por el backend."""

    return service.login(payload)


@auth_router.get("/me", response_model=CurrentUserResponse)
def me(current_user: AuthenticatedUser = Depends(get_current_user)) -> CurrentUserResponse:
    """Devuelve el usuario autenticado a partir del JWT recibido."""

    return CurrentUserResponse.model_validate(current_user)
