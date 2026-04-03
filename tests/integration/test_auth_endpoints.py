import uuid


def test_register_then_login(client):
    email = f"it_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    register_payload = {
        "email": email,
        "password": password,
        "full_name": "Integration User",
    }

    r1 = client.post("/api/v1/auth/register", json=register_payload)
    assert r1.status_code in (200, 201), r1.text

    r2 = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_fails_with_wrong_password(client):
    email = f"it_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Integration User"},
    )

    bad = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "WrongPass123!"},
    )
    assert bad.status_code in (400, 401), bad.text
