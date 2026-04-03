import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.events import OrderCheckoutInitiated, OrderShipped, PaymentSucceeded, event_bus
from app.modules.inventory.infrastructure.models.inventory import Inventory
from app.modules.orders.api.schemas import OrderResponse
from app.shared.enums import OrderStatus
from app.modules.orders.infrastructure.repository import OrderRepository
from app.modules.cart.infrastructure.repository import CartRepository
from app.modules.payments.application.service import PaymentService
from app.core.exceptions import ConflictError, NotFoundError, BadRequestError
from app.shared.cache import AppCache


logger = logging.getLogger(__name__)


class OrderService:
    """
    Service layer handles business logic for orders and checkout.
    """

    ORDER_LIST_KEY = "orders:list:v1"
    ORDER_LIST_TTL_SECONDS = 60
    ORDER_DETAIL_TTL_SECONDS = 120

    def __init__(
        self, 
        cart_repo: CartRepository, 
        order_repo: OrderRepository, 
        payment_service: PaymentService, # Ensure this is here!
        db: Session,
        cache: AppCache,
    ):
        self.cart_repo = cart_repo
        self.order_repo = order_repo
        self.payment_service = payment_service
        self.db = db
        self.cache = cache

   
      # --- CORE BUSINESS LOGIC METHODS ---
      
    def checkout(self, user_id: int):
        """Create an order from cart items and reserve inventory atomically."""
        cart = self.cart_repo.get_cart_by_user(user_id)
        if not cart or not cart.items:
            raise BadRequestError("Cart is empty")

        total_price = 0.0
        
        try:
            # 1. Create Order & User Metadata
            order = self.order_repo.create_order(user_id)
            user_email = cart.user.email

            # 2. Inventory Lock & Item Creation
            for cart_item in cart.items:
                # Acquire row-level lock to prevent concurrent decrements of the same stock.
                inventory = self.db.execute(
                    select(Inventory)
                    .where(Inventory.product_id == cart_item.product_id)
                    .with_for_update()
                ).scalar_one()

                if inventory.quantity < cart_item.quantity:
                    raise ConflictError(
                        f"Insufficient stock for {cart_item.product.name}",
                        code="OUT_OF_STOCK",
                    )

                inventory.quantity -= cart_item.quantity
                total_price += (cart_item.quantity * cart_item.product.price)

                self.order_repo.create_order_item(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )

            # 3. Finalize DB State
            self.order_repo.update_order_total(order, total_price)
            self.cart_repo.clear_cart(cart)
            self.db.commit() 
            # Invalidate caches after commit to ensure we don't cache stale data if something rolls back
            self._invalidate_order_cache(order_id=order.id)
            self._invalidate_cart_cache_for_user(user_id=user_id, cart_id=cart.id)

            # 4. 🔥 PAYSTACK HAND-OFF: Don't send emails yet!
            # Get the redirect URL for the user to pay
            payment_results = event_bus.publish(
                OrderCheckoutInitiated(order_id=order.id, user_email=user_email)
            )
            payment_data = next(
                (result for result in payment_results if isinstance(result, dict) and "checkout_url" in result),
                None,
            )
            if payment_data is None:
                raise RuntimeError("Payment initialization listener did not return checkout data")

            logger.info(
                "order_checkout_initiated",
                extra={
                    "event": "order_checkout_initiated",
                    "entity": "order",
                    "entity_id": order.id,
                    "user_id": user_id,
                },
            )

            return {
                "order_id": order.id,
                "status": OrderStatus.pending,
                "checkout_url": payment_data["checkout_url"], # Send this to frontend
                "total": total_price
            }

        except Exception as e:
            # Roll back any partial stock/order changes on failures.
            self.db.rollback()
            raise e


    def mark_order_as_paid(self, order_id: int):
        """
        Called ONLY by the Payment Webhook when success is verified.
        """
        order = self.order_repo.get_order_by_id(order_id)
        if not order:
            return

        if order.status == OrderStatus.paid:
            return # Already processed (idempotency check)

        # 1. Update Status
        order.status = OrderStatus.paid
        self.db.commit()
        self._invalidate_order_cache(order_id=order.id)

        # 2. Publish domain event for listeners (email, analytics, fulfillment)
        total_amount = float(order.total_price or 0.0)
        event_bus.publish(
            PaymentSucceeded(
                payment_id=0,
                order_id=order.id,
                user_id=order.user_id,
                user_email=order.user.email,
                total_amount=total_amount,
            )
        )
        logger.info(
            "order_marked_paid",
            extra={
                "event": "order_paid",
                "entity": "order",
                "entity_id": order.id,
                "user_id": order.user_id,
            },
        )


    def ship_order(self, order_id: int):
        """Mark an order as shipped and queue shipping notifications."""
        order = self.order_repo.get_order_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")

        # In a real app, you'd check for 'paid' status here
        updated_order = self.order_repo.update_order_status(
            order=order,
            status=OrderStatus.shipped,
        )

        event_bus.publish(
            OrderShipped(
                order_id=order.id,
                user_id=order.user_id,
                user_email=order.user.email,
            )
        )

        logger.info(
            "order_shipped",
            extra={
                "event": "order_shipped",
                "entity": "order",
                "entity_id": order_id,
                "user_id": order.user_id,
            },
        )
        # Invalidate caches after status update

        self._invalidate_order_cache(order_id=order_id)

        return updated_order
    


    # Get single order by ID
    def get_order_by_id(self, order_id: int):
        key = self._order_key(order_id)
        cached = self.cache.get_json(key)
        if cached is not None:
            return cached

        order = self.order_repo.get_order_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")

        payload = self._serialize_order(order)
        self.cache.set_json(key, payload, ttl_seconds=self.ORDER_DETAIL_TTL_SECONDS)

        logger.info(
            "order_fetched",
            extra={
                "event": "order_fetched",
                "entity": "order",
                "entity_id": order_id,
                "user_id": order.user_id,
            },
        )
        return payload

    # Get all orders
    def get_all_orders(self):
        cached = self.cache.get_json(self.ORDER_LIST_KEY)
        if cached is not None:
            return cached

        orders = self.order_repo.get_all_orders()
        if not orders:
            raise NotFoundError(message="No orders found")

        payload = [self._serialize_order(order) for order in orders]
        self.cache.set_json(self.ORDER_LIST_KEY, payload, ttl_seconds=self.ORDER_LIST_TTL_SECONDS)

        logger.info(
            "orders_listed",
            extra={
                "event": "orders_listed",
                "entity": "order",
            },
        )
        return payload

    # Update order status
    def update_order_status(self, order_id: int, status):
        order = self.order_repo.get_order_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")
        updated_order = self.order_repo.update_order_status(order, status)
        logger.info(
            "order_status_updated",
            extra={
                "event": "order_status_updated",
                "entity": "order",
                "entity_id": order_id,
                "user_id": order.user_id,
            },
        )
        # Invalidate caches after status update
        self._invalidate_order_cache(order_id=order_id)
        return updated_order

    # Save order
    def save_order(self, order):
        saved_order = self.order_repo.save_order(order)
        saved_order_id = getattr(saved_order, "id", None)
        # Invalidate caches after saving order
        self._invalidate_order_cache(order_id=saved_order_id)
        return saved_order
    
       # Cache keys for orders and carts

    def _order_key(self, order_id: int) -> str:
        return f"orders:id:{order_id}:v1"

    def _cart_summary_key(self, user_id: int) -> str:
        return f"cart:summary:user:{user_id}:v1"

    def _cart_items_key(self, user_id: int) -> str:
        return f"cart:items:user:{user_id}:v1"

    def _cart_count_key(self, user_id: int) -> str:
        return f"cart:count:user:{user_id}:v1"

    def _cart_id_key(self, cart_id: int) -> str:
        return f"cart:id:{cart_id}:v1"

    def _serialize_order(self, order) -> dict:
        return OrderResponse.model_validate(order).model_dump(mode="json")

    def _invalidate_order_cache(self, order_id: int | None = None) -> None:
        keys = [self.ORDER_LIST_KEY]
        if order_id is not None:
            keys.append(self._order_key(order_id))
        self.cache.delete(*keys)

    def _invalidate_cart_cache_for_user(self, user_id: int, cart_id: int | None = None) -> None:
        keys = [
            self._cart_summary_key(user_id),
            self._cart_items_key(user_id),
            self._cart_count_key(user_id),
        ]
        if cart_id is not None:
            keys.append(self._cart_id_key(cart_id))
        self.cache.delete(*keys)