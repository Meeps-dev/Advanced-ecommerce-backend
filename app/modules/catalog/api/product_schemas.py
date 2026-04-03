from pydantic import BaseModel, ConfigDict
from app.modules.catalog.api.category_schemas import CategoryResponse

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    category_id: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    is_active: bool
    category: CategoryResponse

    model_config = ConfigDict(from_attributes=True)