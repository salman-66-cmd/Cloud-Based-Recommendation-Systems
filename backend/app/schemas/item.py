from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.category import CategoryResponse

class ItemBase(BaseModel):
    name: str
    slug: str
    description: str
    category_id: int
    tags: str = ""
    price: float = 0.0
    cloud_provider: str = "Multi-Cloud"
    image_url: Optional[str] = None
    features: Optional[str] = "[]"
    tier: Optional[str] = "Free Tier Available"

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[str] = None
    price: Optional[float] = None
    cloud_provider: Optional[str] = None
    image_url: Optional[str] = None
    features: Optional[str] = None
    tier: Optional[str] = None

class ItemResponse(ItemBase):
    id: int
    rating: float
    rating_count: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True

class ItemDetailResponse(ItemResponse):
    user_rating: Optional[float] = None
    is_liked: Optional[bool] = False
    is_favorited: Optional[bool] = False
    similar_items: List[ItemResponse] = []

class PaginatedItemsResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
