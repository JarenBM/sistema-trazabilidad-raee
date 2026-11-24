"""Servicios de consulta pública de trazabilidad."""

from ..errors import NoEncontradoError
from ..repositories import publico_repositorio
from ..schemas.publico import FichaRaeeRespuesta, HistorialRespuesta, RastreoRespuesta


def obtener_rastreo(codigo_seguimiento: str) -> RastreoRespuesta:
    ficha = publico_repositorio.obtener_raee(codigo_seguimiento)
    if ficha is None:
        raise NoEncontradoError(
            "No existe un equipo registrado con ese código de seguimiento."
        )

    historial = publico_repositorio.historial(codigo_seguimiento)
    return RastreoRespuesta(
        ficha=FichaRaeeRespuesta.model_validate(ficha),
        historial=[HistorialRespuesta.model_validate(fila) for fila in historial],
    )
