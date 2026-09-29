from typing import List, Optional
from pydantic import BaseModel
from app.schemas.item import ItemResponse

class RecommendationItem(BaseModel):
    item_id: int
    score: float
    reason: str
    algorithm: str
    content_score: Optional[float] = None
    collaborative_score: Optional[float] = None
    item: Optional[ItemResponse] = None

class RecommendationsResponse(BaseModel):
    user_id: Optional[int] = None
    algorithm: str
    cached: bool = False
    execution_time_ms: float = 0.0
    recommendations: List[RecommendationItem] = []

class RecommendationDiagnostics(BaseModel):
    total_users: int
    total_items: int
    total_interactions: int
    content_weight: float
    collaborative_weight: float
    cache_backend: str
    cache_connected: bool
