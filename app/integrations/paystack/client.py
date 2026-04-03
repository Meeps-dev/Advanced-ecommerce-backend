from __future__ import annotations

import hashlib
import hmac
from typing import Any

import requests

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, PaymentGatewayError


class PaystackClient:
    def __init__(self, secret_key: str, initialize_url: str):
        self.secret_key = self._sanitize_secret_key(secret_key)
        self.initialize_url = initialize_url

    @staticmethod
    def _sanitize_secret_key(secret_key: str) -> str:
        cleaned = (secret_key or "").strip()
        if cleaned.lower().startswith("bearer "):
            cleaned = cleaned.split(" ", 1)[1].strip()
        return cleaned

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def initialize_transaction(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.secret_key:
            raise ExternalServiceError(
                "Paystack secret key is not configured",
                code="PAYMENT_CONFIGURATION_ERROR",
            )

        response = requests.post(
            self.initialize_url,
            json=payload,
            headers=self._headers,
            timeout=20,
        )
        if response.status_code != 200:
            raise PaymentGatewayError(f"Paystack failed: {response.text}")

        response_data = response.json()
        data = response_data.get("data")
        if not isinstance(data, dict):
            raise PaymentGatewayError("Paystack response did not contain transaction data")

        return data

    def verify_transaction(self, reference: str) -> dict[str, Any]:
        if not self.secret_key:
            raise ExternalServiceError(
                "Paystack secret key is not configured",
                code="PAYMENT_CONFIGURATION_ERROR",
            )

        verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
        response = requests.get(
            verify_url,
            headers=self._headers,
            timeout=20,
        )

        if response.status_code != 200:
            raise PaymentGatewayError(f"Paystack verification failed: {response.text}")

        response_data = response.json()
        data = response_data.get("data")
        if not isinstance(data, dict):
            raise PaymentGatewayError("Paystack verify response did not contain transaction data")

        return data

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        if not signature or not self.secret_key:
            return False

        digest = hmac.new(
            self.secret_key.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(digest, signature)


paystack_client = PaystackClient(
    secret_key=settings.paystack_secret_key,
    initialize_url=settings.paystack_initialize_url,
)
