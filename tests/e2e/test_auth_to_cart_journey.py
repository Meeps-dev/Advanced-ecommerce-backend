import os
import uuid
import pytest
import requests


BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost")
API = f"{BASE_URL}/api/v1"


def test_auth_to_cart_journey():
    email = f"e2e_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    r1 = requests.post(
        f"{API}/auth/register",
        json={"email": email, "password": password, "full_name": "E2E User"},
        timeout=20,
    )
    assert r1.status_code in (200, 201), r1.text

    r2 = requests.post(
        f"{API}/auth/login",
        data={"username": email, "password": password},
        timeout=20,
    )
    assert r2.status_code == 200, r2.text
    token = r2.json()["access_token"]

    r3 = requests.get(f"{API}/products/", timeout=20)
    assert r3.status_code == 200, r3.text
    products = r3.json()
    if not products:
        pytest.skip("No products available. Run [seed_database.py](http://_vscodecontentref_/6) before e2e.")

    first_product_id = products[0]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    r4 = requests.post(
        f"{API}/cart/items",
        json={"product_id": first_product_id, "quantity": 1},
        headers=headers,
        timeout=20,
    )
    assert r4.status_code == 200, r4.text
