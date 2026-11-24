"""Modelos de evaluación técnica de dispositivos RAEE."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

CondicionFisica = Literal["EXCELENTE", "REGULAR", "INSERVIBLE"]


class EvaluacionCrearRequest(BaseModel):
    id_raee: int = Field(..., gt=0, examples=[1])
    id_tipo_destino: int = Field(..., gt=0, examples=[3])
    condicion_fisica: CondicionFisica = Field(..., examples=["REGULAR"])
    es_operativo: bool = Field(..., examples=[True])
    peso_kg: Decimal = Field(
        ...,
        gt=0,
        le=Decimal("9999.99"),
        examples=[2.5],
    )
    observaciones: str | None = Field(
        None,
        max_length=1000,
        examples=["Pantalla rota; placa madre, procesador y memoria RAM recuperables."],
    )


class EvaluacionRegistradaRespuesta(BaseModel):
    id_evaluacion: int = Field(..., examples=[2])
