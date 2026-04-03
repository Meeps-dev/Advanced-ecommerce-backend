from sqlalchemy.orm import Session
from typing import Optional

from app.modules.inventory.infrastructure.models.inventory import Inventory


class InventoryRepository:

    def __init__(self, db: Session):
        self.db = db


    def get_by_product_id(self, product_id: int) -> Optional[Inventory]:
        """Fetch inventory row for a product, if present."""
        return (
            self.db.query(Inventory)
            .filter(Inventory.product_id == product_id)
            .first()
        )


    def create(self, product_id: int, quantity: int) -> Inventory:
        """Create an inventory row without committing outer transaction."""
        inventory = Inventory(
            product_id=product_id,
            quantity=quantity
        )

        self.db.add(inventory)
        self.db.flush()  # allow access to generated fields without committing
        return inventory


    def update_quantity(self, inventory: Inventory, quantity: int) -> Inventory:
        """Update in-memory quantity and flush pending changes."""
        inventory.quantity = quantity
        self.db.flush()
        return inventory