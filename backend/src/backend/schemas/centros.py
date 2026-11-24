"""Modelos de creación y estado de centros de acopio."""

from decimal import Decimal

from pydantic import BaseModel, Field


class CentroCrearRequest(BaseModel):
    nombre_centro: str = Field(
        ...,
        min_length=3,
        max_length=100,
        examples=["Módulo Ambiental - Chilca"],
    )
    direccion: str = Field(
        ...,
        min_length=5,
        max_length=200,
        examples=["Av. 9 de Diciembre 410, Chilca"],
    )
    telefono: str | None = Field(
        None,
        min_length=6,
        max_length=20,
        pattern=r"^[0-9+\-\s]+$",
        examples=["064-231190"],
    )
    ubigeo: str = Field(
        ...,
        pattern=r"^12\d{4}$",
        examples=["120107"],
    )
    latitud: Decimal | None = Field(
        None,
        ge=-90,
        le=90,
        examples=[-12.084210],
    )
    longitud: Decimal | None = Field(
        None,
        ge=-180,
        le=180,
        examples=[-75.206780],
    )


class CentroCreadoRespuesta(BaseModel):
    id_centro: int = Field(..., examples=[4])


class CentroEstadoRequest(BaseModel):
    activo: bool = Field(..., examples=[False])
