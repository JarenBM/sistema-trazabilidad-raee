"""Modelos de solicitudes de entrega o recolección."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TipoSolicitud = Literal["PRESENCIAL", "RECOLECCION"]


class SolicitudCrearRequest(BaseModel):
    id_raee: int = Field(..., gt=0, examples=[3])
    id_centro: int = Field(..., gt=0, examples=[2])
    tipo_solicitud: TipoSolicitud = Field(..., examples=["PRESENCIAL"])
    fecha_programada: datetime = Field(
        ...,
        examples=["2026-12-01T10:30:00-05:00"],
    )


class SolicitudCreadaRespuesta(BaseModel):
    id_solicitud: int = Field(..., examples=[3])


class SolicitudCentroRespuesta(BaseModel):
    id_solicitud: int = Field(..., examples=[3])
    id_raee: int = Field(..., examples=[3])
    codigo_seguimiento: str = Field(..., examples=["RAEE-2026-0003"])
    categoria: str = Field(..., examples=["Informática y Telecomunicaciones"])
    marca: str | None = Field(None, examples=["Lenovo"])
    modelo: str | None = Field(None, examples=["IdeaPad 330"])
    ciudadano: str = Field(..., examples=["Andrea Sofía Vargas Salazar"])
    telefono_ciudadano: str | None = Field(None, examples=["954777888"])
    direccion_ciudadano: str | None = Field(
        None,
        examples=["Jr. Los Andes 345, El Tambo"],
    )
    tipo_solicitud: str = Field(..., examples=["PRESENCIAL"])
    fecha_programada: datetime = Field(..., examples=["2026-12-01T10:30:00-05:00"])
    estado_solicitud: str = Field(..., examples=["PENDIENTE"])
    estado_raee_actual: str | None = Field(None, examples=["SOLICITADO"])


class OperacionRespuesta(BaseModel):
    mensaje: str = Field(
        ...,
        examples=["Operación realizada correctamente."],
    )
