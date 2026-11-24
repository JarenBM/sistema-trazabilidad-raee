"""Servicios de centros de acopio."""

from ..repositories import centro_repositorio
from ..schemas.centros import CentroCreadoRespuesta, CentroCrearRequest
from ..schemas.usuarios import EstadoActualizadoRespuesta


def crear_centro(datos: CentroCrearRequest) -> CentroCreadoRespuesta:
    id_centro = centro_repositorio.crear(
        nombre_centro=datos.nombre_centro,
        direccion=datos.direccion,
        telefono=datos.telefono,
        ubigeo=datos.ubigeo,
        latitud=datos.latitud,
        longitud=datos.longitud,
    )
    return CentroCreadoRespuesta(id_centro=id_centro)


def cambiar_estado(id_centro: int, activo: bool) -> EstadoActualizadoRespuesta:
    centro_repositorio.cambiar_estado(id_centro, activo)
    return EstadoActualizadoRespuesta(actualizado=True)
