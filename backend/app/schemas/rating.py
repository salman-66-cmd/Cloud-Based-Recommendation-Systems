from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class RatingCreate(BaseModel):
    item_id: int
    rating: float = Field(..., ge=1.0, le=5.0)
    review: Optional[str] = None

class RatingResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    rating: float
    review: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserRatingResponse(BaseModel):
    has_rated: bool
    rating: Optional[float] = None
    review: Optional[str] = None
