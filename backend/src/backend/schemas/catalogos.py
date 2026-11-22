"""Modelos de catálogos geográficos y de clasificación."""

from decimal import Decimal

from pydantic import BaseModel, Field


class DistritoRespuesta(BaseModel):
    ubigeo: str = Field(..., examples=["120114"])
    distrito: str = Field(..., examples=["El Tambo"])
    provincia: str = Field(..., examples=["Huancayo"])


class CategoriaRespuesta(BaseModel):
    id_categoria: int = Field(..., examples=[1])
    nombre: str = Field(..., examples=["Informática y Telecomunicaciones"])
    descripcion: str | None = Field(
        None,
        examples=["Laptops, computadoras de escritorio, monitores, teclados e impresoras."],
    )


class TipoDestinoRespuesta(BaseModel):
    id_tipo_destino: int = Field(..., examples=[3])
    nombre: str = Field(..., examples=["Recuperación de componentes"])
    descripcion: str | None = Field(
        None,
        examples=["Se extraen piezas útiles como RAM, discos y placas."],
    )
    es_valorizacion: bool = Field(..., examples=[True])


class CentroRespuesta(BaseModel):
    id_centro: int = Field(..., examples=[2])
    nombre_centro: str = Field(..., examples=["Centro de Acopio RAEE - El Tambo"])
    direccion: str = Field(..., examples=["Av. Mariscal Castilla 2450, El Tambo"])
    telefono: str | None = Field(None, examples=["064-248910"])
    ubigeo: str = Field(..., examples=["120114"])
    distrito: str = Field(..., examples=["El Tambo"])
    latitud: Decimal | None = Field(None, examples=[-12.049340])
    longitud: Decimal | None = Field(None, examples=[-75.218920])
    activo: bool = Field(..., examples=[True])
