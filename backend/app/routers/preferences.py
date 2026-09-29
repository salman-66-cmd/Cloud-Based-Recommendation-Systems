import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.preference import UserPreference
from app.schemas.preference import PreferenceCreate, PreferenceResponse
from app.auth.deps import get_current_active_user
from app.utils.cache import cache

router = APIRouter(prefix="/preferences", tags=["Preferences"])

@router.get("", response_model=PreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id, onboarding_completed=False)
        db.add(pref)
        db.commit()
        db.refresh(pref)

    cats = []
    tags = []
    providers = []
    try:
        cats = json.loads(pref.preferred_categories or "[]")
        tags = json.loads(pref.preferred_tags or "[]")
        providers = json.loads(pref.preferred_cloud_providers or "[]")
    except Exception:
        pass

    return PreferenceResponse(
        id=pref.id,
        user_id=pref.user_id,
        preferred_categories=cats,
        preferred_tags=tags,
        preferred_cloud_providers=providers,
        onboarding_completed=pref.onboarding_completed
    )

@router.post("", response_model=PreferenceResponse)
def save_preferences(
    pref_in: PreferenceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    pref.preferred_categories = json.dumps(pref_in.preferred_categories)
    pref.preferred_tags = json.dumps(pref_in.preferred_tags)
    pref.preferred_cloud_providers = json.dumps(pref_in.preferred_cloud_providers)
    pref.onboarding_completed = True

    db.commit()
    db.refresh(pref)

    # Invalidate cache so fresh cold-start / personalized recs generate immediately
    cache.invalidate_user_cache(current_user.id)

    return PreferenceResponse(
        id=pref.id,
        user_id=pref.user_id,
        preferred_categories=pref_in.preferred_categories,
        preferred_tags=pref_in.preferred_tags,
        preferred_cloud_providers=pref_in.preferred_cloud_providers,
        onboarding_completed=True
    )
