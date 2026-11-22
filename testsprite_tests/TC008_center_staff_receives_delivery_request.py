import time
from datetime import datetime, timedelta, timezone

import requests


def test_center_staff_receives_delivery_request():
    base_url = "http://localhost:8000"
    timeout = 30
    timestamp = str(time.time_ns())
    admin_email = "admin@raeehuancayo.pe"
    admin_password = "Raee2026!"
    citizen_email = f"ts.citizen.{timestamp}@example.com"
    staff_one_email = f"ts.staff1.{timestamp}@example.com"
    staff_two_email = f"ts.staff2.{timestamp}@example.com"
    password = f"TS_Password_{timestamp}"

    def login(email, user_password):
        response = requests.post(
            f"{base_url}/api/auth/login",
            data={"username": email, "password": user_password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=timeout,
        )
        assert response.status_code == 200, (
            f"Login failed for {email}: {response.status_code} {response.text}"
        )
        token = response.json().get("access_token")
        assert token, f"Login response did not include an access token for {email}"
        return {"Authorization": f"Bearer {token}"}

    try:
        admin_headers = login(admin_email, admin_password)

        center_ids = []
        for suffix in ("1", "2"):
            center_response = requests.post(
                f"{base_url}/api/centros",
                json={
                    "nombre_centro": f"TS Centro {suffix} {timestamp}",
                    "direccion": f"Av. Test {suffix} {timestamp}",
                    "telefono": "987654321",
                    "ubigeo": "120101",
                    "latitud": -12.0651,
                    "longitud": -75.2049,
                },
                headers=admin_headers,
                timeout=timeout,
            )
            assert center_response.status_code == 201, (
                f"Center creation failed: {center_response.status_code} "
                f"{center_response.text}"
            )
            center_id = center_response.json().get("id_centro")
            assert center_id, f"Center response did not include id_centro: {center_response.text}"
            center_ids.append(center_id)

        staff_emails = (staff_one_email, staff_two_email)
        staff_headers = []
        for index, staff_email in enumerate(staff_emails):
            staff_response = requests.post(
                f"{base_url}/api/usuarios/encargado",
                json={
                    "nombres": f"TS Encargado {index + 1}",
                    "apellidos": f"Test {timestamp}",
                    "correo": staff_email,
                    "password": password,
                    "telefono": "987654321",
                    "ubigeo": "120101",
                    "direccion": f"Av. Test {index + 1} {timestamp}",
                    "id_centro": center_ids[index],
                },
                headers=admin_headers,
                timeout=timeout,
            )
            assert staff_response.status_code == 201, (
                f"Staff creation failed: {staff_response.status_code} "
                f"{staff_response.text}"
            )
            assert staff_response.json().get("rol") == "ENCARGADO"
            staff_headers.append(login(staff_email, password))

        registration_response = requests.post(
            f"{base_url}/api/auth/registro",
            json={
                "nombres": f"TS Ciudadano {timestamp}",
                "apellidos": "Test",
                "correo": citizen_email,
                "password": password,
                "telefono": "987654321",
                "ubigeo": "120101",
                "direccion": f"Direccion TS {timestamp}",
            },
            timeout=timeout,
        )
        assert registration_response.status_code == 201, (
            f"Citizen registration failed: {registration_response.status_code} "
            f"{registration_response.text}"
        )
        citizen_headers = login(citizen_email, password)

        categories_response = requests.get(
            f"{base_url}/api/catalogos/categorias", timeout=timeout
        )
        assert categories_response.status_code == 200, categories_response.text
        categories = categories_response.json()
        assert isinstance(categories, list) and categories, (
            f"No RAEE categories were available: {categories}"
        )
        category = categories[0]
        category_id = category.get("id_categoria")
        assert category_id, f"Category did not include id_categoria: {category}"

        device_response = requests.post(
            f"{base_url}/api/raee",
            json={
                "id_categoria": category_id,
                "marca": f"TS Marca {timestamp}"[:50],
                "modelo": f"TS Modelo {timestamp}"[:50],
                "descripcion": f"Test device {timestamp}",
            },
            headers=citizen_headers,
            timeout=timeout,
        )
        assert device_response.status_code == 201, (
            f"Device creation failed: {device_response.status_code} "
            f"{device_response.text}"
        )
        device_id = device_response.json().get("id_raee")
        assert device_id, f"Device response did not include id_raee: {device_response.text}"

        request_response = requests.post(
            f"{base_url}/api/solicitudes",
            json={
                "id_raee": device_id,
                "id_centro": center_ids[0],
                "tipo_solicitud": "PRESENCIAL",
                "fecha_programada": (
                    datetime.now(timezone.utc) + timedelta(days=2)
                ).isoformat(),
            },
            headers=citizen_headers,
            timeout=timeout,
        )
        assert request_response.status_code == 201, (
            f"Delivery request creation failed: {request_response.status_code} "
            f"{request_response.text}"
        )
        request_id = request_response.json().get("id_solicitud")
        assert request_id, (
            f"Request response did not include id_solicitud: {request_response.text}"
        )

        pending_response = requests.get(
            f"{base_url}/api/solicitudes/centro",
            params={"estado": "PENDIENTE"},
            headers=staff_headers[0],
            timeout=timeout,
        )
        assert pending_response.status_code == 200, pending_response.text
        pending_requests = pending_response.json()
        assert isinstance(pending_requests, list), (
            f"Expected a list of center requests: {pending_requests}"
        )
        assert any(
            item.get("id_solicitud") == request_id
            and item.get("estado_solicitud") == "PENDIENTE"
            for item in pending_requests
        ), f"Assigned staff could not see the pending request: {pending_requests}"

        other_center_response = requests.patch(
            f"{base_url}/api/solicitudes/{request_id}/recepcionar",
            headers=staff_headers[1],
            timeout=timeout,
        )
        assert other_center_response.status_code in (403, 404, 409), (
            "Staff assigned to another center should not receive this request; "
            f"got {other_center_response.status_code}: {other_center_response.text}"
        )

        receive_response = requests.patch(
            f"{base_url}/api/solicitudes/{request_id}/recepcionar",
            headers=staff_headers[0],
            timeout=timeout,
        )
        assert receive_response.status_code == 200, (
            f"Reception failed: {receive_response.status_code} "
            f"{receive_response.text}"
        )

        completed_response = requests.get(
            f"{base_url}/api/solicitudes/centro",
            params={"estado": "COMPLETADA"},
            headers=staff_headers[0],
            timeout=timeout,
        )
        assert completed_response.status_code == 200, completed_response.text
        completed_requests = completed_response.json()
        assert isinstance(completed_requests, list), (
            f"Expected a list of completed requests: {completed_requests}"
        )
        assert any(
            item.get("id_solicitud") == request_id
            and item.get("estado_solicitud") == "COMPLETADA"
            for item in completed_requests
        ), f"Request did not become COMPLETADA: {completed_requests}"

        devices_response = requests.get(
            f"{base_url}/api/raee/mios",
            headers=citizen_headers,
            timeout=timeout,
        )
        assert devices_response.status_code == 200, devices_response.text
        devices = devices_response.json()
        assert isinstance(devices, list), f"Expected a list of devices: {devices}"
        received_device = next(
            (item for item in devices if item.get("id_raee") == device_id), None
        )
        assert received_device is not None, (
            f"Created device was not present in the citizen's device list: {devices}"
        )
        assert received_device.get("estado_actual") == "RECIBIDO", (
            f"Expected device state RECIBIDO, got {received_device}"
        )

        repeated_response = requests.patch(
            f"{base_url}/api/solicitudes/{request_id}/recepcionar",
            headers=staff_headers[0],
            timeout=timeout,
        )
        assert repeated_response.status_code in (404, 409), (
            "Receiving an already completed request should be rejected; "
            f"got {repeated_response.status_code}: {repeated_response.text}"
        )
    except requests.RequestException as exc:
        raise AssertionError(f"HTTP request failed: {exc}") from exc


if __name__ == "__main__":
    test_center_staff_receives_delivery_request()
