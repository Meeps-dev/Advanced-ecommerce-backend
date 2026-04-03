import pytest


@pytest.mark.integration
def test_create_and_list_addresses(client, auth_headers):
    create_res = client.post(
        "/api/v1/addresses/",
        headers=auth_headers,
        json={
            "full_name": "Jane Doe",
            "address_line1": "42 Test Street",
            "city": "Lagos",
            "state": "LA",
            "postal_code": "100001",
            "country": "NG",
        },
    )

    assert create_res.status_code == 200, create_res.text

    list_res = client.get("/api/v1/addresses/", headers=auth_headers)
    assert list_res.status_code == 200, list_res.text
    assert isinstance(list_res.json(), list)
