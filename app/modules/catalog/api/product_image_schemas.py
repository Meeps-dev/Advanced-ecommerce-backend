from pydantic import BaseModel, ConfigDict


class ProductImageCreate(BaseModel):
    image_url: str


class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    product_id: int

    model_config = ConfigDict(from_attributes=True)