import requests


BASE_URL = "http://localhost:8000"


def test_public_center_catalog_filtering():
    try:
        active_response = requests.get(
            f"{BASE_URL}/api/catalogos/centros",
            params={"solo_activos": "true"},
            timeout=30,
        )
        assert active_response.status_code == 200, (
            f"Expected 200 for active centers, got {active_response.status_code}: "
            f"{active_response.text}"
        )
        active_centers = active_response.json()
        assert isinstance(active_centers, list), "Expected the active centers response to be a list"

        for center in active_centers:
            assert isinstance(center, dict), "Expected each center to be an object"
            assert center.get("activo") is True, f"Inactive center found in active results: {center}"

        all_response = requests.get(
            f"{BASE_URL}/api/catalogos/centros",
            params={"solo_activos": "false"},
            timeout=30,
        )
        assert all_response.status_code == 200, (
            f"Expected 200 for all centers, got {all_response.status_code}: {all_response.text}"
        )
        all_centers = all_response.json()
        assert isinstance(all_centers, list), "Expected the all-centers response to be a list"

        for center in all_centers:
            assert isinstance(center, dict), "Expected each center to be an object"
            assert isinstance(center.get("activo"), bool), (
                f"Expected each center to include a boolean activo field: {center}"
            )

        active_ids = {
            center["id_centro"] for center in active_centers if "id_centro" in center
        }
        all_ids = {center["id_centro"] for center in all_centers if "id_centro" in center}
        if active_ids and all_ids:
            assert active_ids.issubset(all_ids), (
                "The all-centers response should include every center returned by the "
                "active-only response"
            )

        inactive_centers = [center for center in all_centers if center["activo"] is False]
        if inactive_centers:
            inactive_ids = {
                center["id_centro"] for center in inactive_centers if "id_centro" in center
            }
            active_response_ids = {
                center["id_centro"]
                for center in active_centers
                if "id_centro" in center
            }
            assert inactive_ids.isdisjoint(active_response_ids), (
                "Inactive centers must not appear in the active-only response"
            )

        malformed_response = requests.get(
            f"{BASE_URL}/api/catalogos/centros",
            params={"solo_activos": "TS_malformed_boolean"},
            timeout=30,
        )
        assert malformed_response.status_code == 422, (
            f"Expected 422 for malformed solo_activos value, got "
            f"{malformed_response.status_code}: {malformed_response.text}"
        )
    except requests.RequestException as exc:
        raise AssertionError(f"HTTP request to the catalog API failed: {exc}") from exc


if __name__ == "__main__":
    test_public_center_catalog_filtering()