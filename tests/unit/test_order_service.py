from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.orders.application.service import OrderService


def _build_service():
    cart_repo = MagicMock()
    order_repo = MagicMock()
    payment_service = MagicMock()
    db = MagicMock()
    cache = MagicMock()
    return (
        OrderService(
            cart_repo=cart_repo,
            order_repo=order_repo,
            payment_service=payment_service,
            db=db,
            cache=cache,
        ),
        cart_repo,
        order_repo,
        payment_service,
        db,
        cache,
    )


@pytest.mark.unit
def test_checkout_raises_when_cart_is_empty():
    service, cart_repo, *_ = _build_service()
    cart_repo.get_cart_by_user.return_value = SimpleNamespace(id=1, user_id=1, items=[])

    with pytest.raises(BadRequestError):
        service.checkout(user_id=1)


@pytest.mark.unit
def test_get_all_orders_returns_cached_payload():
    service, *_rest, cache = _build_service()
    cache.get_json.return_value = [{"id": 2, "status": "pending", "items": []}]

    result = service.get_all_orders()

    assert result == [{"id": 2, "status": "pending", "items": []}]


@pytest.mark.unit
def test_get_order_by_id_raises_when_missing():
    service, _, order_repo, *_ = _build_service()
    service.cache.get_json.return_value = None
    order_repo.get_order_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_order_by_id(order_id=404)


@pytest.mark.unit
def test_update_order_status_raises_when_missing():
    service, _, order_repo, *_ = _build_service()
    order_repo.get_order_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.update_order_status(order_id=999, status="paid")
