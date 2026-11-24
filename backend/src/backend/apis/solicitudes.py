"""Endpoints de solicitudes de entrega y recepción."""

from fastapi import APIRouter, Depends, status

from ..schemas.solicitudes import (
    OperacionRespuesta,
    SolicitudCentroRespuesta,
    SolicitudCiudadanoRespuesta,
    SolicitudCreadaRespuesta,
    SolicitudCrearRequest,
)
from ..security import UsuarioAutenticado, requerir_roles
from ..services import solicitudes_service

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


@router.post(
    "",
    response_model=SolicitudCreadaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una solicitud de entrega o recolección",
)
def crear_solicitud(
    datos: SolicitudCrearRequest,
    usuario: UsuarioAutenticado = Depends(requerir_roles("CIUDADANO")),
) -> SolicitudCreadaRespuesta:
    return solicitudes_service.crear(datos, usuario.id_usuario)


@router.get(
    "/mias",
    response_model=list[SolicitudCiudadanoRespuesta],
    summary="Listar las solicitudes del ciudadano autenticado",
)
def listar_mis_solicitudes(
    usuario: UsuarioAutenticado = Depends(requerir_roles("CIUDADANO")),
) -> list[SolicitudCiudadanoRespuesta]:
    return solicitudes_service.listar_mias(usuario.id_usuario)


@router.get(
    "/centro",
    response_model=list[SolicitudCentroRespuesta],
    summary="Listar las solicitudes del centro asignado al encargado",
)
def listar_solicitudes_centro(
    estado: str | None = None,
    usuario: UsuarioAutenticado = Depends(requerir_roles("ENCARGADO")),
) -> list[SolicitudCentroRespuesta]:
    return solicitudes_service.listar_por_centro(usuario, estado)


@router.patch(
    "/{id_solicitud}/cancelar",
    response_model=OperacionRespuesta,
    summary="Cancelar una solicitud pendiente",
)
def cancelar_solicitud(
    id_solicitud: int,
    usuario: UsuarioAutenticado = Depends(requerir_roles("CIUDADANO")),
) -> OperacionRespuesta:
    return solicitudes_service.cancelar(id_solicitud, usuario.id_usuario)


@router.patch(
    "/{id_solicitud}/recepcionar",
    response_model=OperacionRespuesta,
    summary="Confirmar la recepción física de un equipo",
)
def recepcionar_solicitud(
    id_solicitud: int,
    usuario: UsuarioAutenticado = Depends(requerir_roles("ENCARGADO")),
) -> OperacionRespuesta:
    return solicitudes_service.recepcionar(id_solicitud, usuario)
