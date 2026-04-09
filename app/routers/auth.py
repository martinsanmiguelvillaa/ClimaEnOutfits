from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserResponse
from app.auth import verify_password, create_token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mail == data.mail).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return TokenResponse(
        access_token=create_token(user.id),
        user=UserResponse.model_validate(user),
    )
