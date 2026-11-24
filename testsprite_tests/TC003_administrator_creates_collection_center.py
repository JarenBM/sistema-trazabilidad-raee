import time

import requests


def test_administrator_creates_collection_center():
    base_url = "http://localhost:8000"
    session = requests.Session()
    timestamp = time.time_ns()
    admin_credentials = {
        "username": "admin@raeehuancayo.pe",
        "password": "Raee2026!",
    }
    citizen_email = f"tc003_{timestamp}@example.com"
    citizen_password = "TC003-TestPassword2026!"

    try:
        admin_login = session.post(
            f"{base_url}/api/auth/login",
            data=admin_credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        assert admin_login.status_code == 200, (
            f"Admin login failed: {admin_login.status_code} {admin_login.text}"
        )
        admin_token = admin_login.json().get("access_token")
        assert admin_token, "Admin login response did not include an access token"
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        citizen_data = {
            "nombres": "TC003",
            "apellidos": f"Usuario {timestamp}",
            "correo": citizen_email,
            "password": citizen_password,
            "ubigeo": "120101",
        }
        citizen_registration = session.post(
            f"{base_url}/api/auth/registro",
            json=citizen_data,
            timeout=30,
        )
        assert citizen_registration.status_code == 201, (
            f"Citizen registration failed: {citizen_registration.status_code} "
            f"{citizen_registration.text}"
        )

        citizen_login = session.post(
            f"{base_url}/api/auth/login",
            data={"username": citizen_email, "password": citizen_password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        assert citizen_login.status_code == 200, (
            f"Citizen login failed: {citizen_login.status_code} {citizen_login.text}"
        )
        citizen_token = citizen_login.json().get("access_token")
        assert citizen_token, "Citizen login response did not include an access token"

        valid_center = {
            "nombre_centro": f"TC003 Centro {timestamp}",
            "direccion": f"Direccion de prueba {timestamp}",
            "telefono": "987654321",
            "ubigeo": "120101",
            "latitud": -12.0651,
            "longitud": -75.2049,
        }
        create_response = session.post(
            f"{base_url}/api/centros",
            json=valid_center,
            headers=admin_headers,
            timeout=30,
        )
        assert create_response.status_code == 201, (
            f"Creating a valid center failed: {create_response.status_code} "
            f"{create_response.text}"
        )
        center_id = create_response.json().get("id_centro")
        assert isinstance(center_id, int) and center_id > 0, (
            f"Expected a positive integer id_centro, got {center_id!r}"
        )

        invalid_ubigeo = {
            **valid_center,
            "nombre_centro": f"TC003 Invalid Ubigeo {timestamp}",
            "ubigeo": "999999",
        }
        ubigeo_response = session.post(
            f"{base_url}/api/centros",
            json=invalid_ubigeo,
            headers=admin_headers,
            timeout=30,
        )
        assert ubigeo_response.status_code == 422, (
            f"Invalid ubigeo should return 422, got {ubigeo_response.status_code}: "
            f"{ubigeo_response.text}"
        )

        invalid_latitude = {
            **valid_center,
            "nombre_centro": f"TC003 Invalid Latitude {timestamp}",
            "latitud": 91,
        }
        latitude_response = session.post(
            f"{base_url}/api/centros",
            json=invalid_latitude,
            headers=admin_headers,
            timeout=30,
        )
        assert latitude_response.status_code == 422, (
            f"Out-of-range latitude should return 422, got "
            f"{latitude_response.status_code}: {latitude_response.text}"
        )

        invalid_longitude = {
            **valid_center,
            "nombre_centro": f"TC003 Invalid Longitude {timestamp}",
            "longitud": 181,
        }
        longitude_response = session.post(
            f"{base_url}/api/centros",
            json=invalid_longitude,
            headers=admin_headers,
            timeout=30,
        )
        assert longitude_response.status_code == 422, (
            f"Out-of-range longitude should return 422, got "
            f"{longitude_response.status_code}: {longitude_response.text}"
        )

        forbidden_response = session.post(
            f"{base_url}/api/centros",
            json={
                **valid_center,
                "nombre_centro": f"TC003 Nonadmin Attempt {timestamp}",
            },
            headers={"Authorization": f"Bearer {citizen_token}"},
            timeout=30,
        )
        assert forbidden_response.status_code == 403, (
            f"Non-administrator should receive 403, got "
            f"{forbidden_response.status_code}: {forbidden_response.text}"
        )

    except requests.RequestException as exc:
        raise AssertionError(f"HTTP request failed: {exc}") from exc
    finally:
        session.close()


if __name__ == "__main__":
    test_administrator_creates_collection_center()