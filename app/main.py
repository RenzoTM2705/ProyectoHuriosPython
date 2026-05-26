"""Punto de entrada de FastAPI.

La aplicación se mantiene delgada a propósito: solo ensambla la configuración
global y registra los routers. La lógica de negocio vive en capas inferiores.
"""

from fastapi import FastAPI

from app.config.settings import settings
from app.routers.auth_router import auth_router
from app.routers.api import api_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend empresarial modular inspirado en Spring Boot, con capas "
        "separadas y una base lista para escalar."
    ),
    debug=settings.debug,
)


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    """Endpoint mínimo para validar que el servicio está activo."""

    return {
        "message": "API ejecutándose correctamente",
        "version": settings.app_version,
    }


# El router agregado centraliza la composición de rutas de toda la API.
app.include_router(api_router)

# La autenticación se expone en rutas raíz para respetar /auth/register y /auth/login.
app.include_router(auth_router)
