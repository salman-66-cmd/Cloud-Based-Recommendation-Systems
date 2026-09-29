from typing import Optional, List
import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.database import get_db
from app.models.item import Item
from app.models.category import Category
from app.models.interaction import Interaction
from app.models.rating import Rating
from app.schemas.item import (
    ItemCreate, ItemUpdate, ItemResponse, ItemDetailResponse, PaginatedItemsResponse
)
from app.auth.deps import get_current_admin, get_optional_current_user
from app.recommendation.engine import recommendation_engine
from app.utils.cache import cache

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("", response_model=PaginatedItemsResponse)
def get_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    cloud_provider: Optional[str] = None,
    sort_by: Optional[str] = Query("popular", pattern="^(popular|rating|newest|price_asc|price_desc)$"),
    db: Session = Depends(get_db)
):
    query = db.query(Item).join(Category)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Item.name.ilike(s),
                Item.description.ilike(s),
                Item.tags.ilike(s),
                Category.name.ilike(s)
            )
        )

    if category:
        query = query.filter(or_(Category.slug == category, Category.name == category))

    if cloud_provider and cloud_provider != "All":
        query = query.filter(Item.cloud_provider == cloud_provider)

    if sort_by == "rating":
        query = query.order_by(desc(Item.rating), desc(Item.rating_count))
    elif sort_by == "newest":
        query = query.order_by(desc(Item.created_at))
    elif sort_by == "price_asc":
        query = query.order_by(asc(Item.price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Item.price))
    else:  # popular
        query = query.order_by(desc(Item.rating_count), desc(Item.rating))

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PaginatedItemsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{item_id}", response_model=ItemDetailResponse)
def get_item_detail(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    user_rating = None
    is_liked = False
    is_favorited = False

    # Track view interaction if user is authenticated
    if current_user:
        view_interaction = Interaction(
            user_id=current_user.id,
            item_id=item_id,
            interaction_type="view",
            weight=1.0
        )
        db.add(view_interaction)
        db.commit()

        # Check user's rating
        r = db.query(Rating).filter(Rating.user_id == current_user.id, Rating.item_id == item_id).first()
        if r:
            user_rating = r.rating

        # Check likes/favorites
        like_count = db.query(Interaction).filter(
            Interaction.user_id == current_user.id,
            Interaction.item_id == item_id,
            Interaction.interaction_type == "like"
        ).count()
        is_liked = like_count > 0
        is_favorited = is_liked

    # Get similar items
    similar_raw = recommendation_engine.get_similar_items(item_id, db, limit=4)
    similar_items = []
    for sim in similar_raw:
        sim_item = db.query(Item).filter(Item.id == sim["item_id"]).first()
        if sim_item:
            similar_items.append(sim_item)

    return ItemDetailResponse(
        id=item.id,
        name=item.name,
        slug=item.slug,
        description=item.description,
        category_id=item.category_id,
        tags=item.tags,
        price=item.price,
        cloud_provider=item.cloud_provider,
        image_url=item.image_url,
        features=item.features,
        tier=item.tier,
        rating=item.rating,
        rating_count=item.rating_count,
        created_at=item.created_at,
        updated_at=item.updated_at,
        category=item.category,
        user_rating=user_rating,
        is_liked=is_liked,
        is_favorited=is_favorited,
        similar_items=similar_items
    )

@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    # Verify category
    cat = db.query(Category).filter(Category.id == item_in.category_id).first()
    if not cat:
        raise HTTPException(status_code=400, detail="Invalid category ID")

    item = Item(
        name=item_in.name,
        slug=item_in.slug.lower().replace(" ", "-"),
        description=item_in.description,
        category_id=item_in.category_id,
        tags=item_in.tags,
        price=item_in.price,
        cloud_provider=item_in.cloud_provider,
        image_url=item_in.image_url,
        features=item_in.features or "[]",
        tier=item_in.tier or "Free Tier Available",
        rating=0.0,
        rating_count=0
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    # Invalidate cache and trigger model rebuild
    cache.delete_pattern("recommendations:*")
    recommendation_engine.build_content_model(db)

    return item

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item_in.name is not None:
        item.name = item_in.name
    if item_in.slug is not None:
        item.slug = item_in.slug.lower().replace(" ", "-")
    if item_in.description is not None:
        item.description = item_in.description
    if item_in.category_id is not None:
        item.category_id = item_in.category_id
    if item_in.tags is not None:
        item.tags = item_in.tags
    if item_in.price is not None:
        item.price = item_in.price
    if item_in.cloud_provider is not None:
        item.cloud_provider = item_in.cloud_provider
    if item_in.image_url is not None:
        item.image_url = item_in.image_url
    if item_in.features is not None:
        item.features = item_in.features
    if item_in.tier is not None:
        item.tier = item_in.tier

    db.commit()
    db.refresh(item)

    # Invalidate cache
    cache.delete_pattern("recommendations:*")
    recommendation_engine.build_content_model(db)

    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    cache.delete_pattern("recommendations:*")
    recommendation_engine.build_content_model(db)

    return None
