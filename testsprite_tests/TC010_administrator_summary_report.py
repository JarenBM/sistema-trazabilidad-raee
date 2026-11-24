import math
import uuid

import requests


def test_administrator_summary_report():
    base_url = "http://localhost:8000"
    session = requests.Session()
    suffix = f"{int(__import__('time').time())}_{uuid.uuid4().hex[:8]}"
    citizen_email = f"ts_{suffix}@example.com"

    try:
        admin_login = session.post(
            f"{base_url}/api/auth/login",
            data={
                "username": "admin@raeehuancayo.pe",
                "password": "Raee2026!",
            },
            timeout=30,
        )
        assert admin_login.status_code == 200, (
            f"Administrator login failed: {admin_login.status_code} "
            f"{admin_login.text}"
        )
        admin_token = admin_login.json().get("access_token")
        assert admin_token, "Administrator login response did not include access_token"

        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        report_response = session.get(
            f"{base_url}/api/reportes/resumen",
            headers=admin_headers,
            timeout=30,
        )
        assert report_response.status_code == 200, (
            f"Summary report failed: {report_response.status_code} "
            f"{report_response.text}"
        )

        report = report_response.json()
        required_integer_fields = (
            "total_dispositivos",
            "total_registrados",
            "total_solicitados",
            "total_recibidos",
            "total_evaluados",
        )
        required_weight_fields = (
            "peso_total_kg",
            "peso_valorizado_kg",
            "peso_disposicion_final_kg",
        )

        for field in required_integer_fields:
            assert field in report, f"Report is missing required field {field}"
            assert isinstance(report[field], int) and not isinstance(
                report[field], bool
            ), f"{field} should be an integer"
            assert report[field] >= 0, f"{field} cannot be negative"

        for field in required_weight_fields:
            assert field in report, f"Report is missing required field {field}"
            value = float(report[field])
            assert math.isfinite(value), f"{field} should be a finite number"
            assert value >= 0, f"{field} cannot be negative"

        if report["total_dispositivos"] == 0:
            for field in required_integer_fields:
                assert report[field] == 0, (
                    f"Expected {field} to be zero for an empty dataset"
                )
            for field in required_weight_fields:
                assert math.isclose(
                    float(report[field]), 0.0, abs_tol=0.01
                ), f"Expected {field} to be zero or near-zero for an empty dataset"

        if report["total_evaluados"] == 0:
            for field in required_weight_fields:
                assert math.isclose(
                    float(report[field]), 0.0, abs_tol=0.01
                ), f"Expected {field} to be zero or near-zero without evaluated devices"

        registration_response = session.post(
            f"{base_url}/api/auth/registro",
            json={
                "nombres": f"TS_{suffix}",
                "apellidos": "Report Test",
                "correo": citizen_email,
                "password": f"TS_{uuid.uuid4().hex[:12]}",
                "telefono": "987654321",
                "ubigeo": "120101",
                "direccion": "Direccion de prueba TS",
            },
            timeout=30,
        )
        assert registration_response.status_code == 201, (
            f"Non-admin test account registration failed: "
            f"{registration_response.status_code} {registration_response.text}"
        )

        citizen_password = registration_response.request.body
        citizen_password = (
            f"TS_{registration_response.json().get('id_usuario')}_{suffix}"
        )
        citizen_password = citizen_password[:128]

        citizen_login = session.post(
            f"{base_url}/api/auth/login",
            data={
                "username": citizen_email,
                "password": citizen_password,
            },
            timeout=30,
        )
        if citizen_login.status_code != 200:
            fallback_password = None
            try:
                request_body = registration_response.request.body
                if isinstance(request_body, bytes):
                    request_body = request_body.decode("utf-8")
                if isinstance(request_body, str):
                    import json

                    fallback_password = json.loads(request_body).get("password")
            except (TypeError, ValueError):
                pass

            if fallback_password:
                citizen_login = session.post(
                    f"{base_url}/api/auth/login",
                    data={
                        "username": citizen_email,
                        "password": fallback_password,
                    },
                    timeout=30,
                )

        assert citizen_login.status_code == 200, (
            f"Non-administrator login failed: {citizen_login.status_code} "
            f"{citizen_login.text}"
        )
        citizen_token = citizen_login.json().get("access_token")
        assert citizen_token, "Non-administrator login did not include access_token"

        forbidden_response = session.get(
            f"{base_url}/api/reportes/resumen",
            headers={"Authorization": f"Bearer {citizen_token}"},
            timeout=30,
        )
        assert forbidden_response.status_code == 403, (
            f"Expected non-administrator access to return HTTP 403, got "
            f"{forbidden_response.status_code}: {forbidden_response.text}"
        )

    except requests.RequestException as exc:
        raise AssertionError(f"HTTP request failed: {exc}") from exc
    finally:
        session.close()


if __name__ == "__main__":
    test_administrator_summary_report()