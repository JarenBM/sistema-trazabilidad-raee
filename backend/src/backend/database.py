"""Gestión de conexiones a PostgreSQL mediante psycopg."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from .config import configuracion


@contextmanager
def obtener_conexion() -> Iterator[Connection[dict[str, Any]]]:
    """Abre una conexión con autocommit y filas como diccionarios."""
    with psycopg.connect(
        configuracion.database_url,
        row_factory=dict_row,
        autocommit=True,
    ) as conexion:
        yield conexion
