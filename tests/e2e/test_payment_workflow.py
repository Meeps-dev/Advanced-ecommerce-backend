import pytest
import requests


@pytest.mark.e2e
def test_payment_webhook_invalid_signature_is_rejected(api_url):
    res = requests.post(
        f"{api_url}/payments/webhook",
        headers={"x-paystack-signature": "invalid"},
        data=b"{}",
        timeout=20,
    )

    assert res.status_code == 401, res.text
