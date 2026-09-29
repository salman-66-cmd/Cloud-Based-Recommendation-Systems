from typing import List, Optional
from pydantic import BaseModel

class PreferenceBase(BaseModel):
    preferred_categories: List[str] = []
    preferred_tags: List[str] = []
    preferred_cloud_providers: List[str] = []

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceUpdate(PreferenceBase):
    pass

class PreferenceResponse(PreferenceBase):
    id: int
    user_id: int
    onboarding_completed: bool

    class Config:
        from_attributes = True
