"""Modelos de administración de usuarios."""

from datetime import datetime

from pydantic import BaseModel, Field

from .auth import PATRON_CORREO


class UsuarioListadoRespuesta(BaseModel):
    id_usuario: int = Field(..., examples=[4])
    nombres: str = Field(..., examples=["Andrea Sofía"])
    apellidos: str = Field(..., examples=["Vargas Salazar"])
    correo: str = Field(..., examples=["andrea.vargas@gmail.com"])
    telefono: str | None = Field(None, examples=["954777888"])
    rol: str = Field(..., examples=["CIUDADANO"])
    distrito: str = Field(..., examples=["El Tambo"])
    nombre_centro: str | None = Field(None, examples=[None])
    activo: bool = Field(..., examples=[True])
    fecha_registro: datetime = Field(..., examples=["2026-11-22T09:15:00-05:00"])


class EncargadoCrearRequest(BaseModel):
    nombres: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Lucía Fernanda"],
    )
    apellidos: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Quispe Huamán"],
    )
    correo: str = Field(
        ...,
        max_length=100,
        pattern=PATRON_CORREO,
        examples=["encargado.centro@raeehuancayo.pe"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["ClaveSegura123"],
    )
    telefono: str | None = Field(
        None,
        min_length=6,
        max_length=20,
        pattern=r"^[0-9+\-\s]+$",
        examples=["964333444"],
    )
    ubigeo: str = Field(
        ...,
        pattern=r"^12\d{4}$",
        examples=["120101"],
    )
    direccion: str | None = Field(
        None,
        min_length=5,
        max_length=200,
        examples=["Calle Real 850, Cercado de Huancayo"],
    )
    id_centro: int = Field(..., gt=0, examples=[1])


class UsuarioEstadoRequest(BaseModel):
    activo: bool = Field(..., examples=[False])


class UsuarioCreadoRespuesta(BaseModel):
    id_usuario: int = Field(..., examples=[6])
    correo: str = Field(..., examples=["encargado.centro@raeehuancayo.pe"])
    rol: str = Field(..., examples=["ENCARGADO"])


class EstadoActualizadoRespuesta(BaseModel):
    actualizado: bool = Field(..., examples=[True])
