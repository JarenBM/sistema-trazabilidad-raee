"""Acceso a dispositivos RAEE mediante funciones almacenadas."""

import psycopg

from ..database import obtener_conexion
from ..errors import NoEncontradoError
from .comun import traducir_error_bd


def registrar(
    *,
    id_usuario: int,
    id_categoria: int,
    marca: str,
    modelo: str,
    descripcion: str | None,
) -> dict:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_raee_registrar(%s, %s, %s, %s, %s)",
                (id_usuario, id_categoria, marca, modelo, descripcion),
            )
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)

    if fila is None:
        raise NoEncontradoError("No fue posible registrar el dispositivo RAEE.")
    return fila


def listar_por_usuario(id_usuario: int) -> list[dict]:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_raee_listar_por_usuario(%s)",
                (id_usuario,),
            )
            return cursor.fetchall()
    except psycopg.Error as exc:
        traducir_error_bd(exc)
