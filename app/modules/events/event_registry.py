from app.modules.events import OrderCheckoutInitiated, OrderShipped, PaymentSucceeded, event_bus
from app.modules.analytics.application.event_listeners import (
        on_order_checkout_initiated_analytics,
        on_order_shipped_analytics,
        on_payment_succeeded_analytics,
    )
from app.modules.email.application.listeners import (
        on_order_shipped_email,
        on_payment_succeeded_email,
    )
from app.modules.payments.application.listeners import (
        on_order_checkout_initiated_payment,
        on_payment_succeeded_auto_ship,
    )

def register_domain_event_listeners() -> None:

    event_bus.clear()

    event_bus.subscribe(OrderCheckoutInitiated, on_order_checkout_initiated_payment)
    event_bus.subscribe(PaymentSucceeded, on_payment_succeeded_auto_ship)

    event_bus.subscribe(PaymentSucceeded, on_payment_succeeded_email)
    event_bus.subscribe(OrderShipped, on_order_shipped_email)

    event_bus.subscribe(OrderCheckoutInitiated, on_order_checkout_initiated_analytics)
    event_bus.subscribe(PaymentSucceeded, on_payment_succeeded_analytics)
    event_bus.subscribe(OrderShipped, on_order_shipped_analytics)
