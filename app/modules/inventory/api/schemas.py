from pydantic import BaseModel, ConfigDict


class InventoryCreate(BaseModel):
    quantity: int

class InventoryResponse(BaseModel):
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)