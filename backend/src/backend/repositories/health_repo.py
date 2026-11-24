"""Verificación de conectividad con PostgreSQL (excepción de infraestructura)."""

import psycopg

from ..database import obtener_conexion
from .comun import traducir_error_bd


def verificar_conexion() -> bool:
    """Ejecuta SELECT 1 AS ok contra Supabase."""
    fila: dict | None = None
    try:
        with obtener_conexion() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT 1 AS ok")
            fila = cursor.fetchone()
    except psycopg.Error as exc:
        traducir_error_bd(exc)
    return bool(fila and fila["ok"] == 1)
