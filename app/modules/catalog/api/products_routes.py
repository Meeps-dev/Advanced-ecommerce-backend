from fastapi import APIRouter, Depends, status
from typing import List

from app.dependencies.auth import admin_required
from app.dependencies.services import get_product_service
from app.core.exceptions import NotFoundError

from app.modules.catalog.api.product_schemas import ProductCreate, ProductResponse
from app.modules.catalog.api.product_image_schemas import ProductImageCreate, ProductImageResponse

from app.modules.catalog.application.product_service import ProductService


router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_endpoint(
    payload: ProductCreate,
    service: ProductService = Depends(get_product_service),
    admin=Depends(admin_required),
):
    return service.create_product(payload)


@router.get(
    "/",
    response_model=List[ProductResponse],
)
def list_products_endpoint(
    service: ProductService = Depends(get_product_service),
):
    return service.list_products()


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product_endpoint(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    product = service.get_product_by_id(product_id)

    if not product:
        raise NotFoundError("Product not found")

    return product


@router.post(
    "/{product_id}/images",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_product_image_endpoint(
    product_id: int,
    payload: ProductImageCreate,
    service: ProductService = Depends(get_product_service),
    admin=Depends(admin_required),
):
    return service.add_product_image(product_id, payload)