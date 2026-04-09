import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.logger import get_logger

log = get_logger("auth")

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        log.warning("_decode_token: token expirado")
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        log.warning(f"_decode_token: token inválido — {e}")
        raise HTTPException(status_code=401, detail="Token inválido")


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    authorization = request.headers.get("authorization") or request.headers.get("Authorization")
    log.info(f"get_current_user: authorization header present={bool(authorization)}, path={request.url.path}")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autenticado")
    token = authorization.split(" ", 1)[1]
    log.info(f"get_current_user: token prefix={token[:20]}...")
    payload = _decode_token(token)
    log.info(f"get_current_user: token decoded ok, sub={payload.get('sub')}")
    from app.models.user import User
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    log.info(f"get_current_user: user found={bool(user)}")
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user
