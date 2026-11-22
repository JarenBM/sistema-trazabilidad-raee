"""Pruebas de humo offline: no requieren conexión a Supabase."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.security import (
    crear_token_acceso,
    decodificar_token,
    hash_password,
    verificar_password,
)

cliente = TestClient(app)


def test_openapi_disponible() -> None:
    respuesta = cliente.get("/openapi.json")

    assert respuesta.status_code == 200
    rutas = respuesta.json()["paths"]
    assert "/api/health" in rutas
    assert "/api/auth/login" in rutas


def test_documentacion_swagger_disponible() -> None:
    respuesta = cliente.get("/docs")

    assert respuesta.status_code == 200


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("GET", "/api/auth/me"),
        ("GET", "/api/usuarios"),
        ("POST", "/api/usuarios/encargado"),
        ("PATCH", "/api/usuarios/1/estado"),
        ("POST", "/api/centros"),
        ("PATCH", "/api/centros/1/estado"),
        ("POST", "/api/raee"),
        ("GET", "/api/raee/mios"),
        ("POST", "/api/solicitudes"),
        ("PATCH", "/api/solicitudes/1/cancelar"),
        ("GET", "/api/solicitudes/centro"),
        ("PATCH", "/api/solicitudes/1/recepcionar"),
        ("POST", "/api/evaluaciones"),
        ("GET", "/api/reportes/resumen"),
    ],
)
def test_rutas_protegidas_requieren_token(metodo: str, ruta: str) -> None:
    respuesta = cliente.request(metodo, ruta)

    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"].lower().startswith("bearer")


def test_token_invalido_es_rechazado() -> None:
    respuesta = cliente.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert respuesta.status_code == 401


def test_cors_permite_al_frontend() -> None:
    respuesta = cliente.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert respuesta.status_code == 200
    assert (
        respuesta.headers["access-control-allow-origin"]
        == "http://localhost:4200"
    )


def test_hash_argon2_verifica_correctamente() -> None:
    password_hash = hash_password("ClaveSegura123")

    assert verificar_password("ClaveSegura123", password_hash) is True
    assert verificar_password("OtraClave456", password_hash) is False


def test_hash_invalido_devuelve_falso_sin_excepcion() -> None:
    assert verificar_password("ClaveSegura123", "$2b$10$hashfalso") is False


def test_jwt_ida_y_vuelta() -> None:
    token, expira_minutos = crear_token_acceso(
        id_usuario=4,
        correo="andrea.vargas@gmail.com",
        rol="CIUDADANO",
        id_centro=None,
    )

    payload = decodificar_token(token)
    assert payload["sub"] == "4"
    assert payload["correo"] == "andrea.vargas@gmail.com"
    assert payload["rol"] == "CIUDADANO"
    assert payload["id_centro"] is None
    assert expira_minutos == 60
