"""Endpoints de dispositivos RAEE del ciudadano."""

from fastapi import APIRouter, Depends, status

from ..schemas.raee import (
    RaeeCrearRequest,
    RaeeListadoRespuesta,
    RaeeRegistradoRespuesta,
)
from ..security import UsuarioAutenticado, requerir_roles
from ..services import raee_service

router = APIRouter(prefix="/raee", tags=["Dispositivos RAEE"])


@router.post(
    "",
    response_model=RaeeRegistradoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un dispositivo RAEE",
)
def registrar_raee(
    datos: RaeeCrearRequest,
    usuario: UsuarioAutenticado = Depends(requerir_roles("CIUDADANO")),
) -> RaeeRegistradoRespuesta:
    return raee_service.registrar(datos, usuario.id_usuario)


@router.get(
    "/mios",
    response_model=list[RaeeListadoRespuesta],
    summary="Listar mis dispositivos registrados",
)
def listar_mis_raee(
    usuario: UsuarioAutenticado = Depends(requerir_roles("CIUDADANO")),
) -> list[RaeeListadoRespuesta]:
    return raee_service.listar_mios(usuario.id_usuario)
