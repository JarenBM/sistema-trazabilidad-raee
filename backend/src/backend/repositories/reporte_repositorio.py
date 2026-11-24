"""Acceso a reportes estadísticos mediante funciones almacenadas."""

import psycopg

from ..database import obtener_conexion
from ..errors import NoEncontradoError
from .comun import traducir_error_bd


def resumen() -> dict:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM fn_reportes_resumen()")
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)

    if fila is None:
        raise NoEncontradoError("No fue posible obtener el resumen de reportes.")
    return fila
