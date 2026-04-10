from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from datetime import datetime, timezone
from app.db import Base


class MailLog(Base):
    __tablename__ = "mail_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    weather_log_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("weather_logs.id", ondelete="SET NULL"),
        nullable=True
    )

    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    sent_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
