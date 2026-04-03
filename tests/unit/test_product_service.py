from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import NotFoundError
from app.modules.catalog.api.product_image_schemas import ProductImageCreate
from app.modules.catalog.application.product_service import ProductService


def _build_service():
    product_repo = MagicMock()
    image_repo = MagicMock()
    cache = MagicMock()
    return ProductService(product_repo=product_repo, image_repo=image_repo, cache=cache), product_repo, image_repo, cache


@pytest.mark.unit
def test_list_products_returns_cached_payload():
    service, _, _, cache = _build_service()
    cache.get_json.return_value = [{"id": 1, "name": "Cached"}]

    result = service.list_products()

    assert result == [{"id": 1, "name": "Cached"}]


@pytest.mark.unit
def test_get_product_by_id_returns_none_when_missing():
    service, product_repo, _, cache = _build_service()
    cache.get_json.return_value = None
    product_repo.get_by_id.return_value = None

    result = service.get_product_by_id(999)

    assert result is None


@pytest.mark.unit
def test_add_product_image_raises_when_product_missing():
    service, product_repo, _, _ = _build_service()
    product_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.add_product_image(777, ProductImageCreate(image_url="https://example.com/image.png"))


@pytest.mark.unit
def test_add_product_image_invalidates_cache():
    service, product_repo, image_repo, cache = _build_service()
    product_repo.get_by_id.return_value = SimpleNamespace(id=4)
    image_repo.create.return_value = SimpleNamespace(id=5, product_id=4, image_url="https://example.com/img.png")

    image = service.add_product_image(4, ProductImageCreate(image_url="https://example.com/img.png"))

    assert image.id == 5
    cache.delete.assert_called_once()
