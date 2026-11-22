"""Servicios de dispositivos RAEE del ciudadano."""

from ..repositories import raee_repositorio
from ..schemas.raee import (
    RaeeCrearRequest,
    RaeeListadoRespuesta,
    RaeeRegistradoRespuesta,
)


def registrar(datos: RaeeCrearRequest, id_usuario: int) -> RaeeRegistradoRespuesta:
    fila = raee_repositorio.registrar(
        id_usuario=id_usuario,
        id_categoria=datos.id_categoria,
        marca=datos.marca,
        modelo=datos.modelo,
        descripcion=datos.descripcion,
    )
    return RaeeRegistradoRespuesta.model_validate(fila)


def listar_mios(id_usuario: int) -> list[RaeeListadoRespuesta]:
    return [
        RaeeListadoRespuesta.model_validate(fila)
        for fila in raee_repositorio.listar_por_usuario(id_usuario)
    ]
