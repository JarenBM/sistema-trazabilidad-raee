"""Modelos de respuesta del health check."""

from pydantic import BaseModel, Field


class SaludRespuesta(BaseModel):
    ok: bool = Field(..., examples=[True])
    base_datos: str = Field(..., examples=["conectada"])
