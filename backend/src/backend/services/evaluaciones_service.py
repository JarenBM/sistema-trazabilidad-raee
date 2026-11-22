"""Servicios de evaluación técnica."""

from ..repositories import evaluacion_repositorio
from ..schemas.evaluaciones import (
    EvaluacionCrearRequest,
    EvaluacionRegistradaRespuesta,
)


def registrar(
    datos: EvaluacionCrearRequest,
    id_evaluador: int,
) -> EvaluacionRegistradaRespuesta:
    id_evaluacion = evaluacion_repositorio.registrar(
        id_raee=datos.id_raee,
        id_evaluador=id_evaluador,
        id_tipo_destino=datos.id_tipo_destino,
        condicion_fisica=datos.condicion_fisica,
        es_operativo=datos.es_operativo,
        peso_kg=datos.peso_kg,
        observaciones=datos.observaciones,
    )
    return EvaluacionRegistradaRespuesta(id_evaluacion=id_evaluacion)
