from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, ForeignKey, DateTime, String
from datetime import datetime
from app.db import Base
from sqlalchemy.orm import relationship


class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    temperature: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    feels_like: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    humidity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    cloudiness: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    max_uv_index: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=None
    )

    pop: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )

    wind_speed: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    sunset: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    description: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )

    checked_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    
    user = relationship("User", back_populates="weather_logs")
