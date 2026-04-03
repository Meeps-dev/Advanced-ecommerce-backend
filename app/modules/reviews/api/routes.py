from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user

from app.dependencies.services import get_review_service
from app.modules.reviews.application.service import ReviewService

from app.modules.reviews.api.schemas import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])



@router.post(
    "/{product_id}",
    response_model=ReviewResponse
)
def create_review(
    product_id: int,
    payload: ReviewCreate,
    current_user = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    return service.add_review(
        user_id=current_user.id,
        product_id=product_id,
        rating=payload.rating,
        comment=payload.comment
    )



@router.get(
    "/{product_id}",
    response_model=list[ReviewResponse]
)
def get_product_reviews(
    product_id: int,
    service: ReviewService = Depends(get_review_service)
):
    return service.get_reviews_for_product(product_id)



@router.get(
    "/{review_id}",
    response_model=ReviewResponse
)
def get_review(
    review_id: int,
    service: ReviewService = Depends(get_review_service)
):
    return service.get_review(review_id)



@router.put(
    "/{review_id}",
    response_model=ReviewResponse
)
def update_review(
    review_id: int,
    payload: ReviewCreate,
    service: ReviewService = Depends(get_review_service)
):
    return service.update_review(
        review_id=review_id,
        rating=payload.rating,
        comment=payload.comment
    )


@router.delete(
    "/{review_id}",
    response_model=ReviewResponse
)
def delete_review(
    review_id: int,
    service: ReviewService = Depends(get_review_service)
): 
  return service.delete_review(review_id)