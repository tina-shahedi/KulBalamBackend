from sqlalchemy.orm.session import Session 
from typing import List
from fastapi import HTTPException, status
from db.models import DbProductReview, DbProduct
from schemas import Review

def create_review(db: Session, product_id: int, user_id, request: Review):
    product = db.query(DbProduct).filter(DbProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id {product_id} not found")

    #Check score
    min_score = 1
    max_score = 5
    if request.score < min_score or request.score > max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Score must be between {min_score} and {max_score}"
        )

    existing_review = db.query(DbProductReview).filter(DbProductReview.product_id == product_id, 
                                                       DbProductReview.creator_id == user_id).first()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User with id {user_id} has already created a review for product with id {product_id}'")

    new_review = DbProductReview(
        score = request.score,
        comment = request.comment,
        product_id = product_id,
        creator_id = user_id
    )

    db.add(new_review) 
    db.commit()
    db.refresh(new_review)
    return new_review

def get_all_product_reviews (db: Session, product_id: int):
    product = db.query(DbProduct).filter(DbProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    reviews = db.query(DbProductReview).filter(DbProductReview.product_id == product_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail=f"No reviews found for the product with id {product_id}")
    return reviews

def get_review_by_id(db: Session, id: int):
    review = db.query(DbProductReview).filter(DbProductReview.id == id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with id {id} not found."
        )
    return review

def update_review(db: Session, id: int, score: int, comment: str):
    review = db.query(DbProductReview).filter(DbProductReview.id == id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with id {id} not found."
        )
    #Check score
    min_score = 1
    max_score = 5
    if score < min_score or score > max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Score must be between {min_score} and {max_score}"
        )
    
    review.score = score
    review.comment = comment
    db.commit()
    db.refresh(review)
    return review

def delete_review(db: Session, id: int):
    review = db.query(DbProductReview).filter(DbProductReview.id == id).first()
    if review is None:
        raise HTTPException(status_code=404, detail=f"Review with id {id} not found")

    db.delete(review)
    db.commit()
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)      