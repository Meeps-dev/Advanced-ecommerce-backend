"""Service dependency providers.

This module centralizes FastAPI dependency factories so service construction
remains explicit and consistent across route handlers.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.cache import get_cache
from app.dependencies.database import get_db
from app.shared.cache import AppCache

from app.modules.addresses.application.service import AddressService
from app.modules.addresses.infrastructure.repository import AddressRepository
from app.modules.admin.application.service import AdminService
from app.modules.analytics.application.service import AnalyticsService
from app.modules.analytics.infrastructure.repository import AnalyticsRepository
from app.modules.auth.application.service import AuthService
from app.modules.cart.application.service import CartService
from app.modules.cart.infrastructure.repository import CartRepository
from app.modules.catalog.application.category_service import CategoryService
from app.modules.catalog.application.product_service import ProductService
from app.modules.catalog.infrastructure.category_repository import CategoryRepository
from app.modules.catalog.infrastructure.product_image_repository import ProductImageRepository
from app.modules.catalog.infrastructure.product_repository import ProductRepository
from app.modules.inventory.application.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.orders.application.service import OrderService
from app.modules.orders.infrastructure.repository import OrderRepository
from app.modules.payments.application.service import PaymentService
from app.modules.payments.infrastructure.repository import PaymentRepository
from app.modules.reviews.application.service import ReviewService


def get_product_service(
    db: Session = Depends(get_db),
    cache: AppCache = Depends(get_cache),
) -> ProductService:

    product_repo = ProductRepository(db)
    image_repo = ProductImageRepository(db)

    return ProductService(
        product_repo=product_repo,
        image_repo=image_repo,
        cache=cache,
    )



def get_cart_service(
    db: Session = Depends(get_db),
    cache: AppCache = Depends(get_cache),
):
    # Initialize the repositories inside the dependency or pass them in
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    inventory_repo = InventoryRepository(db)
    
    return CartService(
        cart_repo=cart_repo,
        product_repo=product_repo,
        inventory_repo=inventory_repo,
        db=db,  # Pass the session here!
        cache=cache,
    )



def get_inventory_service(
    db: Session = Depends(get_db)
) -> InventoryService:

    inventory_repo = InventoryRepository(db)
    product_repo = ProductRepository(db)

    return InventoryService(
        inventory_repo=inventory_repo,
        product_repo=product_repo
    )


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    repo = CategoryRepository(db)
    return CategoryService(repo)



def get_order_service(
    db: Session = Depends(get_db),
    cache: AppCache = Depends(get_cache),
):
    # 1. Initialize the PaymentService first (using the helper above)
    payment_service = get_payment_service(db)
    
    # 2. Initialize Order-specific repos
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    
    # 3. Return the OrderService with all its tools
    return OrderService(
        cart_repo=cart_repo,
        order_repo=order_repo,
        payment_service=payment_service,
        db=db,
        cache=cache,
    )



def get_payment_service(db: Session = Depends(get_db)):
    # 1. Initialize both required repositories
    payment_repo = PaymentRepository(db)
    order_repo = OrderRepository(db)
    address_repo = AddressRepository(db)
    
    # 2. Pass both to the PaymentService
    return PaymentService(
        payment_repo=payment_repo, 
        order_repo=order_repo,
        address_repo=address_repo,
    )



def get_address_service(db: Session = Depends(get_db)) -> AddressService:
    return AddressService(db)

# Dependency injector for the service
def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    return ReviewService(db)



def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db=db)


# Inject AdminService class as dependency
def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db=db)


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    repo = AnalyticsRepository(db)
    return AnalyticsService(repo=repo)