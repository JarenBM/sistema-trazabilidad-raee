"""Endpoints de registro, login y perfil del usuario autenticado."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas.auth import RegistroRequest, TokenRespuesta, UsuarioSesionRespuesta
from ..security import UsuarioAutenticado, get_usuario_actual
from ..services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/registro",
    response_model=UsuarioSesionRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un ciudadano",
)
def registrar_ciudadano(datos: RegistroRequest) -> UsuarioSesionRespuesta:
    return auth_service.registrar_ciudadano(datos)


@router.post(
    "/login",
    response_model=TokenRespuesta,
    summary="Iniciar sesión y obtener un token JWT",
)
def iniciar_sesion(
    formulario: OAuth2PasswordRequestForm = Depends(),
) -> TokenRespuesta:
    return auth_service.autenticar(formulario.username, formulario.password)


@router.get(
    "/me",
    response_model=UsuarioSesionRespuesta,
    summary="Obtener los datos frescos del usuario autenticado",
)
def obtener_mi_perfil(
    usuario: UsuarioAutenticado = Depends(get_usuario_actual),
) -> UsuarioSesionRespuesta:
    return auth_service.obtener_perfil(usuario.correo)
