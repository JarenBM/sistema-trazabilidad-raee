"""Endpoints de catálogos (consulta pública)."""

from fastapi import APIRouter

from ..schemas.catalogos import (
    CategoriaRespuesta,
    CentroRespuesta,
    DistritoRespuesta,
    TipoDestinoRespuesta,
)
from ..services import catalogos_service

router = APIRouter(prefix="/catalogos", tags=["Catálogos"])


@router.get(
    "/distritos",
    response_model=list[DistritoRespuesta],
    summary="Listar distritos de Junín",
)
def listar_distritos() -> list[DistritoRespuesta]:
    return catalogos_service.listar_distritos()


@router.get(
    "/categorias",
    response_model=list[CategoriaRespuesta],
    summary="Listar categorías de RAEE",
)
def listar_categorias() -> list[CategoriaRespuesta]:
    return catalogos_service.listar_categorias()


@router.get(
    "/tipos-destino",
    response_model=list[TipoDestinoRespuesta],
    summary="Listar tipos de destino ambiental",
)
def listar_tipos_destino() -> list[TipoDestinoRespuesta]:
    return catalogos_service.listar_tipos_destino()


@router.get(
    "/centros",
    response_model=list[CentroRespuesta],
    summary="Listar centros de acopio",
)
def listar_centros(solo_activos: bool = True) -> list[CentroRespuesta]:
    return catalogos_service.listar_centros(solo_activos)
