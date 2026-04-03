import logging
from typing import Optional

from app.modules.inventory.infrastructure.models.inventory import Inventory
from app.core.exceptions import NotFoundError
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.catalog.infrastructure.product_repository import ProductRepository


logger = logging.getLogger(__name__)


class InventoryService:

    def __init__(
        self,
        inventory_repo: InventoryRepository,
        product_repo: ProductRepository
    ):
        self.inventory_repo = inventory_repo
        self.product_repo = product_repo


    def set_inventory(
        self,
        product_id: int,
        quantity: int
    ) -> Inventory:
        """Upsert inventory quantity for a product."""

        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")

        inventory = self.inventory_repo.get_by_product_id(product_id)

        if inventory:
            inventory = self.inventory_repo.update_quantity(inventory, quantity)
        else:
            inventory = self.inventory_repo.create(product_id, quantity)

        self.inventory_repo.db.commit()
        self.inventory_repo.db.refresh(inventory)

        logger.info(
            "inventory_set",
            extra={
                "event": "inventory_set",
                "entity": "inventory",
                "entity_id": inventory.id,
            },
        )

        return inventory


    def get_inventory(
        self,
        product_id: int
    ) -> Optional[Inventory]:
        """Fetch inventory for a product if it exists."""
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if inventory:
            logger.info(
                "inventory_fetched",
                extra={
                    "event": "inventory_fetched",
                    "entity": "inventory",
                    "entity_id": inventory.id,
                },
            )
        return inventory