from app.services.outfit import get_outfit_recommendation
from app.services.mail import send_mail, build_weather_mail_html, create_mail_log
from app.services.whatsapp import send_whatsapp_message, create_whatsapp_log
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.preferences import Preferences
from app.logger import get_logger

log = get_logger("services.notification")


def notify_user(db: Session, user: User, weather_log: dict):
    city = user.city

    weather = {
        "city": city,
        "temperature": weather_log["temperature"],
        "feels_like": weather_log["feels_like"],
        "humidity": weather_log["humidity"],
        "cloudiness": weather_log["cloudiness"],
        "max_uv_index": weather_log["max_uv_index"],
        "pop": weather_log["pop"],
        "wind_speed": weather_log["wind_speed"],
        "sunset": weather_log["sunset"],
        "description": weather_log["description"]
    }

    prefs = db.query(Preferences).filter(Preferences.user_id == user.id).all()
    weather["preferences"] = " | ".join(pref.preferences for pref in prefs) if prefs else "No hay preferencias"

    outfit = get_outfit_recommendation(weather, user)

    html = build_weather_mail_html(
        weather=weather,
        outfit_summary=outfit["summary"],
        upper_body=outfit["upper_body"],
        lower_body=outfit["lower_body"],
        footwear=outfit["footwear"],
        extras=outfit["extras"]
    )

    subject = f"Clima y outfit recomendado para hoy en {city}"

    whatsapp_variables = {
        "1": user.name,
        "2": city,
        "3": str(weather["temperature"]),
        "4": weather["description"],
        "5": outfit["upper_body"],
        "6": outfit["lower_body"],
        "7": outfit["footwear"],
        "8": outfit["summary"],
    }

    log.info(f"Notificando user_id={user.id} | canal={user.preferred_channel} | ciudad={city}")

    if user.preferred_channel == "whatsapp":
        if not user.whatsapp_opt_in:
            log.warning(f"User_id={user.id} no tiene whatsapp_opt_in activo")
            raise ValueError("El usuario no ha optado por recibir mensajes de WhatsApp")
        if not user.phone_number:
            log.warning(f"User_id={user.id} no tiene número de teléfono")
            raise ValueError("El usuario no tiene un número de teléfono configurado")

        try:
            message_sid = send_whatsapp_message(
                to_number=user.phone_number,
                variables=whatsapp_variables
            )
            create_whatsapp_log(
                db=db,
                user_id=user.id,
                weather_log_id=weather_log["id"],
                to_number=user.phone_number,
                body=str(whatsapp_variables),
                status="sent",
                message_sid=message_sid
            )
            return {"whatsapp": message_sid}
        except Exception as e:
            log.error(f"Error enviando WhatsApp a user_id={user.id}: {e}", exc_info=True)
            create_whatsapp_log(
                db=db,
                user_id=user.id,
                weather_log_id=weather_log["id"],
                to_number=user.phone_number,
                body=str(whatsapp_variables),
                status="error",
                error_message=str(e)
            )
            raise e

    elif user.preferred_channel == "mail":
        try:
            result = send_mail(
                to=user.mail,
                subject=subject,
                html=html
            )

            create_mail_log(
                db=db,
                weather_log_id=weather_log["id"],
                user_id=user.id,
                subject=subject,
                body=html,
                status="sent"
            )

            return {"mail": result}

        except Exception as e:
            log.error(f"Error enviando mail a user_id={user.id}: {e}", exc_info=True)
            create_mail_log(
                db=db,
                user_id=user.id,
                weather_log_id=weather_log["id"],
                subject=subject,
                body=html,
                status="error",
                error_message=str(e)
            )
            raise e

    elif user.preferred_channel == "both":
        if not user.whatsapp_opt_in:
            log.warning(f"User_id={user.id} no tiene whatsapp_opt_in activo (canal=both)")
            raise ValueError("El usuario no ha optado por recibir mensajes de WhatsApp")
        if not user.phone_number:
            log.warning(f"User_id={user.id} no tiene número de teléfono (canal=both)")
            raise ValueError("El usuario no tiene un número de teléfono configurado")

        result = {}

        try:
            mail_result = send_mail(
                to=user.mail,
                subject=subject,
                html=html
            )

            create_mail_log(
                db=db,
                user_id=user.id,
                weather_log_id=weather_log["id"],
                subject=subject,
                body=html,
                status="sent"
            )

            result["mail"] = mail_result

        except Exception as e:
            create_mail_log(
                db=db,
                user_id=user.id,
                weather_log_id=weather_log["id"],
                subject=subject,
                body=html,
                status="error",
                error_message=str(e)
            )
            result["mail_error"] = str(e)

        try:
            whatsapp_result = send_whatsapp_message(
                to_number=user.phone_number,
                variables=whatsapp_variables
            )
            create_whatsapp_log(
                db=db,
                user_id=user.id,
                weather_log_id=weather_log["id"],
                to_number=user.phone_number,
                body=str(whatsapp_variables),
                status="sent",
                message_sid=whatsapp_result
            )
            result["whatsapp"] = whatsapp_result

        except Exception as e:
            create_whatsapp_log(
                db=db,
                user_id=user.id,
                weather_log_id=weather_log["id"],
                to_number=user.phone_number,
                body=str(whatsapp_variables),
                status="error",
                error_message=str(e)
            )
            result["whatsapp_error"] = str(e)

        return result

    else:
        log.error(f"Canal de notificación inválido para user_id={user.id}: {user.preferred_channel}")
        raise ValueError("Canal de notificación inválido")