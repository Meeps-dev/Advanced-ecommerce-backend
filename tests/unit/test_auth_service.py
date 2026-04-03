from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

from app.modules.auth.application.service import AuthService
from app.core.exceptions import ConflictError, UnauthorizedError


def test_register_user_raises_conflict_on_duplicate_email():
    service = AuthService(db=MagicMock())
    service.user_repo = MagicMock()
    service.user_repo.get_user_by_email.return_value = SimpleNamespace(id=1, email="x@example.com")

    with pytest.raises(ConflictError):
        service.register_user("x@example.com", "Pass123!", "Existing User")


def test_login_user_raises_unauthorized_on_bad_password():
    service = AuthService(db=MagicMock())
    service.user_repo = MagicMock()
    service.user_repo.get_user_by_email.return_value = SimpleNamespace(id=1, password_hash="fakehash")

    with patch("app.modules.auth.application.service.verify_password", return_value=False):
        with pytest.raises(UnauthorizedError):
            service.login_user("x@example.com", "wrong-password")
