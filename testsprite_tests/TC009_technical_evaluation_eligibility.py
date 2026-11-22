import uuid
from datetime import datetime, timedelta, timezone

import requests


def test_technical_evaluation_eligibility():
    base_url = "http://localhost:8000"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    unique = f"TS_{timestamp}_{uuid.uuid4().hex[:8]}"

    try:
        admin_login = requests.post(
            f"{base_url}/api/auth/login",
            data={"username": "admin@raeehuancayo.pe", "password": "Raee2026!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        assert admin_login.status_code == 200, admin_login.text
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        centers_response = requests.get(
            f"{base_url}/api/catalogos/centros",
            params={"solo_activos": "true"},
            timeout=30,
        )
        assert centers_response.status_code == 200, centers_response.text
        centers = centers_response.json()
        assert isinstance(centers, list) and centers, "No active collection centers are available"
        center_id = centers[0]["id_centro"]

        categories_response = requests.get(
            f"{base_url}/api/catalogos/categorias",
            timeout=30,
        )
        assert categories_response.status_code == 200, categories_response.text
        categories = categories_response.json()
        assert isinstance(categories, list) and categories, "No RAEE categories are available"
        category_id = categories[0]["id_categoria"]

        destinations_response = requests.get(
            f"{base_url}/api/catalogos/tipos-destino",
            timeout=30,
        )
        assert destinations_response.status_code == 200, destinations_response.text
        destinations = destinations_response.json()
        assert isinstance(destinations, list) and destinations, "No environmental destination types are available"
        destination_id = destinations[0]["id_tipo_destino"]

        staff_payload = {
            "nombres": f"Encargado {unique}",
            "apellidos": "Evaluacion Prueba",
            "correo": f"{unique.lower()}@example.com",
            "password": f"Test_{uuid.uuid4().hex[:12]}!",
            "telefono": "987654321",
            "ubigeo": "120101",
            "direccion": "Direccion de prueba RAEE",
            "id_centro": center_id,
        }
        staff_create = requests.post(
            f"{base_url}/api/usuarios/encargado",
            json=staff_payload,
            headers=admin_headers,
            timeout=30,
        )
        assert staff_create.status_code == 201, staff_create.text

        citizen_payload = {
            "nombres": f"Ciudadano {unique}",
            "apellidos": "Prueba Evaluacion",
            "correo": f"citizen.{unique.lower()}@example.com",
            "password": f"Test_{uuid.uuid4().hex[:12]}!",
            "telefono": "987654321",
            "ubigeo": "120101",
            "direccion": "Direccion de prueba RAEE",
        }
        citizen_create = requests.post(
            f"{base_url}/api/auth/registro",
            json=citizen_payload,
            timeout=30,
        )
        assert citizen_create.status_code == 201, citizen_create.text

        citizen_login = requests.post(
            f"{base_url}/api/auth/login",
            data={
                "username": citizen_payload["correo"],
                "password": citizen_payload["password"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        assert citizen_login.status_code == 200, citizen_login.text
        citizen_token = citizen_login.json()["access_token"]
        citizen_headers = {"Authorization": f"Bearer {citizen_token}"}

        def create_device(suffix):
            response = requests.post(
                f"{base_url}/api/raee",
                json={
                    "id_categoria": category_id,
                    "marca": f"Marca {suffix}",
                    "modelo": f"Modelo {suffix}",
                    "descripcion": f"Dispositivo de prueba {unique} {suffix}",
                },
                headers=citizen_headers,
                timeout=30,
            )
            assert response.status_code == 201, response.text
            return response.json()["id_raee"]

        eligible_device_id = create_device("EVAL")
        ineligible_device_id = create_device("INELIGIBLE")

        request_response = requests.post(
            f"{base_url}/api/solicitudes",
            json={
                "id_raee": eligible_device_id,
                "id_centro": center_id,
                "tipo_solicitud": "PRESENCIAL",
                "fecha_programada": (
                    datetime.now(timezone.utc) + timedelta(days=1)
                ).isoformat(),
            },
            headers=citizen_headers,
            timeout=30,
        )
        assert request_response.status_code == 201, request_response.text
        request_id = request_response.json()["id_solicitud"]

        staff_login = requests.post(
            f"{base_url}/api/auth/login",
            data={
                "username": staff_payload["correo"],
                "password": staff_payload["password"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        assert staff_login.status_code == 200, staff_login.text
        staff_token = staff_login.json()["access_token"]
        staff_headers = {"Authorization": f"Bearer {staff_token}"}

        reception_response = requests.patch(
            f"{base_url}/api/solicitudes/{request_id}/recepcionar",
            headers=staff_headers,
            timeout=30,
        )
        assert reception_response.status_code == 200, reception_response.text

        def get_owned_device_state(device_id):
            response = requests.get(
                f"{base_url}/api/raee/mios",
                headers=citizen_headers,
                timeout=30,
            )
            assert response.status_code == 200, response.text
            devices = response.json()
            assert isinstance(devices, list), f"Expected a device list, got {devices!r}"
            device = next(
                (item for item in devices if item.get("id_raee") == device_id),
                None,
            )
            assert device is not None, f"Device {device_id} was not found in its owner's list"
            state = device.get("estado", device.get("estado_actual"))
            assert state is not None, f"Device response does not include a state: {device!r}"
            return state

        assert get_owned_device_state(eligible_device_id) == "RECIBIDO"

        invalid_evaluation = requests.post(
            f"{base_url}/api/evaluaciones",
            json={
                "id_raee": eligible_device_id,
                "id_tipo_destino": destination_id,
                "condicion_fisica": "INVALIDA",
                "es_operativo": True,
                "peso_kg": 0,
            },
            headers=staff_headers,
            timeout=30,
        )
        assert invalid_evaluation.status_code == 422, invalid_evaluation.text

        ineligible_evaluation = requests.post(
            f"{base_url}/api/evaluaciones",
            json={
                "id_raee": ineligible_device_id,
                "id_tipo_destino": destination_id,
                "condicion_fisica": "REGULAR",
                "es_operativo": True,
                "peso_kg": 1.25,
                "observaciones": f"Prueba de elegibilidad {unique}",
            },
            headers=staff_headers,
            timeout=30,
        )
        assert ineligible_evaluation.status_code in (404, 409), ineligible_evaluation.text

        non_staff_evaluation = requests.post(
            f"{base_url}/api/evaluaciones",
            json={
                "id_raee": ineligible_device_id,
                "id_tipo_destino": destination_id,
                "condicion_fisica": "REGULAR",
                "es_operativo": True,
                "peso_kg": 1.25,
            },
            headers=citizen_headers,
            timeout=30,
        )
        assert non_staff_evaluation.status_code == 403, non_staff_evaluation.text

        valid_evaluation = requests.post(
            f"{base_url}/api/evaluaciones",
            json={
                "id_raee": eligible_device_id,
                "id_tipo_destino": destination_id,
                "condicion_fisica": "REGULAR",
                "es_operativo": True,
                "peso_kg": 2.5,
                "observaciones": f"Evaluacion tecnica {unique}",
            },
            headers=staff_headers,
            timeout=30,
        )
        assert valid_evaluation.status_code == 201, valid_evaluation.text
        assert "id_evaluacion" in valid_evaluation.json()

        assert get_owned_device_state(eligible_device_id) == "EVALUADO"

    except requests.RequestException as exc:
        raise AssertionError(f"HTTP request failed: {exc}") from exc


if __name__ == "__main__":
    test_technical_evaluation_eligibility()