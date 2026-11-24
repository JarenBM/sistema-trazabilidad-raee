"""Punto de entrada de la API de gestión y trazabilidad de RAEE."""

import logging

import psycopg
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .apis import (
    auth,
    catalogos,
    centros,
    evaluaciones,
    health,
    publico,
    raee,
    reportes,
    solicitudes,
    usuarios,
)
from .config import configuracion
from .errors import ErrorDominio, NoAutorizadoError

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sistema de Gestión y Trazabilidad de RAEE",
    description=(
        "API para la gestión y trazabilidad de residuos de aparatos eléctricos "
        "y electrónicos en Huancayo, Junín."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(ErrorDominio)
async def manejar_error_dominio(_: Request, exc: ErrorDominio) -> JSONResponse:
    cabeceras = (
        {"WWW-Authenticate": "Bearer"}
        if isinstance(exc, NoAutorizadoError)
        else None
    )
    return JSONResponse(
        status_code=exc.codigo_http,
        content={"detail": exc.mensaje},
        headers=cabeceras,
    )


@app.exception_handler(psycopg.Error)
async def manejar_error_bd(_: Request, exc: psycopg.Error) -> JSONResponse:
    logger.error("Error de base de datos", exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "La base de datos no se encuentra disponible."},
    )


for enrutador in (
    health.router,
    auth.router,
    usuarios.router,
    catalogos.router,
    centros.router,
    publico.router,
    raee.router,
    solicitudes.router,
    evaluaciones.router,
    reportes.router,
):
    app.include_router(enrutador, prefix="/api")
