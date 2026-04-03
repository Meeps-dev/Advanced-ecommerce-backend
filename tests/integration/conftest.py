import uuid

import pytest


@pytest.fixture
def register_and_login(client):
    def _do_register_and_login(prefix: str = "it"):
        email = f"{prefix}_{uuid.uuid4().hex}@example.com"
        password = "StrongPass123!"

        reg = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "Integration User"},
        )
        assert reg.status_code in (200, 201), reg.text

        login = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        assert login.status_code == 200, login.text

        body = login.json()
        return {
            "email": email,
            "password": password,
            "access_token": body["access_token"],
            "refresh_token": body["refresh_token"],
        }

    return _do_register_and_login


@pytest.fixture
def auth_headers(register_and_login):
    session = register_and_login()
    return {"Authorization": f"Bearer {session['access_token']}"}
