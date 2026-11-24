"""Endpoint de verificación de salud de la API y PostgreSQL."""

from fastapi import APIRouter

from ..schemas.health import SaludRespuesta
from ..services import health_service

router = APIRouter(tags=["Salud"])


@router.get(
    "/health",
    response_model=SaludRespuesta,
    summary="Verificar el estado de la API y de PostgreSQL",
)
def verificar_salud() -> SaludRespuesta:
    return health_service.verificar_salud()
