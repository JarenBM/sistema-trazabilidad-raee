"""Modelos de consulta pública de trazabilidad."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class HistorialRespuesta(BaseModel):
    id_historial: int = Field(..., examples=[1])
    estado_anterior: str | None = Field(None, examples=[None])
    estado_nuevo: str = Field(..., examples=["REGISTRADO"])
    comentario: str | None = Field(
        None,
        examples=["Dispositivo registrado por el ciudadano en la plataforma."],
    )
    fecha_cambio: datetime = Field(..., examples=["2026-11-20T10:00:00-05:00"])


class FichaRaeeRespuesta(BaseModel):
    id_raee: int = Field(..., examples=[1])
    codigo_seguimiento: str = Field(..., examples=["RAEE-2026-0001"])
    categoria: str = Field(..., examples=["Informática y Telecomunicaciones"])
    marca: str | None = Field(None, examples=["Lenovo"])
    modelo: str | None = Field(None, examples=["IdeaPad 330"])
    descripcion: str | None = Field(
        None,
        examples=["Laptop de 15 pulgadas con pantalla dañada."],
    )
    fecha_registro: datetime = Field(..., examples=["2026-11-20T09:30:00-05:00"])
    estado_actual: str | None = Field(None, examples=["EVALUADO"])
    destino_final: str | None = Field(None, examples=["Recuperación de componentes"])
    es_valorizacion: bool | None = Field(None, examples=[True])
    peso_kg: Decimal | None = Field(None, examples=[2.5])


class RastreoRespuesta(BaseModel):
    ficha: FichaRaeeRespuesta
    historial: list[HistorialRespuesta]
