"""Servicios de solicitudes de entrega y recepción."""

from ..errors import ProhibidoError
from ..repositories import solicitud_repositorio
from ..schemas.solicitudes import (
    OperacionRespuesta,
    SolicitudCentroRespuesta,
    SolicitudCreadaRespuesta,
    SolicitudCrearRequest,
)
from ..security import UsuarioAutenticado


def crear(
    datos: SolicitudCrearRequest,
    id_usuario: int,
) -> SolicitudCreadaRespuesta:
    id_solicitud = solicitud_repositorio.crear(
        id_raee=datos.id_raee,
        id_usuario=id_usuario,
        id_centro=datos.id_centro,
        tipo_solicitud=datos.tipo_solicitud,
        fecha_programada=datos.fecha_programada,
    )
    return SolicitudCreadaRespuesta(id_solicitud=id_solicitud)


def cancelar(id_solicitud: int, id_usuario: int) -> OperacionRespuesta:
    solicitud_repositorio.cancelar(id_solicitud, id_usuario)
    return OperacionRespuesta(mensaje="Solicitud cancelada correctamente.")


def listar_por_centro(
    usuario: UsuarioAutenticado,
    estado: str | None,
) -> list[SolicitudCentroRespuesta]:
    if usuario.id_centro is None:
        raise ProhibidoError("El encargado no tiene un centro de acopio asignado.")
    return [
        SolicitudCentroRespuesta.model_validate(fila)
        for fila in solicitud_repositorio.listar_por_centro(
            usuario.id_centro,
            estado,
        )
    ]


def recepcionar(
    id_solicitud: int,
    usuario: UsuarioAutenticado,
) -> OperacionRespuesta:
    if usuario.id_centro is None:
        raise ProhibidoError("El encargado no tiene un centro de acopio asignado.")
    solicitud_repositorio.recepcionar(id_solicitud, usuario.id_usuario)
    return OperacionRespuesta(mensaje="Recepción registrada correctamente.")
