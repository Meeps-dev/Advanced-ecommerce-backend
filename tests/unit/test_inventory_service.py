from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import NotFoundError
from app.modules.inventory.application.service import InventoryService


@pytest.mark.unit
def test_set_inventory_raises_for_missing_product():
    inventory_repo = MagicMock()
    product_repo = MagicMock()
    product_repo.get_by_id.return_value = None

    service = InventoryService(inventory_repo=inventory_repo, product_repo=product_repo)

    with pytest.raises(NotFoundError):
        service.set_inventory(product_id=999, quantity=10)


@pytest.mark.unit
def test_get_inventory_returns_none_when_absent():
    inventory_repo = MagicMock()
    product_repo = MagicMock()
    inventory_repo.get_by_product_id.return_value = None

    service = InventoryService(inventory_repo=inventory_repo, product_repo=product_repo)

    assert service.get_inventory(product_id=1) is None


@pytest.mark.unit
def test_set_inventory_creates_new_inventory_record():
    inventory_repo = MagicMock()
    inventory_repo.db = MagicMock()
    product_repo = MagicMock()
    product_repo.get_by_id.return_value = SimpleNamespace(id=1)
    inventory_repo.get_by_product_id.return_value = None
    inventory_repo.create.return_value = SimpleNamespace(id=4, product_id=1, quantity=12)

    service = InventoryService(inventory_repo=inventory_repo, product_repo=product_repo)
    result = service.set_inventory(product_id=1, quantity=12)

    assert result.id == 4
    inventory_repo.db.commit.assert_called_once()
