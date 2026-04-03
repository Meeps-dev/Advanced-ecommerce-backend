from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_db_session() -> MagicMock:
    db = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.rollback = MagicMock()
    return db


@pytest.fixture
def sample_user() -> SimpleNamespace:
    return SimpleNamespace(id=101, email="unit@example.com", full_name="Unit User")


@pytest.fixture
def sample_product() -> SimpleNamespace:
    category = SimpleNamespace(id=1, name="Category", description="Desc")
    return SimpleNamespace(
        id=1,
        name="Product",
        description="Desc",
        price=25.0,
        is_active=True,
        category=category,
    )
