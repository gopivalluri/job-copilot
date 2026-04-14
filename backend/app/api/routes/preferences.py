"""
Preferences API routes
GET  /preferences     - get user preferences
POST /preferences     - create or update preferences
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import User, UserPreferences
from app.schemas.schemas import PreferencesCreate, PreferencesOut

router = APIRouter()


@router.get("", response_model=PreferencesOut)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not set yet")
    return prefs


@router.post("", response_model=PreferencesOut)
def upsert_preferences(
    payload: PreferencesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or fully replace user preferences."""
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    if prefs:
        for field, value in payload.model_dump().items():
            setattr(prefs, field, value)
    else:
        prefs = UserPreferences(user_id=current_user.id, **payload.model_dump())
        db.add(prefs)

    db.commit()
    db.refresh(prefs)
    return prefs
