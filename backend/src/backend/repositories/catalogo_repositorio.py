"""Acceso a catálogos mediante funciones almacenadas."""

import psycopg

from ..database import obtener_conexion
from .comun import traducir_error_bd


def distritos() -> list[dict]:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM fn_catalogos_distritos()")
            return cursor.fetchall()
    except psycopg.Error as exc:
        traducir_error_bd(exc)


def categorias() -> list[dict]:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM fn_catalogos_categorias()")
            return cursor.fetchall()
    except psycopg.Error as exc:
        traducir_error_bd(exc)


def tipos_destino() -> list[dict]:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM fn_catalogos_tipos_destino()")
            return cursor.fetchall()
    except psycopg.Error as exc:
        traducir_error_bd(exc)


def centros(solo_activos: bool) -> list[dict]:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_centros_listar(%s)",
                (solo_activos,),
            )
            return cursor.fetchall()
    except psycopg.Error as exc:
        traducir_error_bd(exc)
