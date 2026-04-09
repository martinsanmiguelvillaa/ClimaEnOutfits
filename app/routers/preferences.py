from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.preferences import Preferences
from app.schemas.user import UserResponse, UserNotificationUpdate
from app.schemas.preferences import PreferenceBody
from app.services.scheduler import schedule_user_notification

router = APIRouter(tags=["preferences"])


@router.post("/{user_id}/outfit_preferences")
def add_user_preferences(user_id: int, body: PreferenceBody, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    new_preferences = Preferences(user_id=user_id, preferences=body.preferences)
    db.add(new_preferences)
    db.commit()
    db.refresh(new_preferences)
    return {"message": "Preferences saved successfully"}

@router.put("/{user_id}/notifications_moment", response_model=UserResponse)
def update_user_notifications(user_id: int, data: UserNotificationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    if data.notifications_enabled and data.notification_time is None:
        raise HTTPException(status_code=400, detail="Si activás las notificaciones, tenés que indicar un horario.")
    current_user.notifications_enabled = data.notifications_enabled
    current_user.notification_time = data.notification_time
    db.commit()
    db.refresh(current_user)
    schedule_user_notification(current_user)
    return current_user

@router.get("/{user_id}/preferences")
def get_user_preferences(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    preferences = db.query(Preferences).filter(Preferences.user_id == user_id).all()
    return {
        "preferences": [
            {"id": pref.id, "preference": pref.preferences}
            for pref in preferences
        ]
    }


@router.patch("/{user_id}/preference/{preference_id}")
def update_user_preference(user_id: int, preference_id: int, body: PreferenceBody, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    preference = db.query(Preferences).filter(
        Preferences.id == preference_id,
        Preferences.user_id == user_id
    ).first()
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    preference.preferences = body.preferences
    db.commit()
    db.refresh(preference)
    return {"id": preference.id, "preference": preference.preferences}


@router.delete("/{user_id}/preference/{preference_id}")
def delete_user_preference(user_id: int, preference_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    preference = db.query(Preferences).filter(
        Preferences.id == preference_id,
        Preferences.user_id == user_id
    ).first()
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    db.delete(preference)
    db.commit()
    return {"message": "Preference deleted successfully"}