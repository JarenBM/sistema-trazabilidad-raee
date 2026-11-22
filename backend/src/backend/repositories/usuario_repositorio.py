"""Acceso a datos de usuarios mediante funciones almacenadas."""

import psycopg

from ..database import obtener_conexion
from ..errors import NoEncontradoError
from .comun import traducir_error_bd


def obtener_sesion(correo: str) -> dict | None:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_usuario_obtener_sesion(%s)",
                (correo,),
            )
            return cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)


def registrar(
    *,
    nombres: str,
    apellidos: str,
    correo: str,
    password_hash: str,
    telefono: str | None,
    rol: str,
    ubigeo: str,
    direccion: str | None,
    id_centro: int | None,
) -> dict:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM fn_usuario_registrar(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    nombres,
                    apellidos,
                    correo,
                    password_hash,
                    telefono,
                    rol,
                    ubigeo,
                    direccion,
                    id_centro,
                ),
            )
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)

    if fila is None:
        raise NoEncontradoError("No fue posible registrar el usuario.")
    return fila


def listar() -> list[dict]:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM fn_usuarios_listar()")
            return cursor.fetchall()
    except psycopg.Error as exc:
        traducir_error_bd(exc)


def cambiar_estado(id_usuario: int, activo: bool) -> bool:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT fn_usuario_cambiar_estado(%s, %s) AS resultado",
                (id_usuario, activo),
            )
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)
    return bool(fila and fila["resultado"])
