"""
Address models for the ecommerce application.
Includes shipping addresses and user locations.
"""

from app.modules.addresses.infrastructure.models.shipping_address import ShippingAddress

__all__ = ["ShippingAddress"]
