from fastapi import APIRouter, Depends
from typing import List

from app.dependencies.auth import admin_required
from app.modules.catalog.api.category_schemas import CategoryCreate, CategoryResponse
from app.modules.catalog.application.category_service import CategoryService
from app.dependencies.services import get_category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "/",
    response_model=CategoryResponse,
    dependencies=[Depends(admin_required)]
)
def create_category(
    payload: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    return service.create_category(payload)


@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    service: CategoryService = Depends(get_category_service),
):
    return service.list_categories()