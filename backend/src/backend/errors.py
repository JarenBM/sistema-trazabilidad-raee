"""Excepciones de dominio traducidas a respuestas HTTP en main.py."""


class ErrorDominio(Exception):
    """Error de negocio con su código HTTP asociado."""

    codigo_http: int = 500

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontradoError(ErrorDominio):
    codigo_http = 404


class ConflictoNegocioError(ErrorDominio):
    codigo_http = 409


class NoAutorizadoError(ErrorDominio):
    codigo_http = 401


class ProhibidoError(ErrorDominio):
    codigo_http = 403
