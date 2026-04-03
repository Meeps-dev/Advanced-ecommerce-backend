import pytest


@pytest.mark.e2e
def test_add_to_cart_and_view_summary(api_url, auth_session):
    products = auth_session.get(f"{api_url}/products/", timeout=20)
    assert products.status_code == 200, products.text
    data = products.json()
    if not data:
        pytest.skip("No products available")

    product_id = data[0]["id"]
    add = auth_session.post(
        f"{api_url}/cart/items",
        json={"product_id": product_id, "quantity": 1},
        timeout=20,
    )
    assert add.status_code == 200, add.text

    summary = auth_session.get(f"{api_url}/cart/", timeout=20)
    assert summary.status_code == 200, summary.text
    assert "items" in summary.json()
