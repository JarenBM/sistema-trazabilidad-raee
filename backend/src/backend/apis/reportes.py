"""Endpoints de reportes estadísticos (solo ADMIN)."""

from fastapi import APIRouter, Depends

from ..schemas.reportes import ReporteResumenRespuesta
from ..security import requerir_roles
from ..services import reportes_service

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"],
    dependencies=[Depends(requerir_roles("ADMIN"))],
)


@router.get(
    "/resumen",
    response_model=ReporteResumenRespuesta,
    summary="Obtener los indicadores globales del sistema",
)
def obtener_resumen() -> ReporteResumenRespuesta:
    return reportes_service.obtener_resumen()
