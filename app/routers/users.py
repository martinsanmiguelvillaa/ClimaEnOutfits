from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.limiter import limiter
from app.auth import hash_password, get_current_user
from app.models.user import User
from app.models.preferences import Preferences
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserNotificationUpdate
from app.services.weather import create_weather_log
from app.services.outfit import get_outfit_recommendation
from app.services.scheduler import schedule_user_notification

router = APIRouter(tags=["users"])


@router.post("", response_model=UserResponse)
@limiter.limit("5/minute")
def create_user(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    if user_data.notifications_enabled and user_data.notification_time is None:
        raise HTTPException(
            status_code=400,
            detail="Si las notificaciones están activadas, tenés que indicar un horario."
        )

    if user_data.preferred_channel == "whatsapp" and not user_data.whatsapp_opt_in:
        raise HTTPException(
            status_code=400,
            detail="No podés elegir WhatsApp si el usuario no hizo opt-in."
        )
    
    existing_mail = db.query(User).filter(User.mail == user_data.mail).first()
    existing_phone = db.query(User).filter(User.phone_number == user_data.phone_number).first()
    if existing_mail or existing_phone:
        raise HTTPException(
        status_code=400,
        detail="El usuario ya existe"
    )

    user = User(
        name=user_data.name,
        last_name=user_data.last_name,
        gender=user_data.gender,
        mail=user_data.mail,
        phone_number=user_data.phone_number,
        password_hash=hash_password(user_data.password),
        whatsapp_opt_in=user_data.whatsapp_opt_in,
        preferred_channel=user_data.preferred_channel,
        city=user_data.city,
        notifications_enabled=user_data.notifications_enabled,
        notification_time=user_data.notification_time
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    schedule_user_notification(user)
    return user

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    return current_user

@router.delete("/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/{user_id}/weather")
def get_user_weather(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    try:
        weather_data = create_weather_log(db, current_user.id, current_user.city)
        return {
            "user_id": current_user.id,
            "user_name": current_user.name,
            "weather": weather_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener el clima")


@router.get("/{user_id}/outfit")
def get_user_outfit(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    preferences = db.query(Preferences).filter(Preferences.user_id == user_id).all()
    try:
        weather_data = create_weather_log(db, current_user.id, current_user.city)
        weather_data["preferences"] = " | ".join(pref.preferences for pref in preferences) if preferences else "No hay preferencias"
        outfit_data = get_outfit_recommendation(weather_data, current_user)
        return {
            "user_id": current_user.id,
            "user_name": current_user.name,
            "weather": weather_data,
            "outfit": outfit_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener el outfit")

