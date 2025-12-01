from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger, DateTime, func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    panel_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    short_uuid: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64))
    subscription_url: Mapped[str] = mapped_column(String(255), nullable=False)
    
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

    # Связи
    subscription: Mapped["Subscription"] = relationship(back_populates="user", uselist=False)
    wallet: Mapped["Wallet"] = relationship(back_populates="user", uselist=False)