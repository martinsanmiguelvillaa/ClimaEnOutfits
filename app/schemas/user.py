from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import time


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    gender: Optional[str] = None
    mail: EmailStr
    phone_number: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=8, max_length=100)
    whatsapp_opt_in: bool = False
    preferred_channel: str
    city: str = Field(min_length=1, max_length=100)
    notifications_enabled: bool = False
    notification_time: Optional[time] = None

    @field_validator("preferred_channel")
    @classmethod
    def validate_channel(cls, value):
        allowed = {"mail", "whatsapp", "both"}
        if value not in allowed:
            raise ValueError("preferred_channel debe ser 'mail', 'whatsapp' o 'both'")
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):
        if value is None:
            return value
        allowed = {"masculino", "femenino", "prefiero no decirlo", "otro"}
        if value not in allowed:
            raise ValueError("gender debe ser 'masculino', 'femenino', 'prefiero no decirlo' o 'other'")
        return value


class LoginRequest(BaseModel):
    mail: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    last_name: str
    gender: Optional[str] = None
    mail: str
    phone_number: str
    whatsapp_opt_in: bool
    preferred_channel: str
    city: str
    notifications_enabled: bool
    notification_time: Optional[time]

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserNotificationUpdate(BaseModel):
    notifications_enabled: bool
    notification_time: Optional[time] = None

    @field_validator("notification_time")
    @classmethod
    def validate_time(cls, value):
        return value
    
class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    gender: Optional[str] = None
    mail: Optional[EmailStr] = None
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(default=None, min_length=7, max_length=20)
    whatsapp_opt_in: Optional[bool] = None
    preferred_channel: Optional[str] = None
    

    @field_validator("preferred_channel")
    @classmethod
    def validate_channel(cls, value):
        if value is None:
            return value
        allowed = {"mail", "whatsapp", "both"}
        if value not in allowed:
            raise ValueError("preferred_channel debe ser 'mail', 'whatsapp' o 'both'")
        return value
    
    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):
        if value is None:
            return value
        allowed = {"masculino", "femenino", "prefiero no decirlo", "otro"}
        if value not in allowed:
            raise ValueError("gender debe ser 'masculino', 'femenino', 'prefiero no decirlo' o 'other'")
        return value