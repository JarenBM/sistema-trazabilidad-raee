"""Hash de contraseñas con Argon2id y tokens JWT HS256."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from .config import configuracion
from .errors import NoAutorizadoError, ProhibidoError

ALGORITMO_JWT = "HS256"
_hasher = PasswordHasher()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@dataclass(frozen=True)
class UsuarioAutenticado:
    """Identidad extraída de los claims del JWT (sin consultar la BD)."""

    id_usuario: int
    correo: str
    rol: str
    id_centro: int | None = None


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def crear_token_acceso(
    *,
    id_usuario: int,
    correo: str,
    rol: str,
    id_centro: int | None,
) -> tuple[str, int]:
    expira_minutos = configuracion.jwt_expiracion_minutos
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_usuario),
        "correo": correo,
        "rol": rol,
        "id_centro": id_centro,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=expira_minutos),
    }
    token = jwt.encode(payload, configuracion.jwt_secret, algorithm=ALGORITMO_JWT)
    return token, expira_minutos


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, configuracion.jwt_secret, algorithms=[ALGORITMO_JWT])
    except jwt.ExpiredSignatureError as exc:
        raise NoAutorizadoError("El token de acceso ha expirado.") from exc
    except jwt.InvalidTokenError as exc:
        raise NoAutorizadoError("El token de acceso no es válido.") from exc


def get_usuario_actual(token: str = Depends(oauth2_scheme)) -> UsuarioAutenticado:
    """Valida el JWT en memoria y devuelve la identidad del usuario."""
    payload = decodificar_token(token)
    try:
        id_usuario = int(payload["sub"])
        correo = str(payload["correo"])
        rol = str(payload["rol"])
    except (KeyError, TypeError, ValueError) as exc:
        raise NoAutorizadoError("El token de acceso no es válido.") from exc

    id_centro = payload.get("id_centro")
    return UsuarioAutenticado(
        id_usuario=id_usuario,
        correo=correo,
        rol=rol,
        id_centro=int(id_centro) if id_centro is not None else None,
    )


def requerir_roles(*roles: str) -> Callable[..., UsuarioAutenticado]:
    """Fábrica de dependencias que exige uno de los roles indicados."""

    def verificador(
        usuario: UsuarioAutenticado = Depends(get_usuario_actual),
    ) -> UsuarioAutenticado:
        if usuario.rol not in roles:
            raise ProhibidoError("No tiene permisos para realizar esta operación.")
        return usuario

    return verificador
