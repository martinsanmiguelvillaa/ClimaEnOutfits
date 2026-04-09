import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.limiter import limiter
from app.db import Base, engine
from app.models.user import User
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.weather import router as weather_router
from app.routers.outfit import router as outfit_router
from app.routers.notification import router as notification_router
from app.routers.preferences import router as preferences_router
from fastapi import APIRouter
from app.services.scheduler import scheduler
from app.db import SessionLocal
from app.services.scheduler import schedule_user_notification
from app.logger import get_logger

MAX_REQUEST_SIZE_BYTES = 10 * 1024  # 10 KB

log = get_logger("main")

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "OPENWEATHER_API_KEY",
    "OPENAI_API_KEY",
    "RESEND_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_WHATSAPP_CONTENT_SID",
    "SECRET_KEY",
]

def validate_env_vars():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Variables de entorno faltantes: {', '.join(missing)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_env_vars()
    log.info("Iniciando aplicación")
    scheduler.start()
    load_all_user_notifications()
    yield
    log.info("Cerrando aplicación")
    scheduler.shutdown()


ALLOWED_ORIGINS = [
    "https://clima-en-outfits.vercel.app",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app = FastAPI(title="Weather Outfit API", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Request demasiado grande"})
    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    log.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.1f}ms)")
    return response


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


def load_all_user_notifications():
    db = SessionLocal()
    try:
        users = db.query(User).filter(
            User.notifications_enabled == True,
            User.notification_time.isnot(None)
        ).all()

        log.info(f"Cargando notificaciones para {len(users)} usuario(s)")
        for user in users:
            schedule_user_notification(user)

    finally:
        db.close()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(preferences_router, prefix="/preferences", tags=["preferences"])
app.include_router(weather_router, prefix="/weather", tags=["weather"])
app.include_router(outfit_router, prefix="/outfit", tags=["outfit"])
app.include_router(notification_router, prefix="/notifications", tags=["notifications"])


router = APIRouter()
