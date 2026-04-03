from app.modules.events import OrderShipped, PaymentSucceeded
from app.tasks.email_tasks import (
    notify_admin_new_order,
    send_order_confirmation_email,
    send_shipping_update_email,
)


def on_payment_succeeded_email(event: PaymentSucceeded) -> None:
    send_order_confirmation_email.delay(
        user_email=event.user_email,
        order_id=event.order_id,
        total_amount=event.total_amount,
    )
    notify_admin_new_order.delay(order_id=event.order_id)


def on_order_shipped_email(event: OrderShipped) -> None:
    send_shipping_update_email.delay(
        user_email=event.user_email,
        order_id=event.order_id,
        new_status=event.status,
    )
