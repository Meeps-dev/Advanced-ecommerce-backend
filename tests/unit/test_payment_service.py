from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import NotFoundError
from app.modules.payments.application.service import PaymentService


@pytest.mark.unit
def test_verify_payment_by_reference_raises_when_missing():
    payment_repo = MagicMock()
    payment_repo.get_by_reference.return_value = None
    service = PaymentService(payment_repo=payment_repo, order_repo=MagicMock(), address_repo=MagicMock())

    with pytest.raises(NotFoundError):
        service.verify_payment_by_reference("missing-ref")


@pytest.mark.unit
def test_handle_webhook_returns_false_for_invalid_signature():
    service = PaymentService(payment_repo=MagicMock(), order_repo=MagicMock(), address_repo=MagicMock())

    result = service.handle_webhook(b"{}", "bad-signature")

    assert result is False


@pytest.mark.unit
def test_update_payment_status_returns_none_for_invalid_status():
    payment_repo = MagicMock()
    payment_repo.get_by_id.return_value = SimpleNamespace(status="pending")
    service = PaymentService(payment_repo=payment_repo, order_repo=MagicMock(), address_repo=MagicMock())

    result = service.update_payment_status(payment_id=1, status="invalid-status")

    assert result is None


@pytest.mark.unit
def test_verify_payment_by_reference_success_path_updates_status():
    payment = SimpleNamespace(id=10, order=SimpleNamespace(user_id=5))
    payment_repo = MagicMock()
    payment_repo.get_by_reference.return_value = payment

    service = PaymentService(payment_repo=payment_repo, order_repo=MagicMock(), address_repo=MagicMock())

    with patch("app.modules.payments.application.service.paystack_client.verify_transaction", return_value={"status": "success"}):
        with patch.object(service, "update_payment_status", return_value=payment) as update_status:
            result = service.verify_payment_by_reference("ok-ref")

    assert result == payment
    update_status.assert_called_once()
