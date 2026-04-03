import pytest


@pytest.mark.e2e
def test_customer_cannot_access_admin_users(api_url, auth_session):
    res = auth_session.get(f"{api_url}/admin/users", timeout=20)

    assert res.status_code in (401, 403), res.text
