from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.catalog.infrastructure.models.product import Product
from app.modules.inventory.infrastructure.models.inventory import Inventory
from app.modules.orders.infrastructure.models.order import Order
from app.modules.payments.infrastructure.models.payment import Payment
from app.modules.users.infrastructure.models.user import User
from app.shared.enums import OrderStatus, PaymentStatus


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_overview_metrics(self) -> dict:
        """Return aggregate metrics used by the admin analytics overview."""
        # Use UTC windows so date-based metrics stay consistent across environments.
        now = datetime.now(timezone.utc)
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)

        total_users = self.db.query(func.count(User.id)).scalar() or 0
        total_orders = self.db.query(func.count(Order.id)).scalar() or 0

        paid_orders = (
            self.db.query(func.count(Order.id))
            .filter(Order.status == OrderStatus.paid)
            .scalar()
            or 0
        )
        pending_orders = (
            self.db.query(func.count(Order.id))
            .filter(Order.status == OrderStatus.pending)
            .scalar()
            or 0
        )
        delivered_orders = (
            self.db.query(func.count(Order.id))
            .filter(Order.status == OrderStatus.delivered)
            .scalar()
            or 0
        )
        cancelled_orders = (
            self.db.query(func.count(Order.id))
            .filter(Order.status == OrderStatus.cancelled)
            .scalar()
            or 0
        )

        # Revenue excludes pending/cancelled orders and counts only fulfilled or paid states.
        total_revenue = (
            self.db.query(func.coalesce(func.sum(Order.total_price), 0.0))
            .filter(Order.status.in_([OrderStatus.paid, OrderStatus.shipped, OrderStatus.delivered]))
            .scalar()
            or 0.0
        )

        total_products = self.db.query(func.count(Product.id)).scalar() or 0
        low_stock_products = (
            self.db.query(func.count(Inventory.id))
            .filter(Inventory.quantity <= 5)
            .scalar()
            or 0
        )

        new_users_last_30_days = (
            self.db.query(func.count(User.id))
            .filter(User.created_at >= last_30_days)
            .scalar()
            or 0
        )

        orders_last_7_days = (
            self.db.query(func.count(Order.id))
            .filter(Order.created_at >= last_7_days)
            .scalar()
            or 0
        )

        successful_payments = (
            self.db.query(func.count(Payment.id))
            .filter(Payment.status == PaymentStatus.successful)
            .scalar()
            or 0
        )
        failed_payments = (
            self.db.query(func.count(Payment.id))
            .filter(Payment.status == PaymentStatus.failed)
            .scalar()
            or 0
        )

        # Cast SQLAlchemy scalar results to plain Python types for schema compatibility.
        return {
            "total_users": int(total_users),
            "total_orders": int(total_orders),
            "paid_orders": int(paid_orders),
            "pending_orders": int(pending_orders),
            "delivered_orders": int(delivered_orders),
            "cancelled_orders": int(cancelled_orders),
            "total_revenue": float(total_revenue),
            "total_products": int(total_products),
            "low_stock_products": int(low_stock_products),
            "new_users_last_30_days": int(new_users_last_30_days),
            "orders_last_7_days": int(orders_last_7_days),
            "successful_payments": int(successful_payments),
            "failed_payments": int(failed_payments),
        }
