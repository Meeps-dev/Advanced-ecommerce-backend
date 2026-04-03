from sqlalchemy.orm import Session
from app.modules.reviews.infrastructure.models.review import Review


class ReviewRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, product_id: int, rating: int, comment: str) -> Review:
        review = Review(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            comment=comment
        )

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        return review

    def get_by_product(self, product_id: int) -> list[Review]:
        return (
            self.db.query(Review)
            .filter(Review.product_id == product_id)
            .all()
        )
    
    def get_by_id(self, review_id: int) -> Review | None:
        return self.db.query(Review).filter(Review.id == review_id).first()
    
    def update(self, review: Review, rating: int, comment: str) -> Review:
        review.rating = rating
        review.comment = comment

        self.db.commit()
        self.db.refresh(review)

        return review


    def delete(self, review: Review):   
        self.db.delete(review)
        self.db.commit()