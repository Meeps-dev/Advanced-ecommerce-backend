import pytest


@pytest.mark.integration
def test_get_single_order_not_found(client, auth_headers):
    res = client.get("/api/v1/orders/999999", headers=auth_headers)

    assert res.status_code in (404, 422), res.text


@pytest.mark.integration
def test_admin_orders_endpoint_forbidden_for_customer(client, auth_headers):
    res = client.get("/api/v1/orders/", headers=auth_headers)

    assert res.status_code in (401, 403), res.text
