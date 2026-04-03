from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ConflictError
from app.modules.catalog.api.category_schemas import CategoryCreate
from app.modules.catalog.application.category_service import CategoryService


@pytest.mark.unit
def test_create_category_raises_on_duplicate_name():
    repo = MagicMock()
    repo.get_by_name.return_value = SimpleNamespace(id=1, name="Electronics")
    service = CategoryService(repo=repo)

    with pytest.raises(ConflictError):
        service.create_category(CategoryCreate(name="Electronics", description="x"))


@pytest.mark.unit
def test_list_categories_returns_repo_results():
    repo = MagicMock()
    repo.get_all.return_value = [SimpleNamespace(id=1, name="Electronics", description="x")]
    service = CategoryService(repo=repo)

    result = service.list_categories()

    assert len(result) == 1
    assert result[0].name == "Electronics"
