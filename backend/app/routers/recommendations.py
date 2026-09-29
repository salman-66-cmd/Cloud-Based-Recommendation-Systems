import time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.item import Item
from app.schemas.recommendation import (
    RecommendationsResponse, RecommendationItem, RecommendationDiagnostics
)
from app.schemas.item import ItemResponse
from app.auth.deps import get_optional_current_user
from app.recommendation.engine import recommendation_engine
from app.utils.cache import cache
from app.config import settings

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

def _populate_item_objects(db: Session, raw_recs: List[dict]) -> List[RecommendationItem]:
    """Helper to attach full item details to recommendation records."""
    if not raw_recs:
        return []

    item_ids = [r["item_id"] for r in raw_recs]
    items = db.query(Item).filter(Item.id.in_(item_ids)).all()
    item_map = {item.id: item for item in items}

    results = []
    for r in raw_recs:
        item = item_map.get(r["item_id"])
        if item:
            item_resp = ItemResponse.model_validate(item)
            results.append(
                RecommendationItem(
                    item_id=r["item_id"],
                    score=r["score"],
                    reason=r["reason"],
                    algorithm=r.get("algorithm", "hybrid"),
                    content_score=r.get("content_score"),
                    collaborative_score=r.get("collaborative_score"),
                    item=item_resp
                )
            )
    return results

@router.get("", response_model=RecommendationsResponse)
@router.get("/personalized", response_model=RecommendationsResponse)
def get_personalized_recommendations(
    content_weight: Optional[float] = Query(None, ge=0.0, le=1.0),
    collab_weight: Optional[float] = Query(None, ge=0.0, le=1.0),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user)
):
    start_time = time.time()
    user_id = current_user.id if current_user else None

    # Check cache if user and default weights
    cache_key = f"recommendations:user:{user_id or 'guest'}:w{content_weight}_{collab_weight}_l{limit}"
    cached_data = cache.get_json(cache_key)
    if cached_data:
        # Re-attach fresh item objects
        populated = _populate_item_objects(db, cached_data["raw"])
        exec_ms = round((time.time() - start_time) * 1000, 2)
        return RecommendationsResponse(
            user_id=user_id,
            algorithm=cached_data.get("algorithm", "hybrid"),
            cached=True,
            execution_time_ms=exec_ms,
            recommendations=populated
        )

    # Compute recommendations using engine
    if user_id:
        raw_recs = recommendation_engine.get_hybrid_recommendations(
            user_id=user_id,
            db=db,
            content_weight=content_weight,
            collab_weight=collab_weight,
            limit=limit
        )
        algo_name = "hybrid"
    else:
        raw_recs = recommendation_engine.get_cold_start_recommendations(
            user_id=None,
            db=db,
            limit=limit
        )
        algo_name = "cold_start_guest"

    # Save to cache (raw list)
    cache.set_json(cache_key, {"raw": raw_recs, "algorithm": algo_name}, ttl=1800)

    populated = _populate_item_objects(db, raw_recs)
    exec_ms = round((time.time() - start_time) * 1000, 2)

    return RecommendationsResponse(
        user_id=user_id,
        algorithm=algo_name,
        cached=False,
        execution_time_ms=exec_ms,
        recommendations=populated
    )

@router.get("/content-based", response_model=RecommendationsResponse)
def get_content_based(
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user)
):
    start_time = time.time()
    user_id = current_user.id if current_user else None

    if user_id:
        raw_recs = recommendation_engine.get_content_based_recommendations(user_id, db, limit=limit)
    else:
        raw_recs = recommendation_engine.get_cold_start_recommendations(None, db, limit=limit)

    populated = _populate_item_objects(db, raw_recs)
    exec_ms = round((time.time() - start_time) * 1000, 2)

    return RecommendationsResponse(
        user_id=user_id,
        algorithm="content_based",
        cached=False,
        execution_time_ms=exec_ms,
        recommendations=populated
    )

