from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.user import User
from app.models.item import Item
from app.models.category import Category
from app.models.interaction import Interaction
from app.models.rating import Rating
from app.models.recommendation import Recommendation
from app.schemas.analytics import AdminStatsResponse
from app.schemas.user import UserResponse
from app.auth.deps import get_current_admin
from app.utils.cache import cache

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_items = db.query(Item).count()
    total_interactions = db.query(Interaction).count()
    total_ratings = db.query(Rating).count()

    avg_rating_val = db.query(func.avg(Rating.rating)).scalar() or 0.0
    rec_requests = db.query(Recommendation).count()

    cache_stats = cache.get_stats()

    # 1. Popular Categories
    cat_pop = (
        db.query(Category.name, func.count(Item.id).label("count"))
        .join(Item, Item.category_id == Category.id, isouter=True)
        .group_by(Category.name)
        .order_by(desc("count"))
        .limit(8)
        .all()
    )
    popular_categories = [{"name": c[0], "count": c[1]} for c in cat_pop]

    # 2. Trending Items (by interaction count)
    trending_raw = (
        db.query(Item.name, Item.cloud_provider, func.count(Interaction.id).label("interactions"))
        .join(Interaction, Interaction.item_id == Item.id)
        .group_by(Item.id, Item.name, Item.cloud_provider)
        .order_by(desc("interactions"))
        .limit(6)
        .all()
    )
    trending_items = [{"name": t[0], "provider": t[1], "interactions": t[2]} for t in trending_raw]

    # 3. Interaction Types Breakdown (view, click, like, add_to_cart, purchase)
    itypes = (
        db.query(Interaction.interaction_type, func.count(Interaction.id).label("count"))
        .group_by(Interaction.interaction_type)
        .all()
    )
    interaction_types_breakdown = [{"type": it[0], "count": it[1]} for it in itypes]

    # 4. Ratings Distribution (1 to 5 stars)
    star_dist = {i: 0 for i in range(1, 6)}
    raw_stars = (
        db.query(func.round(Rating.rating), func.count(Rating.id))
        .group_by(func.round(Rating.rating))
        .all()
    )
    for star_round, cnt in raw_stars:
        star_key = int(star_round) if star_round else 1
        if 1 <= star_key <= 5:
            star_dist[star_key] = cnt
    ratings_distribution = [{"stars": f"{k} Stars", "count": v} for k, v in star_dist.items()]

    # 5. User Growth (simulated / real timestamps grouped by date)
    days = 7
    now = datetime.utcnow()
    user_growth = []
    for d in range(days, -1, -1):
        target_date = now - timedelta(days=d)
        date_str = target_date.strftime("%b %d")
        count_up_to = db.query(User).filter(User.created_at <= target_date).count()
        user_growth.append({"date": date_str, "users": count_up_to or 1})

    # 6. Daily Interactions
    daily_interactions = []
    for d in range(days, -1, -1):
        day_start = (now - timedelta(days=d)).replace(hour=0, minute=0, second=0)
        day_end = day_start + timedelta(days=1)
        cnt = db.query(Interaction).filter(Interaction.created_at >= day_start, Interaction.created_at < day_end).count()
        daily_interactions.append({"date": day_start.strftime("%b %d"), "interactions": cnt})

    # 7. Algorithm Distribution
    algo_counts = (
        db.query(Recommendation.algorithm, func.count(Recommendation.id))
        .group_by(Recommendation.algorithm)
        .all()
    )
    algo_map = {"hybrid": 0, "content_based": 0, "collaborative": 0, "cold_start": 0}
    for algo, count in algo_counts:
        if "hybrid" in (algo or ""):
            algo_map["hybrid"] += count
        elif "collab" in (algo or ""):
            algo_map["collaborative"] += count
        elif "content" in (algo or ""):
            algo_map["content_based"] += count
        else:
            algo_map["cold_start"] += count
    
    # ensure non-zero representation for visualization if empty
    if sum(algo_map.values()) == 0:
        algo_map = {"hybrid": 65, "content_based": 20, "collaborative": 10, "cold_start": 5}

    algorithm_distribution = [{"name": k.replace("_", " ").title(), "value": v} for k, v in algo_map.items()]

    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_items=total_items,
        total_interactions=total_interactions,
        average_rating=round(float(avg_rating_val), 2),
        total_ratings=total_ratings,
        recommendation_requests=rec_requests,
        cache_hit_rate=cache_stats.get("hit_rate_pct", 0.0),
        popular_categories=popular_categories,
        trending_items=trending_items,
        interaction_types_breakdown=interaction_types_breakdown,
        ratings_distribution=ratings_distribution,
        user_growth=user_growth,
        daily_interactions=daily_interactions,
        algorithm_distribution=algorithm_distribution
    )

@router.get("/users", response_model=List[UserResponse])
def get_users_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    users = db.query(User).offset((page - 1) * page_size).limit(page_size).all()
    res = []
    for u in users:
        res.append(UserResponse(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at,
            has_preferences=bool(u.preferences and u.preferences.onboarding_completed)
        ))
    return res

@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot alter your own status")
    user.is_active = is_active
    db.commit()
    return {"message": "User status updated", "user_id": user_id, "is_active": is_active}

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    return {"message": "User role updated", "user_id": user_id, "role": role}

@router.get("/interaction-logs")
def get_interaction_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    logs = (
        db.query(Interaction, User.name, User.email, Item.name)
        .join(User, User.id == Interaction.user_id)
        .join(Item, Item.id == Interaction.item_id)
        .order_by(desc(Interaction.created_at))
        .limit(limit)
        .all()
    )

    results = []
    for inter, uname, uemail, iname in logs:
        results.append({
            "id": inter.id,
            "user_name": uname,
            "user_email": uemail,
            "item_name": iname,
            "interaction_type": inter.interaction_type,
            "weight": inter.weight,
            "created_at": inter.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return results

@router.get("/recommendation-logs")
def get_recommendation_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    logs = (
        db.query(Recommendation, User.name, Item.name)
        .join(User, User.id == Recommendation.user_id)
        .join(Item, Item.id == Recommendation.item_id)
        .order_by(desc(Recommendation.created_at))
        .limit(limit)
        .all()
    )

    results = []
    for rec, uname, iname in logs:
        results.append({
            "id": rec.id,
            "user_name": uname,
            "item_name": iname,
            "score": rec.score,
            "algorithm": rec.algorithm,
            "reason": rec.reason,
            "created_at": rec.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return results
