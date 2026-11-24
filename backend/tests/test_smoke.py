"""Pruebas de humo offline: no requieren conexión a Supabase."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas.solicitudes import SolicitudCiudadanoRespuesta
from backend.security import (
    crear_token_acceso,
    decodificar_token,
    hash_password,
    verificar_password,
)
from backend.services import solicitudes_service

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
        ("GET", "/api/solicitudes/mias"),
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


def _token_de_prueba(rol: str, id_usuario: int = 4) -> str:
    token, _ = crear_token_acceso(
        id_usuario=id_usuario,
        correo="prueba@raeehuancayo.pe",
        rol=rol,
        id_centro=None,
    )
    return token


def test_listar_mias_mapea_las_filas_del_repositorio(monkeypatch) -> None:
    fila = {
        "id_solicitud": 7,
        "id_raee": 3,
        "codigo_seguimiento": "RAEE-2026-0003",
        "tipo_solicitud": "PRESENCIAL",
        "fecha_programada": datetime(2026, 12, 1, 10, 30, tzinfo=timezone.utc),
        "estado_solicitud": "PENDIENTE",
    }
    monkeypatch.setattr(
        solicitudes_service.solicitud_repositorio,
        "listar_por_usuario",
        lambda id_usuario: [fila],
    )

    resultado = solicitudes_service.listar_mias(4)

    assert len(resultado) == 1
    assert resultado[0].id_solicitud == 7
    assert resultado[0].codigo_seguimiento == "RAEE-2026-0003"
    assert resultado[0].estado_solicitud == "PENDIENTE"


def test_listar_mias_responde_al_ciudadano(monkeypatch) -> None:
    monkeypatch.setattr(
        solicitudes_service,
        "listar_mias",
        lambda id_usuario: [
            SolicitudCiudadanoRespuesta(
                id_solicitud=7,
                id_raee=3,
                codigo_seguimiento="RAEE-2026-0003",
                tipo_solicitud="RECOLECCION",
                fecha_programada=datetime(
                    2026, 12, 1, 10, 30, tzinfo=timezone.utc
                ),
                estado_solicitud="PENDIENTE",
            )
        ],
    )

    respuesta = cliente.get(
        "/api/solicitudes/mias",
        headers={"Authorization": f"Bearer {_token_de_prueba('CIUDADANO')}"},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo[0]["codigo_seguimiento"] == "RAEE-2026-0003"
    assert cuerpo[0]["tipo_solicitud"] == "RECOLECCION"


def test_listar_mias_rechaza_roles_distintos_de_ciudadano() -> None:
    respuesta = cliente.get(
        "/api/solicitudes/mias",
        headers={"Authorization": f"Bearer {_token_de_prueba('ENCARGADO')}"},
    )

    assert respuesta.status_code == 403

