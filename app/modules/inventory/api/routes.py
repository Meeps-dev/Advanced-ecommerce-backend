from fastapi import APIRouter, Depends

from app.core.exceptions import NotFoundError
from app.modules.inventory.application.service import InventoryService
from app.dependencies.services import get_inventory_service

router = APIRouter( prefix="/inventory", tags=["Inventory"]) 


@router.post("/{product_id}")
def set_inventory(
    product_id: int,
    quantity: int,
    service: InventoryService = Depends(get_inventory_service)
):

    return service.set_inventory(product_id, quantity)


@router.get("/{product_id}")
def get_inventory(
    product_id: int,
    service: InventoryService = Depends(get_inventory_service)
):

    inventory = service.get_inventory(product_id)

    if not inventory:
        raise NotFoundError("Inventory not found")

    return inventory