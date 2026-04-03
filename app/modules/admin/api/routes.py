from fastapi import APIRouter, Depends

from typing import List

from app.dependencies.auth import admin_required
from app.dependencies.services import get_admin_service
from app.modules.users.api.schemas import UserResponse
from app.modules.orders.api.schemas import OrderResponse
from app.modules.admin.application.service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])




# --- Users ---
@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    service: AdminService = Depends(get_admin_service),
    current_admin = Depends(admin_required)
):
    return service.get_all_users()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    service: AdminService = Depends(get_admin_service),
    current_admin = Depends(admin_required)
):
    """
    Delete a user by ID (admin only).
    """
    return service.delete_user(user_id)


# --- Orders ---
@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(
    service: AdminService = Depends(get_admin_service),
    current_admin = Depends(admin_required)
):
    return service.get_all_orders()


@router.get("/orders/user/{user_id}", response_model=List[OrderResponse])
def get_orders_by_user(
    user_id: int,
    service: AdminService = Depends(get_admin_service),
    current_admin = Depends(admin_required)
):
    return service.get_orders_by_user(user_id)


@router.patch("/orders/{order_id}/ship", response_model=OrderResponse)
def ship_order(
    order_id: int,
    service: AdminService = Depends(get_admin_service),
    current_admin = Depends(admin_required)
):
    return service.ship_order(order_id)


@router.patch("/orders/{order_id}/deliver", response_model=OrderResponse)
def deliver_order(
    order_id: int,
    service: AdminService = Depends(get_admin_service),
    current_admin = Depends(admin_required)
):
    return service.deliver_order(order_id)

