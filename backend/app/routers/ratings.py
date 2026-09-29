from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.rating import Rating
from app.models.item import Item
from app.models.interaction import Interaction
from app.schemas.rating import RatingCreate, RatingResponse, UserRatingResponse
from app.auth.deps import get_current_active_user
from app.utils.cache import cache

router = APIRouter(prefix="/ratings", tags=["Ratings"])

def _update_item_rating_stats(db: Session, item_id: int):
    stats = db.query(
        func.avg(Rating.rating).label("avg_rating"),
        func.count(Rating.id).label("count_rating")
    ).filter(Rating.item_id == item_id).first()

    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        item.rating = round(float(stats.avg_rating or 0.0), 2)
        item.rating_count = int(stats.count_rating or 0)
        db.commit()

@router.post("", response_model=RatingResponse)
def submit_rating(
    rating_in: RatingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    item = db.query(Item).filter(Item.id == rating_in.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_rating = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.item_id == rating_in.item_id
    ).first()

    if existing_rating:
        existing_rating.rating = rating_in.rating
        existing_rating.review = rating_in.review
        db.commit()
        db.refresh(existing_rating)
        rating_obj = existing_rating
    else:
        rating_obj = Rating(
            user_id=current_user.id,
            item_id=rating_in.item_id,
            rating=rating_in.rating,
            review=rating_in.review
        )
        db.add(rating_obj)
        db.commit()
        db.refresh(rating_obj)

    # Record implicit interaction for rating
    inter = Interaction(
        user_id=current_user.id,
        item_id=rating_in.item_id,
        interaction_type="rating",
        weight=min(rating_in.rating, 5.0)
    )
    db.add(inter)
    db.commit()

    # Recalculate average rating & count
    _update_item_rating_stats(db, rating_in.item_id)

    # Invalidate user recommendation cache
    cache.invalidate_user_cache(current_user.id)

    return rating_obj

@router.get("/item/{item_id}", response_model=UserRatingResponse)
def get_item_user_rating(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    r = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.item_id == item_id
    ).first()

    if r:
        return UserRatingResponse(has_rated=True, rating=r.rating, review=r.review)
    return UserRatingResponse(has_rated=False, rating=None, review=None)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.item_id == item_id
    ).delete()
    db.commit()

    _update_item_rating_stats(db, item_id)
    cache.invalidate_user_cache(current_user.id)

    return None

@router.get("/user", response_model=List[RatingResponse])
def get_user_ratings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    return db.query(Rating).filter(Rating.user_id == current_user.id).all()
