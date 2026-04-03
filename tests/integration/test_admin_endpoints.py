import pytest


@pytest.mark.integration
def test_admin_users_forbidden_for_customer(client, auth_headers):
    res = client.get("/api/v1/admin/users", headers=auth_headers)

    assert res.status_code in (401, 403), res.text


@pytest.mark.integration
def test_admin_orders_forbidden_for_customer(client, auth_headers):
    res = client.get("/api/v1/admin/orders", headers=auth_headers)

    assert res.status_code in (401, 403), res.text
