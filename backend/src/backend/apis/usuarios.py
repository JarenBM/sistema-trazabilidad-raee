"""Endpoints de administración de usuarios (solo ADMIN)."""

from fastapi import APIRouter, Depends, status

from ..schemas.usuarios import (
    EncargadoCrearRequest,
    EstadoActualizadoRespuesta,
    UsuarioCreadoRespuesta,
    UsuarioEstadoRequest,
    UsuarioListadoRespuesta,
)
from ..security import requerir_roles
from ..services import usuarios_service

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(requerir_roles("ADMIN"))],
)


@router.get(
    "",
    response_model=list[UsuarioListadoRespuesta],
    summary="Listar todos los usuarios",
)
def listar_usuarios() -> list[UsuarioListadoRespuesta]:
    return usuarios_service.listar()


@router.post(
    "/encargado",
    response_model=UsuarioCreadoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un encargado de centro de acopio",
)
def crear_encargado(datos: EncargadoCrearRequest) -> UsuarioCreadoRespuesta:
    return usuarios_service.crear_encargado(datos)


@router.patch(
    "/{id_usuario}/estado",
    response_model=EstadoActualizadoRespuesta,
    summary="Activar o desactivar una cuenta",
)
def cambiar_estado_usuario(
    id_usuario: int,
    datos: UsuarioEstadoRequest,
) -> EstadoActualizadoRespuesta:
    return usuarios_service.cambiar_estado(id_usuario, datos.activo)
