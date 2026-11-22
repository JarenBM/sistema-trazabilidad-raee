"""Modelos de dispositivos RAEE del ciudadano."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class RaeeCrearRequest(BaseModel):
    id_categoria: int = Field(..., gt=0, examples=[1])
    marca: str = Field(..., min_length=1, max_length=50, examples=["Lenovo"])
    modelo: str = Field(..., min_length=1, max_length=50, examples=["IdeaPad 330"])
    descripcion: str | None = Field(
        None,
        max_length=500,
        examples=["Laptop de 15 pulgadas, pantalla dañada pero enciende con monitor externo."],
    )


class RaeeRegistradoRespuesta(BaseModel):
    id_raee: int = Field(..., examples=[3])
    codigo_seguimiento: str = Field(..., examples=["RAEE-2026-0003"])


class RaeeListadoRespuesta(BaseModel):
    id_raee: int = Field(..., examples=[3])
    codigo_seguimiento: str = Field(..., examples=["RAEE-2026-0003"])
    categoria: str = Field(..., examples=["Informática y Telecomunicaciones"])
    marca: str | None = Field(None, examples=["Lenovo"])
    modelo: str | None = Field(None, examples=["IdeaPad 330"])
    descripcion: str | None = Field(
        None,
        examples=["Laptop de 15 pulgadas con pantalla dañada."],
    )
    fecha_registro: datetime = Field(..., examples=["2026-11-20T09:30:00-05:00"])
    estado_actual: str | None = Field(None, examples=["REGISTRADO"])
    destino_final: str | None = Field(None, examples=[None])
    peso_kg: Decimal | None = Field(None, examples=[None])
