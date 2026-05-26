"""Agrupador principal de routers versionados."""

from fastapi import APIRouter

from app.routers.health import router as health_router


api_router = APIRouter(prefix="/api/v1")

# Se registran aquí todos los routers funcionales de la versión actual.
api_router.include_router(health_router)
