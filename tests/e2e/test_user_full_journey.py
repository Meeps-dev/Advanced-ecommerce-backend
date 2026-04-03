import pytest


@pytest.mark.e2e
def test_register_login_and_list_products(api_url, auth_session):
    products = auth_session.get(f"{api_url}/products/", timeout=20)

    assert products.status_code == 200, products.text
    assert isinstance(products.json(), list)
