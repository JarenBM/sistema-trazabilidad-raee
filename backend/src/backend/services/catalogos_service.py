"""Servicios de catálogos."""

from ..repositories import catalogo_repositorio
from ..schemas.catalogos import (
    CategoriaRespuesta,
    CentroRespuesta,
    DistritoRespuesta,
    TipoDestinoRespuesta,
)


def listar_distritos() -> list[DistritoRespuesta]:
    return [
        DistritoRespuesta.model_validate(fila)
        for fila in catalogo_repositorio.distritos()
    ]


def listar_categorias() -> list[CategoriaRespuesta]:
    return [
        CategoriaRespuesta.model_validate(fila)
        for fila in catalogo_repositorio.categorias()
    ]


def listar_tipos_destino() -> list[TipoDestinoRespuesta]:
    return [
        TipoDestinoRespuesta.model_validate(fila)
        for fila in catalogo_repositorio.tipos_destino()
    ]


def listar_centros(solo_activos: bool = True) -> list[CentroRespuesta]:
    return [
        CentroRespuesta.model_validate(fila)
        for fila in catalogo_repositorio.centros(solo_activos)
    ]
