import time
import uuid

import requests


BASE_URL = "http://localhost:8000"


def test_citizen_registration_validation():
    unique_id = f"TS_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    email = f"{unique_id.lower()}@example.com"
    payload = {
        "nombres": unique_id,
        "apellidos": "Test Ciudadano",
        "correo": email,
        "password": "TS_ValidPassword2026!",
        "telefono": "+51987654321",
        "ubigeo": "120101",
        "direccion": "Av. Test 123, Huancayo",
    }
    url = f"{BASE_URL.rstrip('/')}/api/auth/registro"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        assert response.status_code == 201, (
            f"Expected registration to return 201, got {response.status_code}: "
            f"{response.text}"
        )
        created_user = response.json()
        assert created_user["rol"] == "CIUDADANO", created_user
        assert created_user["activo"] is True, created_user
        assert created_user["correo"] == email, created_user
        assert isinstance(created_user["id_usuario"], int), created_user

        duplicate_response = requests.post(
            url, json=payload, headers=headers, timeout=30
        )
        assert duplicate_response.status_code == 409, (
            f"Expected duplicate email to return 409, got "
            f"{duplicate_response.status_code}: {duplicate_response.text}"
        )

        invalid_payload = {
            **payload,
            "correo": f"invalid-{unique_id}",
            "ubigeo": "99000",
        }
        invalid_response = requests.post(
            url, json=invalid_payload, headers=headers, timeout=30
        )
        assert invalid_response.status_code == 422, (
            f"Expected invalid registration fields to return 422, got "
            f"{invalid_response.status_code}: {invalid_response.text}"
        )
    except requests.RequestException as exc:
        raise AssertionError(f"Registration API request failed: {exc}") from exc


if __name__ == "__main__":
    test_citizen_registration_validation()