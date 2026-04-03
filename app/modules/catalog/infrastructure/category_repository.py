from sqlalchemy.orm import Session
from app.modules.catalog.infrastructure.models.category import Category
from app.modules.catalog.api.category_schemas import CategoryCreate


class CategoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: CategoryCreate) -> Category:
        category = Category(
            name=payload.name,
            description=payload.description
        )

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    def get_all(self) -> list[Category]:
        return self.db.query(Category).all()

    def get_by_name(self, name: str) -> Category | None:
        return (
            self.db.query(Category)
            .filter(Category.name == name)
            .first()
        )