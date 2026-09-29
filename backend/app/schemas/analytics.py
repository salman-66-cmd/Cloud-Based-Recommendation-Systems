from typing import List, Dict, Any
from pydantic import BaseModel

class ChartDataPoint(BaseModel):
    name: str
    value: float
    count: int = 0
    secondary: float = 0.0

class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_items: int
    total_interactions: int
    average_rating: float
    total_ratings: int
    recommendation_requests: int
    cache_hit_rate: float
    popular_categories: List[Dict[str, Any]]
    trending_items: List[Dict[str, Any]]
    interaction_types_breakdown: List[Dict[str, Any]]
    ratings_distribution: List[Dict[str, Any]]
    user_growth: List[Dict[str, Any]]
    daily_interactions: List[Dict[str, Any]]
    algorithm_distribution: List[Dict[str, Any]]

class InteractionLogItem(BaseModel):
    id: int
    user_name: str
    user_email: str
    item_name: str
    interaction_type: str
    weight: float
    created_at: str
