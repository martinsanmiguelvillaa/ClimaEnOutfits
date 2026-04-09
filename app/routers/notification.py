from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.limiter import limiter
from app.auth import get_current_user
from app.models.user import User
from app.services.notification import notify_user
from app.services.weather import create_weather_log

router = APIRouter()

@router.post("/notify/{user_id}")
@limiter.limit("5/minute")
def notify_user_route(request: Request, user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    weather_log = create_weather_log(db, user_id, current_user.city)
    result = notify_user(db, current_user, weather_log)
    if current_user.preferred_channel == "whatsapp" and current_user.whatsapp_opt_in and current_user.phone_number:
        return {"message": "Mensaje de WhatsApp enviado", "result": result}
    elif current_user.preferred_channel == "mail":
        return {"message": "Mail enviado", "result": result}
    else:
        return {"message": "Notificación enviada por ambos canales", "result": result} 
    
    