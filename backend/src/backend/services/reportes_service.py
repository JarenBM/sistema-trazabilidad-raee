"""Servicios de reportes estadísticos."""

from ..repositories import reporte_repositorio
from ..schemas.reportes import ReporteResumenRespuesta


def obtener_resumen() -> ReporteResumenRespuesta:
    return ReporteResumenRespuesta.model_validate(reporte_repositorio.resumen())
