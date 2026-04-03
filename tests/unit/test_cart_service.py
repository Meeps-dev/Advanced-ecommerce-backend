from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.cart.application.service import CartService


def _build_service():
    cart_repo = MagicMock()
    product_repo = MagicMock()
    inventory_repo = MagicMock()
    db = MagicMock()
    cache = MagicMock()
    return (
        CartService(
            cart_repo=cart_repo,
            product_repo=product_repo,
            inventory_repo=inventory_repo,
            db=db,
            cache=cache,
        ),
        cart_repo,
        product_repo,
        inventory_repo,
        db,
        cache,
    )


@pytest.mark.unit
def test_add_to_cart_rejects_non_positive_quantity():
    service, *_ = _build_service()

    with pytest.raises(BadRequestError):
        service.add_to_cart(user_id=1, product_id=1, quantity=0)


@pytest.mark.unit
def test_add_to_cart_raises_when_product_missing():
    service, cart_repo, product_repo, *_ = _build_service()
    cart_repo.get_cart_by_user.return_value = SimpleNamespace(id=1, user_id=1, items=[])
    product_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.add_to_cart(user_id=1, product_id=999, quantity=1)


@pytest.mark.unit
def test_get_item_count_returns_cached_value():
    service, *_rest, cache = _build_service()
    cache.get_json.return_value = {"total_items": 7}

    result = service.get_item_count(user_id=1)

    assert result == {"total_items": 7}


@pytest.mark.unit
def test_clear_cart_raises_for_missing_cart():
    service, cart_repo, *_ = _build_service()
    cart_repo.get_cart_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.clear_cart(cart_id=500)
