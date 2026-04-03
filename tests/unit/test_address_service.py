from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import NotFoundError
from app.modules.addresses.api.schemas import AddressCreate
from app.modules.addresses.application.service import AddressService


def _payload():
    return AddressCreate(
        full_name="John Doe",
        address_line1="12 Main St",
        city="Lagos",
        state="LA",
        postal_code="100001",
        country="NG",
    )


@pytest.mark.unit
def test_list_user_addresses_raises_when_empty(mock_db_session):
    service = AddressService(db=mock_db_session)
    service.address_repo = MagicMock()
    service.address_repo.get_by_user.return_value = []

    with pytest.raises(NotFoundError):
        service.list_user_addresses(user_id=1)


@pytest.mark.unit
def test_get_user_address_raises_when_missing(mock_db_session):
    service = AddressService(db=mock_db_session)
    service.address_repo = MagicMock()
    service.address_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_user_address(address_id=2)


@pytest.mark.unit
def test_create_user_address_returns_pydantic_response(mock_db_session):
    service = AddressService(db=mock_db_session)
    service.address_repo = MagicMock()
    service.address_repo.create.return_value = SimpleNamespace(
        id=4,
        full_name="John Doe",
        address_line1="12 Main St",
        city="Lagos",
        state="LA",
        postal_code="100001",
        country="NG",
    )

    result = service.create_user_address(user_id=1, payload=_payload())

    assert result.id == 4
    assert result.city == "Lagos"
