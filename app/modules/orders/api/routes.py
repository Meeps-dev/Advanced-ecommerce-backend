from fastapi import APIRouter, Depends
from app.dependencies.auth import admin_required, get_current_user
from app.dependencies.services import get_order_service
from app.modules.orders.api.schemas import OrderResponse, CheckoutResponse
from app.modules.orders.application.service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])

# Checkout endpoint
@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    order_service: OrderService = Depends(get_order_service),
    current_user = Depends(get_current_user),
):
    """
    Convert user's cart into an order and deduct inventory.
    """
    return order_service.checkout(current_user.id)

# Ship order endpoint (admin)
@router.patch("/{order_id}/ship", response_model=OrderResponse)
def ship_order(
    order_id: int,
    order_service: OrderService = Depends(get_order_service),
    admin = Depends(admin_required),
):
    """
    Admin marks order as shipped.
    """
    return order_service.ship_order(order_id)

# Get single order by ID
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    order_service: OrderService = Depends(get_order_service),
    current_user = Depends(get_current_user),
):
    """
    Fetch single order by ID.
    """
    return order_service.get_order_by_id(order_id)

# Get all orders
@router.get("/", response_model=list[OrderResponse])
def get_orders(
    order_service: OrderService = Depends(get_order_service),
    admin = Depends(admin_required),
):
    """
    Fetch all orders (admin only).
    """
    return order_service.get_all_orders()

# Update order status
@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status: str,
    order_service: OrderService = Depends(get_order_service),
    admin = Depends(admin_required),
):
    """
    Update order status (admin only).
    """
    return order_service.update_order_status(order_id, status)


# Save order manually
@router.post("/save", response_model=OrderResponse)
def save_order(
    order_data: dict,
    order_service: OrderService = Depends(get_order_service),
    admin = Depends(admin_required),
):
    """
    Save order manually (admin only).
    """
    return order_service.save_order(order_data)

