import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.orders.infrastructure.repository import OrderRepository
from app.modules.orders.infrastructure.models.order import Order
from app.modules.users.infrastructure.repository import UserRepository
from app.shared.enums import OrderStatus
from app.core.exceptions import ConflictError, NotFoundError


logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.user_repo = UserRepository(self.db)

    # --- Users ---
    def get_all_users(self):
        """List all users for admin dashboards."""
        users = self.user_repo.get_all_users()
        logger.info(
            "admin_fetched_users",
            extra={
                "event": "admin_users_listed",
                "entity": "user",
            },
        )
        return users

    def delete_user(self, user_id: int) -> dict:
        """Delete a user by ID. Admin action only."""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundError(message=f"User with ID {user_id} not found")

        try:
            success = self.user_repo.delete_user(user_id)
        except IntegrityError as exc:
            raise ConflictError(
                message="Cannot delete user because related records still reference this account"
            ) from exc

        if success:
            logger.info(
                "admin_deleted_user",
                extra={
                    "event": "admin_user_deleted",
                    "entity": "user",
                    "entity_id": user_id,
                    "user_id": user_id,
                },
            )
            return {"message": f"User {user.email} has been deleted successfully"}
        else:
            raise NotFoundError(message=f"User with ID {user_id} not found")


    # --- Orders ---
    def get_all_orders(self) -> list[Order]:
        """Return all orders, raising when repository is empty."""
        orders = self.order_repo.get_all_orders()
        if not orders:
            raise NotFoundError(message="No orders found")
        return orders

    def get_orders_by_user(self, user_id: int) -> list[Order]:
        """List orders belonging to a specific user."""
        orders = self.order_repo.get_orders_by_user_id(user_id)
        if not orders:
            raise NotFoundError(message=f"No orders found for user {user_id}")
        return orders

    def ship_order(self, order_id: int) -> Order:
        """Transition an order to shipped state."""
        order = self.order_repo.get_order_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")
        order.status = OrderStatus.shipped
        self.order_repo.save_order(order)
        logger.info(
            "admin_shipped_order",
            extra={
                "event": "order_shipped",
                "entity": "order",
                "entity_id": order_id,
                "user_id": order.user_id,
            },
        )
        return order

    def deliver_order(self, order_id: int) -> Order:
        """Transition an order to delivered state."""
        order = self.order_repo.get_order_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")
        order.status = OrderStatus.delivered
        self.order_repo.save_order(order)
        logger.info(
            "admin_delivered_order",
            extra={
                "event": "order_delivered",
                "entity": "order",
                "entity_id": order_id,
                "user_id": order.user_id,
            },
        )
        return order