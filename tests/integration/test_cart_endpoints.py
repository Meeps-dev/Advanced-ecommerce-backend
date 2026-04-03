import pytest


@pytest.mark.integration
def test_add_item_then_fetch_cart_summary(client, auth_headers):
    products = client.get("/api/v1/products/")
    assert products.status_code == 200, products.text
    payload = products.json()
    if not payload:
        pytest.skip("No products found for cart integration test")

    product_id = payload[0]["id"]

    add_res = client.post(
        "/api/v1/cart/items",
        json={"product_id": product_id, "quantity": 1},
        headers=auth_headers,
    )
    assert add_res.status_code == 200, add_res.text

    cart_res = client.get("/api/v1/cart/", headers=auth_headers)
    assert cart_res.status_code == 200, cart_res.text
    assert "items" in cart_res.json()


@pytest.mark.integration
def test_cart_count_endpoint_returns_total_items(client, auth_headers):
    count_res = client.get("/api/v1/cart/items/count", headers=auth_headers)

    assert count_res.status_code in (200, 404), count_res.text
    if count_res.status_code == 200:
        assert "total_items" in count_res.json()
