import logging
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.modules.cart.infrastructure.repository import CartRepository
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.catalog.infrastructure.product_repository import ProductRepository
from app.shared.cache import AppCache


logger = logging.getLogger(__name__)

class CartService:
    CART_SUMMARY_TTL_SECONDS = 60
    CART_ITEMS_TTL_SECONDS = 60
    CART_COUNT_TTL_SECONDS = 30

    def __init__(
        self,
        cart_repo: CartRepository,
        product_repo: ProductRepository,
        inventory_repo: InventoryRepository,
        db: Session,
        cache: AppCache,
    ):
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.inventory_repo = inventory_repo
        self.db = db
        self.cache = cache

        # Cache keys for carts

    def _summary_key(self, user_id: int) -> str:
        return f"cart:summary:user:{user_id}:v1"

    def _items_key(self, user_id: int) -> str:
        return f"cart:items:user:{user_id}:v1"

    def _count_key(self, user_id: int) -> str:
        return f"cart:count:user:{user_id}:v1"

    def _cart_id_key(self, cart_id: int) -> str:
        return f"cart:id:{cart_id}:v1"

    def _invalidate_cart_cache(self, user_id: int | None = None, cart_id: int | None = None) -> None:
        """Clear cache entries affected by cart mutations."""
        keys: list[str] = []
        if user_id is not None:
            keys.extend(
                [
                    self._summary_key(user_id),
                    self._items_key(user_id),
                    self._count_key(user_id),
                ]
            )
        if cart_id is not None:
            keys.append(self._cart_id_key(cart_id))
        if keys:
            self.cache.delete(*keys)


    
       # --- CART MANAGEMENT METHODS ---
    def add_to_cart(self, user_id: int, product_id: int, quantity: int):
        """Add an item to cart with optimistic stock validation."""
        if quantity <= 0:
            raise BadRequestError("Quantity must be greater than zero")

        cart = self.cart_repo.get_cart_by_user(user_id)
        if not cart:
            cart = self.cart_repo.create_cart(user_id)

        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product")

        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise NotFoundError(message="Inventory record not found")

        cart_item = self.cart_repo.get_cart_item(cart.id, product_id)

        if cart_item:
            # Recheck against live inventory before merging with existing quantity.
            new_quantity = cart_item.quantity + quantity
            if new_quantity > inventory.quantity:
                raise ConflictError("Requested quantity exceeds available stock", code="OUT_OF_STOCK")
            self.cart_repo.update_cart_item(cart_item, quantity=new_quantity)
        else:
            if quantity > inventory.quantity:
                raise ConflictError("Insufficient stock", code="OUT_OF_STOCK")
            self.cart_repo.create_cart_item(cart.id, product_id, quantity)

        self.db.commit()
        self.db.refresh(cart)
        # Invalidate caches after updating cart
        self._invalidate_cart_cache(user_id=user_id, cart_id=cart.id)

        logger.info(
            "cart_item_added",
            extra={
                "event": "cart_item_added",
                "entity": "cart",
                "entity_id": cart.id,
                "user_id": user_id,
            },
        )

        return self.get_cart_summary(user_id)

    def get_cart_summary(self, user_id: int):
        summary_key = self._summary_key(user_id)
        cached = self.cache.get_json(summary_key)
        if cached is not None:
            return cached

        cart = self.cart_repo.get_cart_by_user(user_id)
        if not cart or not cart.items:
            raise NotFoundError(message="No cart items found")

        payload = self._build_cart_response(cart)
        self.cache.set_json(summary_key, payload, ttl_seconds=self.CART_SUMMARY_TTL_SECONDS)

        logger.info(
            "cart_summary_fetched",
            extra={
                "event": "cart_summary_fetched",
                "entity": "cart",
                "entity_id": cart.id,
                "user_id": user_id,
            },
        )
        return payload

    def get_item_count(self, user_id: int):
        count_key = self._count_key(user_id)
        cached = self.cache.get_json(count_key)
        if cached is not None:
            return cached

        cart = self.cart_repo.get_cart_by_user(user_id)

        if not cart or not cart.items:
            raise NotFoundError(message="No cart items found")

        total_items = sum(item.quantity for item in cart.items)
        logger.info(
            "cart_item_count_fetched",
            extra={
                "event": "cart_item_count_fetched",
                "entity": "cart",
                "entity_id": cart.id,
                "user_id": user_id,
            },
        )

        payload = {"total_items": total_items}
        self.cache.set_json(count_key, payload, ttl_seconds=self.CART_COUNT_TTL_SECONDS)
        return payload

    def _build_cart_response(self, cart):
        """Normalize cart entities into the API response shape."""
        if not cart:
            return {"id": 0, "user_id": 0, "items": [], "subtotal": 0, "total_items": 0}

        items_list = []
        subtotal = 0
        total_qty = 0

        for item in cart.items:
            product = item.product
            if not product:
                continue

            line_total = product.price * item.quantity
            items_list.append(
                {
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "price": product.price,
                }
            )
            subtotal += line_total
            total_qty += item.quantity

        return {
            "id": cart.id,
            "user_id": cart.user_id,
            "items": items_list,
            "subtotal": round(subtotal, 2),
            "total_items": total_qty,
        }

    def get_cart_items(self, user_id: int):
        items_key = self._items_key(user_id)
        cached = self.cache.get_json(items_key)
        if cached is not None:
            return cached

        cart = self.cart_repo.get_cart_by_user(user_id)

        if not cart or not cart.items:
            raise NotFoundError(message="No cart items found")

        logger.info(
            "cart_items_listed",
            extra={
                "event": "cart_items_listed",
                "entity": "cart",
                "entity_id": cart.id,
                "user_id": user_id,
            },
        )
        payload = [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.product.price,
            }
            for item in cart.items
            if item.product
        ]
        self.cache.set_json(items_key, payload, ttl_seconds=self.CART_ITEMS_TTL_SECONDS)
        return payload

    def update_cart(self, cart_id: int, updates: list):
        cart = self.cart_repo.get_cart_by_id(cart_id)
        if not cart:
            raise NotFoundError("Cart")

        for item_update in updates:
            item = self.cart_repo.get_cart_item(
                cart_id=cart.id,
                product_id=item_update["product_id"],
            )

            if not item:
                raise NotFoundError(
                    message=f"Cart item for product {item_update['product_id']} not found"
                )

            inventory = self.inventory_repo.get_by_product_id(item_update["product_id"])
            if not inventory:
                raise NotFoundError(message="Inventory record not found")

            if item_update["quantity"] > inventory.quantity:
                raise ConflictError(
                    message=f"Requested quantity for product {item_update['product_id']} exceeds stock",
                    code="OUT_OF_STOCK",
                )

            self.cart_repo.update_cart_item(item, item_update["quantity"])

        self.db.commit()
        self.db.refresh(cart)
        # Invalidate caches after updating cart
        self._invalidate_cart_cache(user_id=cart.user_id, cart_id=cart.id)

        logger.info(
            "cart_updated",
            extra={
                "event": "cart_updated",
                "entity": "cart",
                "entity_id": cart_id,
                "user_id": cart.user_id,
            },
        )

        return {"message": "Cart updated"}

    def get_cart_by_id(self, cart_id: int):
        key = self._cart_id_key(cart_id)
        cached = self.cache.get_json(key)
        if cached is not None:
            return cached

        cart = self.cart_repo.get_cart_by_id(cart_id)
        if not cart:
            raise NotFoundError("Cart not found")

        logger.info(
            "cart_fetched_by_id",
            extra={
                "event": "cart_fetched",
                "entity": "cart",
                "entity_id": cart_id,
                "user_id": cart.user_id,
            },
        )

        payload = self._build_cart_response(cart)
        self.cache.set_json(key, payload, ttl_seconds=self.CART_SUMMARY_TTL_SECONDS)
        return payload

    def clear_cart(self, cart_id: int):
        cart = self.cart_repo.get_cart_by_id(cart_id)

        if not cart:
            raise NotFoundError("Cart not found")

        self.cart_repo.clear_cart(cart)
        self.db.commit()
        self._invalidate_cart_cache(user_id=cart.user_id, cart_id=cart.id)

        logger.info(
            "cart_cleared",
            extra={
                "event": "cart_cleared",
                "entity": "cart",
                "entity_id": cart_id,
                "user_id": cart.user_id,
            },
        )

        return {"message": "Cart cleared"}

     
    def remove_item(self, user_id: int, product_id: int):
        cart = self.cart_repo.get_cart_by_user(user_id)
        if not cart:
            raise NotFoundError("Cart not found")

        item = self.cart_repo.get_cart_item(cart.id, product_id)
        if not item:
            raise NotFoundError(message="Item not found in cart")

        self.cart_repo.remove_cart_item(cart.id, product_id)
        self.db.commit()
        # Invalidate caches after updating cart
        self._invalidate_cart_cache(user_id=user_id, cart_id=cart.id)

        logger.info(
            "cart_item_removed",
            extra={
                "event": "cart_item_removed",
                "entity": "cart",
                "entity_id": cart.id,
                "user_id": user_id,
            },
        )

        return self.get_cart_summary(user_id)
