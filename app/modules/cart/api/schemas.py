from pydantic import BaseModel, ConfigDict


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int


class CartItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)

class UpdateCartRequest(BaseModel):
    items: list[CartItemResponse]
    
    
class CartResponse(BaseModel):
    id: int  # <-- ENSURE THIS LINE EXISTS
    user_id: int
    items: list[CartItemResponse]
    subtotal: float
    total_items: int


class CartItemCountResponse(BaseModel):
    total_items: int

    