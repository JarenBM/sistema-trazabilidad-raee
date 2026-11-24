import time
from urllib.parse import quote

import requests


BASE_URL = "http://localhost:8000"


def test_public_tracking_lookup_privacy():
    session = requests.Session()
    timestamp = str(time.time_ns())
    email = f"ts_privacy_{timestamp}@example.com"
    password = f"TS_Password_{timestamp}"
    brand = f"TSBrand{timestamp[-8:]}"
    model = f"TSModel{timestamp[-8:]}"
    nombres = f"TS{timestamp[-8:]}"
    apellidos = f"Privacy{timestamp[-8:]}"
    tracking_code = None

    try:
        registration = session.post(
            f"{BASE_URL}/api/auth/registro",
            json={
                "nombres": nombres,
                "apellidos": apellidos,
                "correo": email,
                "password": password,
                "ubigeo": "120101",
            },
            timeout=30,
        )
        assert registration.status_code == 201, registration.text

        login = session.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        categories_response = session.get(
            f"{BASE_URL}/api/catalogos/categorias",
            timeout=30,
        )
        assert categories_response.status_code == 200, categories_response.text
        categories = categories_response.json()
        assert isinstance(categories, list) and categories, categories
        category_id = categories[0]["id_categoria"]

        device_response = session.post(
            f"{BASE_URL}/api/raee",
            json={
                "id_categoria": category_id,
                "marca": brand,
                "modelo": model,
            },
            headers=auth_headers,
            timeout=30,
        )
        assert device_response.status_code == 201, device_response.text
        tracking_code = device_response.json()["codigo_seguimiento"]
        assert isinstance(tracking_code, str) and tracking_code

        tracking_url = (
            f"{BASE_URL}/api/publico/rastreo/{quote(tracking_code, safe='')}"
        )
        lookup = session.get(tracking_url, timeout=30)
        assert lookup.status_code == 200, lookup.text
        public_data = lookup.json()

        assert isinstance(public_data, dict), public_data
        assert isinstance(public_data.get("ficha"), dict), public_data
        assert isinstance(public_data.get("historial"), list), public_data

        def collect_values(value):
            if isinstance(value, dict):
                return [
                    item
                    for nested in value.values()
                    for item in collect_values(nested)
                ]
            if isinstance(value, list):
                return [item for nested in value for item in collect_values(nested)]
            return [value]

        ficha_values = collect_values(public_data["ficha"])
        assert brand in ficha_values, public_data
        assert model in ficha_values, public_data
        assert any(
            isinstance(value, str) and value.lower() == tracking_code.lower()
            for value in ficha_values
        ), public_data

        sensitive_keys = {
            "nombres",
            "apellidos",
            "nombre_completo",
            "correo",
            "email",
            "telefono",
            "direccion",
            "id_usuario",
        }

        def assert_no_personal_data(value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    assert key.lower() not in sensitive_keys, public_data
                    assert_no_personal_data(nested)
            elif isinstance(value, list):
                for nested in value:
                    assert_no_personal_data(nested)

        assert_no_personal_data(public_data)
        serialized_data = str(public_data).lower()
        assert email.lower() not in serialized_data
        assert nombres.lower() not in serialized_data
        assert apellidos.lower() not in serialized_data

        alternate_case_code = tracking_code.swapcase()
        alternate_case_response = session.get(
            f"{BASE_URL}/api/publico/rastreo/"
            f"{quote(alternate_case_code, safe='')}",
            timeout=30,
        )
        assert alternate_case_response.status_code == 200, alternate_case_response.text
        assert alternate_case_response.json() == public_data

        unknown_code = f"TS-UNKNOWN-{timestamp}"
        unknown_response = session.get(
            f"{BASE_URL}/api/publico/rastreo/{quote(unknown_code, safe='')}",
            timeout=30,
        )
        assert unknown_response.status_code == 404, unknown_response.text
    finally:
        session.close()


if __name__ == "__main__":
    test_public_tracking_lookup_privacy()