"""Endpoints de evaluación técnica (solo ENCARGADO)."""

from fastapi import APIRouter, Depends, status

from ..schemas.evaluaciones import (
    EvaluacionCrearRequest,
    EvaluacionRegistradaRespuesta,
)
from ..security import UsuarioAutenticado, requerir_roles
from ..services import evaluaciones_service

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])


@router.post(
    "",
    response_model=EvaluacionRegistradaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar la evaluación técnica y el destino ambiental",
)
def registrar_evaluacion(
    datos: EvaluacionCrearRequest,
    usuario: UsuarioAutenticado = Depends(requerir_roles("ENCARGADO")),
) -> EvaluacionRegistradaRespuesta:
    return evaluaciones_service.registrar(datos, usuario.id_usuario)
