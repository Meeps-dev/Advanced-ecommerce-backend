import logging
from sqlalchemy.orm import Session

from app.modules.reviews.infrastructure.repository import ReviewRepository
from app.modules.catalog.infrastructure.product_repository import ProductRepository

from app.modules.orders.infrastructure.models.order import Order
from app.modules.orders.infrastructure.models.order_item import OrderItem
from app.core.exceptions import ForbiddenError, NotFoundError


logger = logging.getLogger(__name__)


class ReviewService:

    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.product_repo = ProductRepository(db)

    def add_review(
        self,
        user_id: int,
        product_id: int,
        rating: int,
        comment: str
    ):
        """Create a review only when the user has purchased the product."""

        product = self.product_repo.get_by_id(product_id)

        if not product:
            raise NotFoundError("Product not found")

        # Anti-abuse rule: reviews are allowed only for products the user bought.
        purchased = (
            self.db.query(OrderItem)
            .join(Order)
            .filter(
                Order.user_id == user_id,
                OrderItem.product_id == product_id
            )
            .first()
        )

        if not purchased:
            raise ForbiddenError("You must purchase product before reviewing")

        review = self.review_repo.create(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            comment=comment
        )
        logger.info(
            "review_created",
            extra={
                "event": "review_created",
                "entity": "review",
                "entity_id": review.id,
                "user_id": user_id,
            },
        )
        return review

    def get_reviews_for_product(self, product_id: int):
        reviews = self.review_repo.get_by_product(product_id)
        logger.info(
            "reviews_listed_for_product",
            extra={
                "event": "reviews_listed",
                "entity": "review",
                "entity_id": product_id,
            },
        )
        return reviews
    
    def get_review(self, review_id: int):
        review = self.review_repo.get_by_id(review_id)

        if not review:
            raise NotFoundError("Review not found")

        logger.info(
            "review_fetched",
            extra={
                "event": "review_fetched",
                "entity": "review",
                "entity_id": review_id,
                "user_id": review.user_id,
            },
        )
        return review

    def update_review(self, review_id: int, rating: int, comment: str):

        review = self.review_repo.get_by_id(review_id)

        if not review:
            raise NotFoundError("Review not found")

        updated_review = self.review_repo.update(review, rating, comment)
        logger.info(
            "review_updated",
            extra={
                "event": "review_updated",
                "entity": "review",
                "entity_id": review_id,
                "user_id": updated_review.user_id,
            },
        )
        return updated_review


    def delete_review(self, review_id: int):    
        review = self.review_repo.get_by_id(review_id)

        if not review:
            raise NotFoundError("Review not found")

        self.review_repo.delete(review)
        logger.info(
            "review_deleted",
            extra={
                "event": "review_deleted",
                "entity": "review",
                "entity_id": review_id,
                "user_id": review.user_id,
            },
        )
        