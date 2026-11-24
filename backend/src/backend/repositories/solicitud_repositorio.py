"""Acceso a solicitudes de entrega mediante funciones almacenadas."""

from datetime import datetime

import psycopg

from ..database import obtener_conexion
from ..errors import NoEncontradoError
from .comun import traducir_error_bd


def crear(
    *,
    id_raee: int,
    id_usuario: int,
    id_centro: int,
    tipo_solicitud: str,
    fecha_programada: datetime,
) -> int:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT fn_solicitud_crear(%s, %s, %s, %s, %s) AS resultado",
                (id_raee, id_usuario, id_centro, tipo_solicitud, fecha_programada),
            )
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)

    if fila is None:
        raise NoEncontradoError("No fue posible crear la solicitud.")
    return int(fila["resultado"])


def cancelar(id_solicitud: int, id_usuario: int) -> bool:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT fn_solicitud_cancelar(%s, %s) AS resultado",
                (id_solicitud, id_usuario),
            )
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)
    return bool(fila and fila["resultado"])


def listar_por_usuario(id_usuario: int) -> list[dict]:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_solicitudes_listar_por_usuario(%s)",
                (id_usuario,),
            )
            return cursor.fetchall()
    except psycopg.Error as exc:
        traducir_error_bd(exc)


def listar_por_centro(id_centro: int, estado: str | None) -> list[dict]:
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_solicitudes_listar_por_centro(%s, %s)",
                (id_centro, estado),
            )
            return cursor.fetchall()
    except psycopg.Error as exc:
        traducir_error_bd(exc)


def recepcionar(id_solicitud: int, id_encargado: int) -> bool:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT fn_solicitud_recepcionar(%s, %s) AS resultado",
                (id_solicitud, id_encargado),
            )
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)
    return bool(fila and fila["resultado"])
