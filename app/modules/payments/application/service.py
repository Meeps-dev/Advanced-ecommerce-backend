from datetime import datetime
import logging
import json
from json import JSONDecodeError
from typing import Optional

from app.core.config import settings
from app.modules.events import PaymentSucceeded, event_bus
from app.shared.enums import PaymentStatus, OrderStatus
from app.core.exceptions import NotFoundError
from app.integrations.paystack.client import paystack_client
from app.modules.addresses.infrastructure.repository import AddressRepository
from app.modules.orders.infrastructure.repository import OrderRepository
from app.modules.payments.infrastructure.repository import PaymentRepository


logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(
        self,
        payment_repo: PaymentRepository | None = None,
        order_repo: OrderRepository | None = None,
        address_repo: AddressRepository | None = None,
    ):
        self.payment_repo = payment_repo 
        self.order_repo = order_repo
        self.address_repo = address_repo


    def initiate_payment(self, order_id: int, user_email: str) -> dict:
        """Create a pending payment and initialize provider checkout."""
        order = self.order_repo.get_order_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")

        # 1. Create Internal Payment Record (Status: pending)
        payment = self.payment_repo.create(
            order_id=order.id,
            amount=order.total_price,
            provider="paystack"
        )

        # 2. Call Paystack API
        payload = {
            "email": user_email,
            "amount": int(order.total_price * 100),  # Kobo conversion
            "reference": f"PAY-{payment.id}-{int(datetime.now().timestamp())}",
            "callback_url": settings.paystack_callback_url,
            "metadata": {"payment_id": payment.id, "order_id": order_id},
        }

        data = paystack_client.initialize_transaction(payload)
        
        # Update payment with the reference from Paystack
        self.payment_repo.update_reference(payment, data["reference"])

        logger.info(
            "payment_initiated",
            extra={
                "event": "payment_initiated",
                "entity": "payment",
                "entity_id": payment.id,
                "user_id": order.user_id,
            },
        )

        return {
            "payment_id": payment.id,
            "reference": data["reference"],
            "checkout_url": data["authorization_url"],
            "status": payment.status,
            "amount": payment.amount,
        }


    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Validate webhook authenticity using provider signing rules."""
        return paystack_client.verify_webhook_signature(payload, signature)

    def handle_webhook(self, raw_payload: bytes, signature: str):
        """
        Unified handler: Verifies signature, parses JSON, and updates status.
        """
        # 1. SECURITY FIRST: Verify the source
        if not self.verify_webhook_signature(raw_payload, signature):
            print("SECURITY ALERT: Invalid Paystack webhook signature")
            return False

        # 2. Parse the verified data
        try:
            payload = json.loads(raw_payload)
        except JSONDecodeError:
            return False
        
        # 3. Process the event
        if payload.get('event') == 'charge.success':
            data = payload.get('data', {})
            reference = data.get('reference')
            
            # Use your repo to find the internal payment record
            payment = self.payment_repo.get_by_reference(reference)
            
            if payment:
                # Status update is idempotent, so repeated provider retries are safe.
                self.update_payment_status(payment.id, "successful")
                logger.info(
                    "payment_webhook_processed",
                    extra={
                        "event": "payment_webhook_processed",
                        "entity": "payment",
                        "entity_id": payment.id,
                        "user_id": payment.order.user_id if payment.order else "-",
                    },
                )
                print(f"Payment verified: ref {reference}")
                return True
                
        return False
   

    def verify_payment_by_reference(self, reference: str):
        payment = self.payment_repo.get_by_reference(reference)
        if not payment:
            raise NotFoundError("Payment not found")

        verification_data = paystack_client.verify_transaction(reference)
        provider_status = (verification_data.get("status") or "").lower()
        logger.info(
            "payment_verification_requested",
            extra={
                "event": "payment_verification_requested",
                "entity": "payment",
                "entity_id": payment.id,
                "user_id": payment.order.user_id if payment.order else "-",
            },
        )

        if provider_status == "success":
            return self.update_payment_status(payment.id, PaymentStatus.successful.value)

        if provider_status in {"failed", "reversed"}:
            return self.update_payment_status(payment.id, PaymentStatus.failed.value)

        return payment



    def update_payment_status(self, payment_id: int, status: str):
        """Normalize provider status and apply downstream order side effects."""
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            return None

        normalized_status: Optional[PaymentStatus] = None
        if isinstance(status, PaymentStatus):
            normalized_status = status
        else:
            status_aliases = {
                "success": PaymentStatus.successful,
            }
            mapped_status = status_aliases.get(str(status).lower(), status)
            try:
                normalized_status = PaymentStatus(mapped_status)
            except ValueError:
                return None

        if payment.status == normalized_status:
            # Idempotency guard for duplicate webhook or verify calls.
            return payment

        self.payment_repo.update_status(payment, normalized_status)
        logger.info(
            "payment_status_updated",
            extra={
                "event": "payment_status_updated",
                "entity": "payment",
                "entity_id": payment.id,
                "user_id": payment.order.user_id if payment.order else "-",
            },
        )

        if normalized_status == PaymentStatus.successful:
            # Successful payment transitions order to paid and triggers notifications.
            paid_order = self.order_repo.update_order_status(payment.order, OrderStatus.paid)

            total_amount = float(paid_order.total_price or 0.0)
            event_bus.publish(
                PaymentSucceeded(
                    payment_id=payment.id,
                    order_id=paid_order.id,
                    user_id=paid_order.user_id,
                    user_email=paid_order.user.email,
                    total_amount=total_amount,
                )
            )

        return payment
