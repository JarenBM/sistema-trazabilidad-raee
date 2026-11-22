import re
import time

import requests


BASE_URL = "http://localhost:8000"


def test_citizen_device_registration():
    session = requests.Session()
    timestamp = str(time.time_ns())
    email = f"TS_{timestamp}@example.com"
    password = "TS_DevicePass2026!"

    try:
        registration = session.post(
            f"{BASE_URL}/api/auth/registro",
            json={
                "nombres": f"TS{timestamp[-8:]}",
                "apellidos": "Device Test",
                "correo": email,
                "password": password,
                "telefono": "987654321",
                "ubigeo": "120101",
                "direccion": "Calle de prueba 123",
            },
            timeout=30,
        )
        assert registration.status_code == 201, (
            f"Citizen registration failed: {registration.status_code} "
            f"{registration.text}"
        )
        registered_user = registration.json()
        assert registered_user.get("rol") == "CIUDADANO"
        assert registered_user.get("activo") is True

        login = session.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        assert login.status_code == 200, f"Citizen login failed: {login.text}"
        token = login.json().get("access_token")
        assert token, "Login response did not include an access token"
        headers = {"Authorization": f"Bearer {token}"}

        categories_response = session.get(
            f"{BASE_URL}/api/catalogos/categorias", timeout=30
        )
        assert categories_response.status_code == 200, (
            f"Could not retrieve RAEE categories: {categories_response.text}"
        )
        categories = categories_response.json()
        assert isinstance(categories, list) and categories, (
            "The category catalog is empty or not a list"
        )
        category = categories[0]
        category_id = category.get("id_categoria", category.get("id"))
        assert isinstance(category_id, int) and category_id > 0, (
            f"Could not determine a valid category ID: {category}"
        )

        valid_device = {
            "id_categoria": category_id,
            "marca": "TS Brand",
            "modelo": f"TS-{timestamp[-10:]}",
            "descripcion": "Dispositivo de prueba de registro",
        }

        unauthenticated_response = session.post(
            f"{BASE_URL}/api/raee", json=valid_device, timeout=30
        )
        assert unauthenticated_response.status_code == 401, (
            "Unauthenticated device registration should return HTTP 401; "
            f"got {unauthenticated_response.status_code}: "
            f"{unauthenticated_response.text}"
        )

        invalid_category_response = session.post(
            f"{BASE_URL}/api/raee",
            json={**valid_device, "id_categoria": 0},
            headers=headers,
            timeout=30,
        )
        assert invalid_category_response.status_code == 422, (
            "Invalid category should return HTTP 422; "
            f"got {invalid_category_response.status_code}: "
            f"{invalid_category_response.text}"
        )

        invalid_fields_response = session.post(
            f"{BASE_URL}/api/raee",
            json={**valid_device, "marca": ""},
            headers=headers,
            timeout=30,
        )
        assert invalid_fields_response.status_code == 422, (
            "Malformed device fields should return HTTP 422; "
            f"got {invalid_fields_response.status_code}: "
            f"{invalid_fields_response.text}"
        )

        creation_response = session.post(
            f"{BASE_URL}/api/raee",
            json=valid_device,
            headers=headers,
            timeout=30,
        )
        assert creation_response.status_code == 201, (
            f"Device registration failed: {creation_response.status_code} "
            f"{creation_response.text}"
        )
        created_device = creation_response.json()
        assert created_device.get("id_raee") is not None
        tracking_code = created_device.get("codigo_seguimiento")
        assert isinstance(tracking_code, str) and tracking_code, (
            "The created device did not include a tracking code"
        )
        assert re.fullmatch(r"RAEE-\d{4}-\d{4}", tracking_code), (
            f"Tracking code has an unexpected format: {tracking_code}"
        )

        devices_response = session.get(
            f"{BASE_URL}/api/raee/mios", headers=headers, timeout=30
        )
        assert devices_response.status_code == 200, (
            f"Could not retrieve citizen devices: {devices_response.text}"
        )
        devices = devices_response.json()
        assert isinstance(devices, list), "Citizen device response should be a list"

        matching_devices = [
            device
            for device in devices
            if device.get("codigo_seguimiento") == tracking_code
        ]
        assert len(matching_devices) == 1, (
            "The newly registered tracking code should occur exactly once "
            "in the citizen's device list"
        )
        device = matching_devices[0]
        state = device.get("estado", device.get("estado_actual"))
        assert state == "REGISTRADO", (
            f"Expected initial state REGISTRADO, got {state!r}"
        )

    except requests.RequestException as exc:
        raise AssertionError(f"HTTP request failed during device registration test: {exc}") from exc


if __name__ == "__main__":
    test_citizen_device_registration()