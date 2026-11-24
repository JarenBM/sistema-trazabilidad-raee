"""Carga y validación de la configuración desde el archivo .env."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

RUTA_BACKEND = Path(__file__).resolve().parents[2]
load_dotenv(RUTA_BACKEND / ".env")


def _obtener_requerido(nombre: str) -> str:
    valor = os.getenv(nombre, "").strip()
    if not valor:
        raise RuntimeError(f"Falta la variable de entorno obligatoria: {nombre}")
    return valor


def _obtener_entero(nombre: str, valor_por_defecto: int) -> int:
    valor = os.getenv(nombre, "").strip()
    if not valor:
        return valor_por_defecto
    try:
        numero = int(valor)
    except ValueError as exc:
        raise RuntimeError(f"La variable {nombre} debe ser un número entero.") from exc
    if numero <= 0:
        raise RuntimeError(f"La variable {nombre} debe ser mayor que cero.")
    return numero


def _obtener_origenes_cors() -> list[str]:
    valor = os.getenv("CORS_ORIGINS", "http://localhost:4200")
    return [origen.strip() for origen in valor.split(",") if origen.strip()]


@dataclass(frozen=True)
class Configuracion:
    database_url: str
    jwt_secret: str
    jwt_expiracion_minutos: int
    cors_origins: list[str]


def _cargar_configuracion() -> Configuracion:
    database_url = _obtener_requerido("DATABASE_URL")
    jwt_secret = _obtener_requerido("JWT_SECRET")
    if len(jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET debe tener al menos 32 caracteres.")
    return Configuracion(
        database_url=database_url,
        jwt_secret=jwt_secret,
        jwt_expiracion_minutos=_obtener_entero("JWT_EXPIRACION_MINUTOS", 60),
        cors_origins=_obtener_origenes_cors(),
    )


configuracion = _cargar_configuracion()
