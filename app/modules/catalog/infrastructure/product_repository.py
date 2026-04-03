from sqlalchemy.orm import Session
from app.modules.catalog.infrastructure.models.product import Product



class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        """
        Persist a new product.
        """
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        """
        Fetch a product by its ID.
        """
        return (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

    def get_all_products(self) -> list[Product]:
         """
         Retrieve all active products.
         """
         return (
            self.db.query(Product)
            .filter(Product.is_active.is_(True))
            .all()
        )