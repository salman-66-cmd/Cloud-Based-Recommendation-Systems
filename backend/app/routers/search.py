from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.database import get_db
from app.models.item import Item
from app.models.category import Category
from app.models.search import SearchHistory
from app.schemas.item import ItemResponse
from app.auth.deps import get_optional_current_user

router = APIRouter(prefix="/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None

class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    category_filter: Optional[str] = None
    results_count: int
    created_at: str

@router.post("", response_model=List[ItemResponse])
def execute_search(
    body: SearchRequest,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user)
):
    q_str = body.query.strip()
    if not q_str:
        return []

    s = f"%{q_str}%"
    db_query = db.query(Item).join(Category).filter(
        or_(
            Item.name.ilike(s),
            Item.description.ilike(s),
            Item.tags.ilike(s),
            Item.cloud_provider.ilike(s),
            Category.name.ilike(s)
        )
    )

    if body.category and body.category != "All":
        db_query = db_query.filter(or_(Category.slug == body.category, Category.name == body.category))

    items = db_query.order_by(desc(Item.rating), desc(Item.rating_count)).limit(limit).all()

    # Record search history
    history = SearchHistory(
        user_id=current_user.id if current_user else None,
        query=q_str,
        category_filter=body.category,
        results_count=len(items)
    )
    db.add(history)
    db.commit()

    return items

@router.get("/history", response_model=List[SearchHistoryResponse])
def get_user_search_history(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user)
):
    if not current_user:
        return []

    records = (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == current_user.id)
        .order_by(desc(SearchHistory.created_at))
        .limit(limit)
        .all()
    )

    return [
        SearchHistoryResponse(
            id=r.id,
            query=r.query,
            category_filter=r.category_filter,
            results_count=r.results_count,
            created_at=r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        for r in records
    ]
