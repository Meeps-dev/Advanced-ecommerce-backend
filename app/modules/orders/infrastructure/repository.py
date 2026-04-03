from sqlalchemy.orm import Session

from app.modules.orders.infrastructure.models.order import Order
from app.modules.orders.infrastructure.models.order_item import OrderItem
from app.modules.orders.api.schemas import OrderStatus
from app.modules.catalog.infrastructure.models.product import Product
from app.modules.inventory.infrastructure.models.inventory import Inventory


class OrderRepository:

    def __init__(self, db: Session):
        self.db = db


        
    def create_order(self, user_id: int) -> Order:
        db_order = Order(user_id=user_id, status=OrderStatus.pending, total_price=0.0)
        self.db.add(db_order)
        self.db.flush()  # Gets the ID without committing the whole transaction
        return db_order

    def update_order_total(self, order: Order, total: float):
        """Updates the final calculated price after items are added."""
        order.total_price = total
        self.db.add(order)

    def create_order_item(
        self,
        order_id: int,
        product_id: int,
        quantity: int,
        price: float,
    ) -> OrderItem:

        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
        )

        self.db.add(item)
        return item


    def get_order_by_id(self, order_id: int) -> Order | None:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_admin_notification_context(self, order_id: int) -> dict | None:
        """Build enriched order context used by admin email notifications."""
        order = self.get_order_by_id(order_id)
        if not order:
            return None

        item_rows = (
            self.db.query(OrderItem, Product, Inventory)
            .join(Product, Product.id == OrderItem.product_id)
            # Inventory is optional here so admin notifications still render for missing rows.
            .outerjoin(Inventory, Inventory.product_id == Product.id)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        items = []
        total_quantity = 0
        for order_item, product, inventory in item_rows:
            quantity = int(order_item.quantity or 0)
            unit_price = float(order_item.price or 0)
            total_quantity += quantity
            items.append(
                {
                    "product_name": product.name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": quantity * unit_price,
                    "inventory_left": int(inventory.quantity) if inventory else None,
                }
            )

        return {
            "order_id": order.id,
            "customer_email": order.user.email if order.user else "unknown",
            "total": float(order.total_price or 0.0),
            "items_count": total_quantity,
            "items": items,
            "created_at": order.created_at,
        }
    
    def get_all_orders(self) -> list[Order]:
        return self.db.query(Order).all()
    
    def get_orders_by_user_id(self, user_id: int) -> list[Order]:
        return self.db.query(Order).filter(Order.user_id == user_id).all()
    
    def update_order_status(self, order: Order, status):

        order.status = status
        self.db.commit()
        self.db.refresh(order)

        return order
    
    def save_order(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
