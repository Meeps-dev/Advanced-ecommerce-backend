import logging

from app.modules.events import OrderCheckoutInitiated, PaymentSucceeded, OrderShipped
from app.modules.events import event_bus
from app.db.session import SessionLocal
from app.modules.addresses.infrastructure.repository import AddressRepository
from app.modules.orders.infrastructure.repository import OrderRepository
from app.modules.payments.application.service import PaymentService
from app.modules.payments.infrastructure.repository import PaymentRepository
from app.shared.enums import OrderStatus


logger = logging.getLogger(__name__)


def on_order_checkout_initiated_payment(event: OrderCheckoutInitiated) -> dict:
    db = SessionLocal()
    try:
        payment_repo = PaymentRepository(db)
        order_repo = OrderRepository(db)
        address_repo = AddressRepository(db)

        service = PaymentService(
            payment_repo=payment_repo,
            order_repo=order_repo,
            address_repo=address_repo,
        )
        return service.initiate_payment(order_id=event.order_id, user_email=event.user_email)
    finally:
        db.close()


def on_payment_succeeded_auto_ship(event: PaymentSucceeded) -> None:
    db = SessionLocal()
    try:
        order_repo = OrderRepository(db)
        address_repo = AddressRepository(db)

        order = order_repo.get_order_by_id(event.order_id)
        if not order or order.status != OrderStatus.paid:
            return

        addresses = address_repo.get_by_user(order.user_id)
        if not addresses:
            logger.info(
                "order_not_auto_shipped_missing_address",
                extra={
                    "event": "order_not_auto_shipped_missing_address",
                    "entity": "order",
                    "entity_id": event.order_id,
                    "user_id": event.user_id,
                },
            )
            return

        shipped_order = order_repo.update_order_status(order, OrderStatus.shipped)
        event_bus.publish(
            OrderShipped(
                order_id=shipped_order.id,
                user_id=shipped_order.user_id,
                user_email=shipped_order.user.email,
            )
        )
    finally:
        db.close()
