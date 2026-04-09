import os
import requests
from dotenv import load_dotenv
from app.models.mail_logs import MailLog
from sqlalchemy.orm import Session
from app.logger import get_logger

load_dotenv()

log = get_logger("services.mail")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")


def send_mail(to: str, subject: str, html: str):
    if not RESEND_API_KEY:
        raise ValueError("Falta la variable de entorno RESEND_API_KEY")

    log.info(f"Enviando mail a {to} | asunto: {subject}")
    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "from": "Clima App <onboarding@resend.dev>",
        "to": [to],
        "subject": subject,
        "html": html
    }

    response = requests.post(url, json=data, headers=headers)
    result = response.json()

    if response.ok:
        log.info(f"Mail enviado correctamente a {to}")
    else:
        log.error(f"Error al enviar mail a {to}: {result}")

    return result


def build_weather_mail_html(
    weather: dict,
    outfit_summary: str,
    upper_body: str,
    lower_body: str,
    footwear: str,
    extras: list[str]
) -> str:
    extras_html = "".join(f"<li>{item}</li>" for item in extras)

    return f"""
    <html>
      <body>
        <h2>Clima en {weather['city']}</h2>
        <p><strong>Temperatura:</strong> {weather['temperature']}°C</p>
        <p><strong>Sensación térmica:</strong> {weather['feels_like']}°C</p>
        <p><strong>Humedad:</strong> {weather['humidity']}%</p>
        <p><strong>Probabilidad de lluvia:</strong> {weather['pop']}%</p>

        <h3>Outfit recomendado</h3>
        <p>{outfit_summary}</p>

        <ul>
          <li><strong>Parte superior:</strong> {upper_body}</li>
          <li><strong>Parte inferior:</strong> {lower_body}</li>
          <li><strong>Calzado:</strong> {footwear}</li>
        </ul>

        <h4>Extras</h4>
        <ul>
          {extras_html}
        </ul>
      </body>
    </html>
    """


def create_mail_log(
    db: Session,
    user_id: int,
    subject: str,
    body: str,
    status: str,
    weather_log_id: int | None = None,
    error_message: str | None = None
) -> MailLog:
    mail_log = MailLog(
        user_id=user_id,
        weather_log_id=weather_log_id,
        subject=subject,
        body=body,
        status=status,
        error_message=error_message
    )

    db.add(mail_log)
    db.commit()
    db.refresh(mail_log)

    return mail_log    
