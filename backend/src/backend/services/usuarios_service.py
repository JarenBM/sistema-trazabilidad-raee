"""Servicios de administración de usuarios."""

from ..repositories import usuario_repositorio
from ..schemas.usuarios import (
    EncargadoCrearRequest,
    EstadoActualizadoRespuesta,
    UsuarioCreadoRespuesta,
    UsuarioListadoRespuesta,
)
from ..security import hash_password


def listar() -> list[UsuarioListadoRespuesta]:
    return [
        UsuarioListadoRespuesta.model_validate(fila)
        for fila in usuario_repositorio.listar()
    ]


def crear_encargado(datos: EncargadoCrearRequest) -> UsuarioCreadoRespuesta:
    fila = usuario_repositorio.registrar(
        nombres=datos.nombres,
        apellidos=datos.apellidos,
        correo=datos.correo,
        password_hash=hash_password(datos.password),
        telefono=datos.telefono,
        rol="ENCARGADO",
        ubigeo=datos.ubigeo,
        direccion=datos.direccion,
        id_centro=datos.id_centro,
    )
    return UsuarioCreadoRespuesta.model_validate(fila)


def cambiar_estado(id_usuario: int, activo: bool) -> EstadoActualizadoRespuesta:
    usuario_repositorio.cambiar_estado(id_usuario, activo)
    return EstadoActualizadoRespuesta(actualizado=True)
