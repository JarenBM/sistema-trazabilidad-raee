"""Modelos de reportes estadísticos."""

from decimal import Decimal

from pydantic import BaseModel, Field


class ReporteResumenRespuesta(BaseModel):
    total_dispositivos: int = Field(..., examples=[2])
    total_registrados: int = Field(..., examples=[0])
    total_solicitados: int = Field(..., examples=[1])
    total_recibidos: int = Field(..., examples=[0])
    total_evaluados: int = Field(..., examples=[1])
    peso_total_kg: Decimal = Field(..., examples=[2.2])
    peso_valorizado_kg: Decimal = Field(..., examples=[2.2])
    peso_disposicion_final_kg: Decimal = Field(..., examples=[0])
