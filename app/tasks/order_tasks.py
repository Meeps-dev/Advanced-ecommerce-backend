from datetime import datetime, timedelta, timezone
import logging
from celery import shared_task
from sqlalchemy import select
from app.db.session import SessionLocal
from app.modules.catalog.infrastructure.models.product import Product
from app.modules.catalog.infrastructure.models.product_image import ProductImage
from app.modules.orders.infrastructure.models.order_item import OrderItem
from app.modules.catalog.infrastructure.models.category import Category
from app.modules.reviews.infrastructure.models.review import Review
from app.modules.users.infrastructure.models.user import User
from app.modules.addresses.infrastructure.models.shipping_address import ShippingAddress
from app.modules.payments.infrastructure.models.payment import Payment
from app.modules.cart.infrastructure.models.cart import Cart
from app.modules.cart.infrastructure.models.cart_item import CartItem

from app.modules.inventory.infrastructure.models.inventory import Inventory
from app.modules.orders.infrastructure.models.order import Order
from app.shared.enums import OrderStatus

logger = logging.getLogger(__name__)


@shared_task(
    name="cleanup_expired_orders",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def cleanup_expired_orders(self):
    """
    Finds pending orders older than 24 hours and cancels them,
    returning items to inventory.
    """
    db = SessionLocal()
    try:
        expiration_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        
        query = select(Order).where(
            Order.status == OrderStatus.pending,
            Order.created_at < expiration_threshold
        )
        expired_orders = db.execute(query).scalars().all()

        for order in expired_orders:
            for item in order.items:
                inventory = db.execute(
                    select(Inventory).where(Inventory.product_id == item.product_id)
                ).scalar_one()
                inventory.quantity += item.quantity
            
            order.status = OrderStatus.cancelled
            logger.info("cleanup_expired_orders_cancelled", extra={"order_id": order.id})

        db.commit()
        return f"Cleaned up {len(expired_orders)} orders."
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
