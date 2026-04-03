import pytest


@pytest.mark.integration
def test_get_reviews_for_product_returns_list(client):
    products = client.get("/api/v1/products/")
    assert products.status_code == 200, products.text
    payload = products.json()
    if not payload:
        pytest.skip("No products found")

    product_id = payload[0]["id"]
    reviews = client.get(f"/api/v1/reviews/{product_id}")

    assert reviews.status_code == 200, reviews.text
    assert isinstance(reviews.json(), list)
