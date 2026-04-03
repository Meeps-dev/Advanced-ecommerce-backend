from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.services import get_cart_service

from app.modules.cart.api.schemas import (
    AddToCartRequest,
    CartItemCountResponse,
    CartItemResponse,
    CartResponse,
    UpdateCartRequest,
)
from app.modules.cart.application.service import CartService


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/items", response_model=CartResponse)
def add_to_cart(
    payload: AddToCartRequest,
    cart_service: CartService = Depends(get_cart_service),
    current_user=Depends(get_current_user),
):
    """
    Add a product to the authenticated user's cart.
    """

    return cart_service.add_to_cart(
        user_id=current_user.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )


@router.get("/", response_model=CartResponse)
def view_cart(
    
    cart_service: CartService = Depends(get_cart_service),
    current_user=Depends(get_current_user),
):
    """
    Retrieve the authenticated user's cart with totals.
    """

    return cart_service.get_cart_summary(
        user_id=current_user.id
    )



@router.get("/items", response_model=list[CartItemResponse])
def get_all_cart_items(
    cart_service: CartService = Depends(get_cart_service),
    current_user = Depends(get_current_user),
):
    """
    Get a flat list of all items currently in the authenticated user's cart.
    """
    return cart_service.get_cart_items(user_id=current_user.id)


@router.get("/items/count", response_model=CartItemCountResponse)
def get_cart_item_count(
    cart_service: CartService = Depends(get_cart_service),
    current_user=Depends(get_current_user),
):
    """
    Return the total quantity of items in the authenticated user's cart.
    """
    return cart_service.get_item_count(user_id=current_user.id)


# NEW: Get cart by ID
@router.get("/{cart_id}", response_model=CartResponse)
def get_cart_by_id(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Retrieve a cart by its ID.
    """
    return cart_service.get_cart_by_id(cart_id=cart_id)


# NEW: Update cart (update quantities of items)
@router.put("/{cart_id}", response_model=CartResponse)
def update_cart(
    cart_id: int,
    payload: UpdateCartRequest,
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Update quantities of items in a cart.
    """
    return cart_service.update_cart(
        cart_id=cart_id,
        updates=payload.items
    )


# NEW: Delete cart by ID
@router.delete("/{cart_id}")
def delete_cart(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Delete a cart and all its items by ID.
    """
    return cart_service.clear_cart(cart_id=cart_id)
    

    # app/api/v1/endpoints/cart.py

@router.delete("/items/{product_id}", response_model=CartResponse)
def remove_item_from_cart(
    product_id: int,
    cart_service: CartService = Depends(get_cart_service),
    current_user = Depends(get_current_user),
):
    """
    Remove a specific product from the authenticated user's cart.
    """
    return cart_service.remove_item(
        user_id=current_user.id, 
        product_id=product_id
    )
