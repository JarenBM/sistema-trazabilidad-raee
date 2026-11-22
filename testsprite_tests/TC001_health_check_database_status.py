import requests

BASE_URL = "http://localhost:8000"


def test_health_check_database_status():
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
    except requests.RequestException as exc:
        raise AssertionError(f"Health endpoint request failed: {exc}") from exc

    body_text = response.text.lower()
    database_error_indicators = (
        "database",
        "base_datos",
        "postgres",
        "connection",
        "conexión",
        "error",
        "unavailable",
        "unhealthy",
        "degrad",
        "desconect",
        "no disponible",
    )

    if response.status_code == 200:
        try:
            payload = response.json()
        except ValueError as exc:
            raise AssertionError("Health endpoint returned invalid JSON") from exc

        assert isinstance(payload, dict), "Health response must be a JSON object"
        assert "ok" in payload, "Health response is missing the API status"
        assert isinstance(payload["ok"], bool), "API status 'ok' must be a boolean"
        assert "base_datos" in payload, "Health response is missing the database status"
        assert isinstance(payload["base_datos"], str), "Database status must be a string"
        assert payload["base_datos"].strip(), "Database status must not be empty"

        if payload["ok"]:
            assert not any(
                indicator in payload["base_datos"].lower()
                for indicator in ("error", "unavailable", "degrad", "desconect", "no disponible")
            ), "Healthy API response indicates a degraded database"
        else:
            assert any(
                indicator in payload["base_datos"].lower()
                for indicator in database_error_indicators
            ), "Unhealthy response does not indicate a database connectivity issue"
    else:
        assert response.status_code >= 500, (
            f"Expected HTTP 200 when healthy or a server error when unhealthy; "
            f"received HTTP {response.status_code}"
        )
        assert any(indicator in body_text for indicator in database_error_indicators), (
            "Error response does not indicate a database connectivity issue"
        )


if __name__ == "__main__":
    test_health_check_database_status()