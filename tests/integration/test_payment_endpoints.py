import pytest


@pytest.mark.integration
def test_webhook_rejects_invalid_signature(client):
    res = client.post(
        "/api/v1/payments/webhook",
        headers={"x-paystack-signature": "invalid"},
        content=b"{}",
    )

    assert res.status_code == 401, res.text


@pytest.mark.integration
def test_verify_payment_requires_auth(client):
    res = client.post("/api/v1/payments/verify", json={"reference": "abc"})

    assert res.status_code in (401, 403), res.text
