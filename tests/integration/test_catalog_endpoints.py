import pytest


@pytest.mark.integration
def test_list_products_endpoint_returns_ok(client):
    res = client.get("/api/v1/products/")

    assert res.status_code == 200, res.text
    assert isinstance(res.json(), list)


@pytest.mark.integration
def test_list_categories_endpoint_returns_ok(client):
    res = client.get("/api/v1/categories/")

    assert res.status_code == 200, res.text
    assert isinstance(res.json(), list)
