"""Endpoints de salud y verificación operativa."""

from fastapi import APIRouter, Depends

from app.schemas.health import HealthResponse
from app.services.health_service import HealthService, get_health_service


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def health_check(service: HealthService = Depends(get_health_service)) -> HealthResponse:
    """Endpoint de salud desacoplado de la infraestructura real."""

    return service.get_health()
