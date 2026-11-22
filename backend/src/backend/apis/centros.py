"""Endpoints de administración de centros de acopio (solo ADMIN)."""

from fastapi import APIRouter, Depends, status

from ..schemas.centros import CentroCreadoRespuesta, CentroCrearRequest, CentroEstadoRequest
from ..schemas.usuarios import EstadoActualizadoRespuesta
from ..security import requerir_roles
from ..services import centros_service

router = APIRouter(
    prefix="/centros",
    tags=["Centros de acopio"],
    dependencies=[Depends(requerir_roles("ADMIN"))],
)


@router.post(
    "",
    response_model=CentroCreadoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un centro de acopio",
)
def crear_centro(datos: CentroCrearRequest) -> CentroCreadoRespuesta:
    return centros_service.crear_centro(datos)


@router.patch(
    "/{id_centro}/estado",
    response_model=EstadoActualizadoRespuesta,
    summary="Activar o desactivar un centro de acopio",
)
def cambiar_estado_centro(
    id_centro: int,
    datos: CentroEstadoRequest,
) -> EstadoActualizadoRespuesta:
    return centros_service.cambiar_estado(id_centro, datos.activo)
