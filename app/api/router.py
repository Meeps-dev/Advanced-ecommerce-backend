from fastapi import APIRouter
from app.api import health
from app.modules.addresses.api import routes as addresses
from app.modules.admin.api import routes as admin
from app.modules.analytics.api import routes as analytics
from app.modules.auth.api import routes as auth
from app.modules.cart.api import routes as cart
from app.modules.catalog.api import categories_routes as categories
from app.modules.catalog.api import products_routes as products
from app.modules.inventory.api import routes as inventory
from app.modules.orders.api import routes as orders
from app.modules.payments.api import routes as payments
from app.modules.reviews.api import routes as reviews


api_router = APIRouter()
# Centralize module router registration so app startup has a single API composition point.
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(categories.router)
api_router.include_router(admin.router)
api_router.include_router(analytics.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
api_router.include_router(addresses.router)
api_router.include_router(payments.router)
api_router.include_router(reviews.router)
api_router.include_router(inventory.router)
api_router.include_router(health.router)
