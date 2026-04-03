from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import NotFoundError
from app.modules.admin.application.service import AdminService
from app.shared.enums import OrderStatus


@pytest.mark.unit
def test_delete_user_raises_when_user_missing(mock_db_session):
    service = AdminService(db=mock_db_session)
    service.user_repo = MagicMock()
    service.user_repo.get_user_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.delete_user(user_id=10)


@pytest.mark.unit
def test_get_all_orders_raises_when_empty(mock_db_session):
    service = AdminService(db=mock_db_session)
    service.order_repo = MagicMock()
    service.order_repo.get_all_orders.return_value = []

    with pytest.raises(NotFoundError):
        service.get_all_orders()


@pytest.mark.unit
def test_ship_order_sets_status_to_shipped(mock_db_session):
    service = AdminService(db=mock_db_session)
    service.order_repo = MagicMock()
    order = SimpleNamespace(id=5, user_id=3, status=OrderStatus.pending)
    service.order_repo.get_order_by_id.return_value = order
    service.order_repo.save_order.return_value = order

    result = service.ship_order(order_id=5)

    assert result.status == OrderStatus.shipped
    service.order_repo.save_order.assert_called_once()
