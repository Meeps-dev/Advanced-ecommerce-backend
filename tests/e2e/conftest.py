import os
import uuid

import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("E2E_BASE_URL", "http://localhost")


@pytest.fixture(scope="session")
def api_url(base_url: str) -> str:
    return f"{base_url}/api/v1"


@pytest.fixture
def e2e_account():
    return {
        "email": f"e2e_{uuid.uuid4().hex}@example.com",
        "password": "StrongPass123!",
        "full_name": "E2E User",
    }


@pytest.fixture
def auth_session(api_url: str, e2e_account: dict):
    session = requests.Session()

    reg = session.post(
        f"{api_url}/auth/register",
        json=e2e_account,
        timeout=20,
    )
    assert reg.status_code in (200, 201), reg.text

    login = session.post(
        f"{api_url}/auth/login",
        data={"username": e2e_account["email"], "password": e2e_account["password"]},
        timeout=20,
    )
    assert login.status_code == 200, login.text

    token = login.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    return session
