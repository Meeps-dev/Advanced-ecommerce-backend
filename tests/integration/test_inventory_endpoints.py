import pytest


@pytest.mark.integration
def test_get_inventory_for_first_product(client):
    products = client.get("/api/v1/products/")
    assert products.status_code == 200, products.text
    payload = products.json()
    if not payload:
        pytest.skip("No products available")

    product_id = payload[0]["id"]
    inv = client.get(f"/api/v1/inventory/{product_id}")

    assert inv.status_code in (200, 404), inv.text
