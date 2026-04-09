from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Time
from datetime import time
from app.db import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    mail: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    whatsapp_opt_in: Mapped[bool] = mapped_column(nullable=False, default=False)
    preferred_channel: Mapped[str] = mapped_column(String(20), nullable=False)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notification_time: Mapped[time] = mapped_column(Time, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)

    
    weather_logs = relationship(
    "WeatherLog",
    back_populates="user",
    cascade="all, delete"
    )


    preferences = relationship(
    "Preferences",
    back_populates="user",
    cascade="all, delete",
    )