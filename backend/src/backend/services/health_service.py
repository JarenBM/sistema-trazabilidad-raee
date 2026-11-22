"""Servicio de verificación de salud."""

from ..repositories import health_repo
from ..schemas.health import SaludRespuesta


def verificar_salud() -> SaludRespuesta:
    conectada = health_repo.verificar_conexion()
    return SaludRespuesta(
        ok=conectada,
        base_datos="conectada" if conectada else "sin_conexion",
    )
