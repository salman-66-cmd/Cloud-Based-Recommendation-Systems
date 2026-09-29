from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.interaction import Interaction
from app.models.item import Item
from app.schemas.interaction import InteractionCreate, InteractionResponse
from app.schemas.item import ItemResponse
from app.auth.deps import get_current_active_user
from app.utils.cache import cache

router = APIRouter(prefix="/interactions", tags=["Interactions"])

WEIGHT_MAP = {
    "view": 1.0,
    "click": 1.5,
    "like": 3.0,
    "add_to_cart": 4.0,
    "purchase": 5.0
}

@router.post("", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def record_interaction(
    interaction_in: InteractionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    item = db.query(Item).filter(Item.id == interaction_in.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    itype = interaction_in.interaction_type.lower()
    weight = WEIGHT_MAP.get(itype, 1.0)

    interaction = Interaction(
        user_id=current_user.id,
        item_id=interaction_in.item_id,
        interaction_type=itype,
        weight=weight
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    # Invalidate user recommendation cache
    cache.invalidate_user_cache(current_user.id)

    return interaction

@router.get("/favorites", response_model=List[ItemResponse])
def get_user_favorites(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    # Find items liked by user
    fav_interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == current_user.id, Interaction.interaction_type == "like")
        .order_by(desc(Interaction.created_at))
        .all()
    )
    item_ids = list(dict.fromkeys([fav.item_id for fav in fav_interactions]))
    if not item_ids:
        return []

    items = db.query(Item).filter(Item.id.in_(item_ids)).all()
    # maintain order
    item_dict = {item.id: item for item in items}
    ordered = [item_dict[iid] for iid in item_ids if iid in item_dict]
    return ordered

@router.delete("/favorites/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    db.query(Interaction).filter(
        Interaction.user_id == current_user.id,
        Interaction.item_id == item_id,
        Interaction.interaction_type == "like"
    ).delete()
    db.commit()
    cache.invalidate_user_cache(current_user.id)
    return None
