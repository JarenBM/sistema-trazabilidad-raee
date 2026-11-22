"""Utilidades compartidas por los repositorios."""

from typing import NoReturn

import psycopg

from ..errors import ConflictoNegocioError, NoEncontradoError, ProhibidoError

_PREFIJOS = (
    ("NO_ENCONTRADO:", NoEncontradoError),
    ("CONFLICTO:", ConflictoNegocioError),
    ("PROHIBIDO:", ProhibidoError),
)


def _mensaje_limpio(mensaje: str, prefijo: str) -> str:
    inicio = mensaje.find(prefijo) + len(prefijo)
    texto = mensaje[inicio:].splitlines()[0].strip()
    return texto or mensaje.strip()


def traducir_error_bd(exc: psycopg.Error) -> NoReturn:
    """Traduce los prefijos de las fn_* a excepciones de dominio."""
    mensaje = str(exc)
    for prefijo, clase in _PREFIJOS:
        if prefijo in mensaje:
            raise clase(_mensaje_limpio(mensaje, prefijo)) from exc

    if isinstance(exc, psycopg.errors.UniqueViolation):
        raise ConflictoNegocioError(
            "Ya existe un registro con los mismos datos."
        ) from exc
    if isinstance(
        exc,
        (psycopg.errors.ForeignKeyViolation, psycopg.errors.CheckViolation),
    ):
        raise ConflictoNegocioError(
            "Los datos enviados no cumplen una regla de negocio."
        ) from exc

    raise exc
