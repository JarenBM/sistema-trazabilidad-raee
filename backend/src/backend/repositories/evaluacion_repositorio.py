"""Acceso a evaluaciones técnicas mediante funciones almacenadas."""

from decimal import Decimal

import psycopg

from ..database import obtener_conexion
from ..errors import NoEncontradoError
from .comun import traducir_error_bd


def registrar(
    *,
    id_raee: int,
    id_evaluador: int,
    id_tipo_destino: int,
    condicion_fisica: str,
    es_operativo: bool,
    peso_kg: Decimal,
    observaciones: str | None,
) -> int:
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT fn_evaluacion_registrar(%s, %s, %s, %s, %s, %s, %s) AS resultado",
                (
                    id_raee,
                    id_evaluador,
                    id_tipo_destino,
                    condicion_fisica,
                    es_operativo,
                    peso_kg,
                    observaciones,
                ),
            )
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)

    if fila is None:
        raise NoEncontradoError("No fue posible registrar la evaluación.")
    return int(fila["resultado"])
