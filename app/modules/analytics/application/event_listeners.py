import logging

from redis import Redis

from app.core.config import settings
from app.modules.events import OrderCheckoutInitiated, OrderShipped, PaymentSucceeded


logger = logging.getLogger(__name__)
_ANALYTICS_KEY = "analytics:event_counts:v1"


def _increment(event_name: str) -> None:
    try:
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
        redis_client.hincrby(_ANALYTICS_KEY, event_name, 1)
    except Exception:
        logger.warning(
            "analytics_event_increment_failed",
            extra={"event": "analytics_event_increment_failed", "event_name": event_name},
            exc_info=True,
        )


def on_order_checkout_initiated_analytics(event: OrderCheckoutInitiated) -> None:
    _increment("order_checkout_initiated")


def on_payment_succeeded_analytics(event: PaymentSucceeded) -> None:
    _increment("payment_succeeded")


def on_order_shipped_analytics(event: OrderShipped) -> None:
    _increment("order_shipped")
