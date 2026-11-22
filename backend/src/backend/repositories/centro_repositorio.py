"""Acceso a centros de acopio mediante funciones almacenadas."""

from decimal import Decimal

import psycopg

from ..database import obtener_conexion
from ..errors import NoEncontradoError
from .comun import traducir_error_bd


def crear(
    *,
    nombre_centro: str,
    direccion: str,
    telefono: str | None,
    ubigeo: str,
    latitud: Decimal | None,
    longitud: Decimal | None,
) -> int:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT fn_centro_crear(%s, %s, %s, %s, %s, %s) AS resultado",
                (nombre_centro, direccion, telefono, ubigeo, latitud, longitud),
            )
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)

    if fila is None:
        raise NoEncontradoError("No fue posible crear el centro de acopio.")
    return int(fila["resultado"])


def cambiar_estado(id_centro: int, activo: bool) -> bool:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT fn_centro_cambiar_estado(%s, %s) AS resultado",
                (id_centro, activo),
            )
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)
    return bool(fila and fila["resultado"])
