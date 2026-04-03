import logging
from app.modules.catalog.infrastructure.models.product import Product
from app.modules.catalog.api.product_schemas import ProductCreate
from app.modules.catalog.api.product_schemas import ProductResponse
from app.modules.catalog.api.product_image_schemas import ProductImageCreate

from app.modules.catalog.infrastructure.product_repository import ProductRepository
from app.modules.catalog.infrastructure.product_image_repository import ProductImageRepository
from app.core.exceptions import NotFoundError
from app.shared.cache import AppCache


logger = logging.getLogger(__name__)


class ProductService:
    PRODUCT_LIST_KEY = "catalog:products:list:v1"
    PRODUCT_LIST_TTL_SECONDS = 120
    PRODUCT_DETAIL_TTL_SECONDS = 300

    def __init__(
        self,
        product_repo: ProductRepository,
        image_repo: ProductImageRepository,
        cache: AppCache,
    ):
        self.product_repo = product_repo
        self.image_repo = image_repo
        self.cache = cache

    def _product_key(self, product_id: int) -> str:
        return f"catalog:products:id:{product_id}:v1"

    def _serialize_product(self, product: Product) -> dict:
        return ProductResponse.model_validate(product).model_dump(mode="json")

    def create_product(self, payload: ProductCreate) -> Product:
        """Create a product and invalidate list cache."""

        product = Product(
            name=payload.name,
            description=payload.description,
            price=payload.price,
            category_id=payload.category_id,
        )

        created_product = self.product_repo.create(product)
        logger.info(
            "product_created",
            extra={
                "event": "product_created",
                "entity": "product",
                "entity_id": created_product.id,
            },
        )
        self.cache.delete(self.PRODUCT_LIST_KEY)
        return created_product

    def list_products(self):
        """Return cached product listing when available."""
        cached = self.cache.get_json(self.PRODUCT_LIST_KEY)
        if cached is not None:
            return cached

        products = self.product_repo.get_all_products()
        payload = [self._serialize_product(product) for product in products]
        self.cache.set_json(
            self.PRODUCT_LIST_KEY,
            payload,
            ttl_seconds=self.PRODUCT_LIST_TTL_SECONDS,
        )
        logger.info(
            "products_listed",
            extra={
                "event": "products_listed",
                "entity": "product",
            },
        )
        return payload

    def get_product_by_id(self, product_id: int):
        """Return one product payload with per-item cache fallback."""
        key = self._product_key(product_id)
        cached = self.cache.get_json(key)
        if cached is not None:
            return cached

        product = self.product_repo.get_by_id(product_id)
        if product:
            payload = self._serialize_product(product)
            self.cache.set_json(
                key,
                payload,
                ttl_seconds=self.PRODUCT_DETAIL_TTL_SECONDS,
            )
            logger.info(
                "product_fetched",
                extra={
                    "event": "product_fetched",
                    "entity": "product",
                    "entity_id": product_id,
                },
            )
            return payload

        return None

    def add_product_image(
        self,
        product_id: int,
        payload: ProductImageCreate,
    ):
        """Attach an image to a product and clear affected cache keys."""
        product = self.product_repo.get_by_id(product_id)

        if not product:
            raise NotFoundError("Product not found")

        image = self.image_repo.create(
            product_id=product_id,
            image_url=payload.image_url,
        )
        logger.info(
            "product_image_added",
            extra={
                "event": "product_image_added",
                "entity": "product",
                "entity_id": product_id,
            },
        )
        self.cache.delete(self.PRODUCT_LIST_KEY, self._product_key(product_id))
        return image