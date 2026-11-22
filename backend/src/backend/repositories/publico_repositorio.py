"""Acceso a la consulta pública de trazabilidad."""

import psycopg

from ..database import obtener_conexion
from .comun import traducir_error_bd


def obtener_raee(codigo_seguimiento: str) -> dict | None:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_publico_obtener_raee(%s)",
                (codigo_seguimiento,),
            )
            return cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)


def historial(codigo_seguimiento: str) -> list[dict]:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_publico_historial_raee(%s)",
                (codigo_seguimiento,),
            )
            return cursor.fetchall()
    except psycopg.Error as exc:
        traducir_error_bd(exc)
