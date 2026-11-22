import uuid
from datetime import datetime, timedelta, timezone

import requests


def test_delivery_request_creation_rules():
    base_url = "http://localhost:8000"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    email = f"TS_{timestamp}_{uuid.uuid4().hex[:8]}@example.com"
    password = "TS_TestPassword2026!"
    session = requests.Session()
    solicitud_id = None
    citizen_token = None

    try:
        admin_login = session.post(
            f"{base_url}/api/auth/login",
            data={"username": "admin@raeehuancayo.pe", "password": "Raee2026!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        assert admin_login.status_code == 200, (
            f"Admin login failed: {admin_login.status_code} {admin_login.text}"
        )
        admin_token = admin_login.json()["access_token"]

        centers_response = session.get(
            f"{base_url}/api/catalogos/centros",
            params={"solo_activos": "true"},
            timeout=30,
        )
        assert centers_response.status_code == 200, (
            f"Center catalog failed: {centers_response.status_code} {centers_response.text}"
        )
        centers = centers_response.json()
        assert centers, "At least one active collection center is required"
        center_id = centers[0]["id_centro"]

        categories_response = session.get(
            f"{base_url}/api/catalogos/categorias",
            timeout=30,
        )
        assert categories_response.status_code == 200, (
            f"Category catalog failed: {categories_response.status_code} {categories_response.text}"
        )
        categories = categories_response.json()
        assert categories, "At least one RAEE category is required"
        category_id = categories[0]["id_categoria"]

        registration_response = session.post(
            f"{base_url}/api/auth/registro",
            json={
                "nombres": f"TS{timestamp[-8:]}",
                "apellidos": "Test Citizen",
                "correo": email,
                "password": password,
                "ubigeo": "120101",
                "direccion": "TS Test address 123",
            },
            timeout=30,
        )
        assert registration_response.status_code == 201, (
            f"Citizen registration failed: "
            f"{registration_response.status_code} {registration_response.text}"
        )

        citizen_login = session.post(
            f"{base_url}/api/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        assert citizen_login.status_code == 200, (
            f"Citizen login failed: {citizen_login.status_code} {citizen_login.text}"
        )
        citizen_token = citizen_login.json()["access_token"]
        citizen_headers = {"Authorization": f"Bearer {citizen_token}"}

        device_response = session.post(
            f"{base_url}/api/raee",
            json={
                "id_categoria": category_id,
                "marca": f"TS{timestamp[-8:]}",
                "modelo": "Delivery request test",
                "descripcion": "Device created for delivery request rules test",
            },
            headers=citizen_headers,
            timeout=30,
        )
        assert device_response.status_code == 201, (
            f"Device creation failed: {device_response.status_code} {device_response.text}"
        )
        device_id = device_response.json()["id_raee"]

        my_devices_response = session.get(
            f"{base_url}/api/raee/mios",
            headers=citizen_headers,
            timeout=30,
        )
        assert my_devices_response.status_code == 200, (
            f"Listing own devices failed: "
            f"{my_devices_response.status_code} {my_devices_response.text}"
        )
        my_devices = my_devices_response.json()
        device = next(
            (item for item in my_devices if item.get("id_raee") == device_id),
            None,
        )
        assert device is not None, "The newly created device was not listed as citizen-owned"
        assert device.get("estado") == "REGISTRADO" or device.get("estado_actual") == "REGISTRADO", (
            f"New device should be REGISTRADO, received: {device}"
        )

        request_payload = {
            "id_raee": device_id,
            "id_centro": center_id,
            "tipo_solicitud": "PRESENCIAL",
            "fecha_programada": (
                datetime.now(timezone.utc) + timedelta(days=7)
            ).isoformat(),
        }
        creation_response = session.post(
            f"{base_url}/api/solicitudes",
            json=request_payload,
            headers=citizen_headers,
            timeout=30,
        )
        if creation_response.status_code == 201:
            solicitud_id = creation_response.json().get("id_solicitud")

        try:
            assert creation_response.status_code == 201, (
                f"Delivery request creation should return 201: "
                f"{creation_response.status_code} {creation_response.text}"
            )
            assert solicitud_id is not None, (
                f"Successful response did not include id_solicitud: {creation_response.text}"
            )

            duplicate_response = session.post(
                f"{base_url}/api/solicitudes",
                json=request_payload,
                headers=citizen_headers,
                timeout=30,
            )
            assert duplicate_response.status_code == 409, (
                f"Second pending request should return 409: "
                f"{duplicate_response.status_code} {duplicate_response.text}"
            )

            invalid_payload = {
                **request_payload,
                "tipo_solicitud": "INVALIDO",
            }
            invalid_response = session.post(
                f"{base_url}/api/solicitudes",
                json=invalid_payload,
                headers=citizen_headers,
                timeout=30,
            )
            assert invalid_response.status_code == 422, (
                f"Invalid request data should return 422: "
                f"{invalid_response.status_code} {invalid_response.text}"
            )
        finally:
            if solicitud_id is not None and citizen_token is not None:
                cancellation_response = session.patch(
                    f"{base_url}/api/solicitudes/{solicitud_id}/cancelar",
                    headers=citizen_headers,
                    timeout=30,
                )
                assert cancellation_response.status_code == 200, (
                    f"Could not cancel the test-created pending request: "
                    f"{cancellation_response.status_code} {cancellation_response.text}"
                )

    except requests.RequestException as exc:
        raise AssertionError(f"HTTP request failed: {exc}") from exc


if __name__ == "__main__":
    test_delivery_request_creation_rules()