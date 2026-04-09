from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.db import SessionLocal
from app.models.user import User
from app.services.notification import notify_user
from app.services.weather import create_weather_log
from app.logger import get_logger

log = get_logger("services.scheduler")


scheduler = BackgroundScheduler(timezone="America/Argentina/Buenos_Aires")

def remove_user_notification(user_id: int):
    if scheduler.get_job(f"user_notification_{user_id}"):
        scheduler.remove_job(f"user_notification_{user_id}")
        log.info(f"Notificación removida para user_id={user_id}")


def send_scheduled_notification(user_id: int):
    log.info(f"Ejecutando notificación programada para user_id={user_id}")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            log.warning(f"User_id={user_id} no encontrado al ejecutar notificación programada")
            return

        if not user.notifications_enabled:
            log.info(f"User_id={user_id} tiene notificaciones desactivadas, omitiendo")
            return

        if not user.notification_time:
            log.info(f"User_id={user_id} no tiene hora de notificación, omitiendo")
            return

        weather = create_weather_log(db, user_id, user.city)
        notify_user(db, user, weather)
        log.info(f"Notificación enviada correctamente para user_id={user_id}")

    except Exception as e:
        log.error(f"Error al enviar notificación programada para user_id={user_id}: {e}", exc_info=True)
    finally:
        db.close()


def schedule_user_notification(user: User):
    if not user.notifications_enabled or not user.notification_time:
        remove_user_notification(user.id)
        return

    log.info(f"Programando notificación para user_id={user.id} a las {user.notification_time}")

    trigger = CronTrigger(
        hour=user.notification_time.hour,
        minute=user.notification_time.minute,
        timezone="America/Argentina/Buenos_Aires"
    )

    scheduler.add_job(
        send_scheduled_notification,
        trigger=trigger,
        args=[user.id],
        id=f"user_notification_{user.id}",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )