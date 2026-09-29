from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.category import Category
from app.models.item import Item
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.auth.deps import get_current_admin

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.name).all()
    # Compute item counts
    counts = db.query(Item.category_id, func.count(Item.id)).group_by(Item.category_id).all()
    count_map = {cat_id: count for cat_id, count in counts}

    result = []
    for cat in categories:
        resp = CategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            icon=cat.icon,
            created_at=cat.created_at,
            item_count=count_map.get(cat.id, 0)
        )
        result.append(resp)
    return result

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    cat_in: CategoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    existing = db.query(Category).filter(
        (Category.name == cat_in.name) | (Category.slug == cat_in.slug)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name or slug already exists"
        )
    cat = Category(
        name=cat_in.name,
        slug=cat_in.slug.lower().replace(" ", "-"),
        description=cat_in.description,
        icon=cat_in.icon or "Folder"
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.put("/{cat_id}", response_model=CategoryResponse)
def update_category(
    cat_id: int,
    cat_in: CategoryUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    if cat_in.name is not None:
        cat.name = cat_in.name
    if cat_in.slug is not None:
        cat.slug = cat_in.slug.lower().replace(" ", "-")
    if cat_in.description is not None:
        cat.description = cat_in.description
    if cat_in.icon is not None:
        cat.icon = cat_in.icon

    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return None
