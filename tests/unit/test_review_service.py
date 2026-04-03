from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.reviews.application.service import ReviewService


@pytest.mark.unit
def test_add_review_requires_purchase(mock_db_session):
    service = ReviewService(db=mock_db_session)
    service.product_repo = MagicMock()
    service.review_repo = MagicMock()
    service.product_repo.get_by_id.return_value = SimpleNamespace(id=1)

    query_chain = MagicMock()
    mock_db_session.query.return_value = query_chain
    query_chain.join.return_value = query_chain
    query_chain.filter.return_value = query_chain
    query_chain.first.return_value = None

    with pytest.raises(ForbiddenError):
        service.add_review(user_id=1, product_id=1, rating=5, comment="Great")


@pytest.mark.unit
def test_get_review_raises_when_missing(mock_db_session):
    service = ReviewService(db=mock_db_session)
    service.review_repo = MagicMock()
    service.review_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_review(review_id=999)


@pytest.mark.unit
def test_delete_review_raises_when_missing(mock_db_session):
    service = ReviewService(db=mock_db_session)
    service.review_repo = MagicMock()
    service.review_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.delete_review(review_id=888)
