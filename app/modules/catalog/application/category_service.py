import logging
from app.modules.catalog.api.category_schemas import CategoryCreate
from app.modules.catalog.infrastructure.category_repository import CategoryRepository
from app.core.exceptions import ConflictError


logger = logging.getLogger(__name__)


class CategoryService:

    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    def create_category(self, payload: CategoryCreate):
        """
        Business logic for creating a category.
        """

        # Optional future rule:
        # prevent duplicate category names

        existing = self.repo.get_by_name(payload.name)

        if existing:
            raise ConflictError("Category already exists")

        category = self.repo.create(payload)
        logger.info(
            "category_created",
            extra={
                "event": "category_created",
                "entity": "category",
                "entity_id": category.id,
            },
        )
        return category

    def list_categories(self):
        """
        Returns all categories.
        """
        categories = self.repo.get_all()
        logger.info(
            "categories_listed",
            extra={
                "event": "categories_listed",
                "entity": "category",
            },
        )
        return categories