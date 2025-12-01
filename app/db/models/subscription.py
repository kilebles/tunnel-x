from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func

from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    # Статус подписки
    status: Mapped[str] = mapped_column(String(20), default='FREE', nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Триал
    trial_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trial_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trial_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Устройства
    hwid_limit: Mapped[int | None] = mapped_column(Integer)
    hwid_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Связь
    user: Mapped["User"] = relationship(back_populates="subscription")