@router.get("/collaborative", response_model=RecommendationsResponse)
def get_collaborative(
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user)
):
    start_time = time.time()
    user_id = current_user.id if current_user else None

    if user_id:
        raw_recs = recommendation_engine.get_collaborative_recommendations(user_id, db, limit=limit)
    else:
        raw_recs = recommendation_engine.get_cold_start_recommendations(None, db, limit=limit)

    populated = _populate_item_objects(db, raw_recs)
    exec_ms = round((time.time() - start_time) * 1000, 2)

    return RecommendationsResponse(
        user_id=user_id,
        algorithm="collaborative",
        cached=False,
        execution_time_ms=exec_ms,
        recommendations=populated
    )

@router.get("/trending", response_model=RecommendationsResponse)
def get_trending(
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    cache_key = f"recommendations:trending:limit_{limit}"
    cached_data = cache.get_json(cache_key)

    if cached_data:
        populated = _populate_item_objects(db, cached_data["raw"])
        exec_ms = round((time.time() - start_time) * 1000, 2)
        return RecommendationsResponse(
            user_id=None,
            algorithm="trending_velocity",
            cached=True,
            execution_time_ms=exec_ms,
            recommendations=populated
        )

    raw_recs = recommendation_engine.get_trending_items(db, limit=limit)
    cache.set_json(cache_key, {"raw": raw_recs}, ttl=900)

    populated = _populate_item_objects(db, raw_recs)
    exec_ms = round((time.time() - start_time) * 1000, 2)

    return RecommendationsResponse(
        user_id=None,
        algorithm="trending_velocity",
        cached=False,
        execution_time_ms=exec_ms,
        recommendations=populated
    )

@router.get("/popular", response_model=RecommendationsResponse)
def get_popular(
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    cache_key = f"recommendations:popular:limit_{limit}"
    cached_data = cache.get_json(cache_key)

    if cached_data:
        populated = _populate_item_objects(db, cached_data["raw"])
        exec_ms = round((time.time() - start_time) * 1000, 2)
        return RecommendationsResponse(
            user_id=None,
            algorithm="top_rated_popularity",
            cached=True,
            execution_time_ms=exec_ms,
            recommendations=populated
        )

    items = db.query(Item).order_by(desc(Item.rating), desc(Item.rating_count)).limit(limit).all()
    raw_recs = []
    for item in items:
        raw_recs.append({
            "item_id": item.id,
            "score": round(0.7 + (item.rating / 50.0), 4),
            "reason": f"Highly acclaimed ({item.rating}★ from {item.rating_count} engineers)",
            "algorithm": "top_rated_popularity",
            "content_score": 0.5,
            "collaborative_score": 0.5
        })

    cache.set_json(cache_key, {"raw": raw_recs}, ttl=1800)
    populated = _populate_item_objects(db, raw_recs)
    exec_ms = round((time.time() - start_time) * 1000, 2)

    return RecommendationsResponse(
        user_id=None,
        algorithm="top_rated_popularity",
        cached=False,
        execution_time_ms=exec_ms,
        recommendations=populated
    )

@router.get("/similar/{item_id}", response_model=RecommendationsResponse)
def get_similar_items_route(
    item_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    raw_recs = recommendation_engine.get_similar_items(item_id, db, limit=limit)
    populated = _populate_item_objects(db, raw_recs)
    exec_ms = round((time.time() - start_time) * 1000, 2)

    return RecommendationsResponse(
        user_id=None,
        algorithm="content_cosine_similarity",
        cached=False,
        execution_time_ms=exec_ms,
        recommendations=populated
    )

@router.get("/diagnostics", response_model=RecommendationDiagnostics)
def get_diagnostics(db: Session = Depends(get_db)):
    from app.models.user import User
    from app.models.interaction import Interaction

    total_users = db.query(User).count()
    total_items = db.query(Item).count()
    total_interactions = db.query(Interaction).count()
    cache_stats = cache.get_stats()

    return RecommendationDiagnostics(
        total_users=total_users,
        total_items=total_items,
        total_interactions=total_interactions,
        content_weight=settings.DEFAULT_CONTENT_WEIGHT,
        collaborative_weight=settings.DEFAULT_COLLAB_WEIGHT,
        cache_backend=cache_stats["backend"],
        cache_connected=cache_stats["redis_connected"]
    )
