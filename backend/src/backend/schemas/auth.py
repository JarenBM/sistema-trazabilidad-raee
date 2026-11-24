"""Modelos de autenticación y sesión."""

from pydantic import BaseModel, Field

PATRON_CORREO = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegistroRequest(BaseModel):
    nombres: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Andrea Sofía"],
    )
    apellidos: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Vargas Salazar"],
    )
    correo: str = Field(
        ...,
        max_length=100,
        pattern=PATRON_CORREO,
        examples=["andrea.vargas@gmail.com"],
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
        examples=["954777888"],
    )
    ubigeo: str = Field(
        ...,
        pattern=r"^12\d{4}$",
        examples=["120114"],
    )
    direccion: str | None = Field(
        None,
        min_length=5,
        max_length=200,
        examples=["Jr. Los Andes 345, El Tambo"],
    )


class UsuarioSesionRespuesta(BaseModel):
    id_usuario: int = Field(..., examples=[4])
    nombres: str = Field(..., examples=["Andrea Sofía"])
    apellidos: str = Field(..., examples=["Vargas Salazar"])
    correo: str = Field(..., examples=["andrea.vargas@gmail.com"])
    rol: str = Field(..., examples=["CIUDADANO"])
    id_centro: int | None = Field(None, examples=[None])
    activo: bool = Field(..., examples=[True])


class TokenRespuesta(BaseModel):
    access_token: str = Field(
        ...,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0In0.firma"],
    )
    token_type: str = Field("bearer", examples=["bearer"])
    expira_en_minutos: int = Field(..., examples=[60])
    usuario: UsuarioSesionRespuesta
