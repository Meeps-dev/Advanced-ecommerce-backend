from sqlalchemy.orm import Session
from app.modules.catalog.infrastructure.models.product_image import ProductImage


class ProductImageRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, product_id: int, image_url: str) -> ProductImage:
        image = ProductImage(
            product_id=product_id,
            image_url=image_url,
        )

        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)

        return image