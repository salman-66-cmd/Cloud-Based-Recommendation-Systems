from datetime import datetime
from pydantic import BaseModel, Field

class InteractionCreate(BaseModel):
    item_id: int
    interaction_type: str = Field(..., description="view, click, like, add_to_cart, purchase")

class InteractionResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    interaction_type: str
    weight: float
    created_at: datetime

    class Config:
        from_attributes = True
