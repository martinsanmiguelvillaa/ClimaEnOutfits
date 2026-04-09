import os
from dotenv import load_dotenv
from twilio.rest import Client
from sqlalchemy.orm import Session
from app.models.whatsapp_logs import WhatsAppLog
from app.logger import get_logger

load_dotenv()

log = get_logger("services.whatsapp")

def get_whatsapp_client() -> tuple[Client, str, str]:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_FROM")
    content_sid = os.getenv("TWILIO_WHATSAPP_CONTENT_SID")

    if not account_sid or not auth_token or not from_number or not content_sid:
        raise ValueError("Faltan variables de entorno de Twilio")

    return Client(account_sid, auth_token), from_number, content_sid

def send_whatsapp_message(to_number: str, variables: dict) -> str:
    import json
    client, from_number, content_sid = get_whatsapp_client()

    if not to_number:
        raise ValueError("El número de destino es obligatorio")

    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"

    log.info(f"Enviando WhatsApp a {to_number}")
    message = client.messages.create(
        from_=from_number,
        to=to_number,
        content_sid=content_sid,
        content_variables=json.dumps(variables),
    )

    log.info(f"WhatsApp enviado correctamente a {to_number} | SID: {message.sid}")
    return message.sid


def create_whatsapp_log(
    db: Session,
    user_id: int,
    to_number: str,
    body: str,
    status: str,
    weather_log_id: int | None = None,
    message_sid: str | None = None,
    error_message: str | None = None
) -> WhatsAppLog:
    log = WhatsAppLog(
        user_id=user_id,
        weather_log_id=weather_log_id,
        to_number=to_number,
        body=body,
        status=status,
        message_sid=message_sid,
        error_message=error_message
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
