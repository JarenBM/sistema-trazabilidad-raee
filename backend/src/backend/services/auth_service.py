"""Servicios de registro, login y perfil."""

from ..errors import NoAutorizadoError
from ..repositories import usuario_repositorio
from ..schemas.auth import RegistroRequest, TokenRespuesta, UsuarioSesionRespuesta
from ..security import crear_token_acceso, hash_password, verificar_password


def _a_sesion(fila: dict) -> UsuarioSesionRespuesta:
    return UsuarioSesionRespuesta(
        id_usuario=fila["id_usuario"],
        nombres=fila["nombres"],
        apellidos=fila["apellidos"],
        correo=fila["correo"],
        rol=fila["rol"],
        id_centro=fila["id_centro"],
        activo=fila["activo"],
    )


def registrar_ciudadano(datos: RegistroRequest) -> UsuarioSesionRespuesta:
    usuario_repositorio.registrar(
        nombres=datos.nombres,
        apellidos=datos.apellidos,
        correo=datos.correo,
        password_hash=hash_password(datos.password),
        telefono=datos.telefono,
        rol="CIUDADANO",
        ubigeo=datos.ubigeo,
        direccion=datos.direccion,
        id_centro=None,
    )
    fila = usuario_repositorio.obtener_sesion(datos.correo)
    if fila is None:
        raise NoAutorizadoError("No fue posible recuperar el usuario registrado.")
    return _a_sesion(fila)


def autenticar(correo: str, password: str) -> TokenRespuesta:
    fila = usuario_repositorio.obtener_sesion(correo)
    if fila is None or not fila["activo"]:
        raise NoAutorizadoError("Credenciales inválidas.")
    if not verificar_password(password, fila["password_hash"]):
        raise NoAutorizadoError("Credenciales inválidas.")

    token, expira_minutos = crear_token_acceso(
        id_usuario=fila["id_usuario"],
        correo=fila["correo"],
        rol=fila["rol"],
        id_centro=fila["id_centro"],
    )
    return TokenRespuesta(
        access_token=token,
        expira_en_minutos=expira_minutos,
        usuario=_a_sesion(fila),
    )


def obtener_perfil(correo: str) -> UsuarioSesionRespuesta:
    """Consulta la BD para devolver datos frescos y verificar que siga activo."""
    fila = usuario_repositorio.obtener_sesion(correo)
    if fila is None or not fila["activo"]:
        raise NoAutorizadoError("La cuenta no existe o se encuentra inactiva.")
    return _a_sesion(fila)
