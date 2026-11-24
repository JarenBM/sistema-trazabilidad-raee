"""Endpoint público de rastreo de un equipo RAEE."""

from fastapi import APIRouter

from ..schemas.publico import RastreoRespuesta
from ..services import publico_service

router = APIRouter(prefix="/publico", tags=["Consulta pública"])


@router.get(
    "/rastreo/{codigo_seguimiento}",
    response_model=RastreoRespuesta,
    summary="Consultar la ficha y el historial de un equipo por código",
)
def rastrear_equipo(codigo_seguimiento: str) -> RastreoRespuesta:
    return publico_service.obtener_rastreo(codigo_seguimiento)
