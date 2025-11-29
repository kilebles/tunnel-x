from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Integer, DateTime, func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    panel_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    short_uuid: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subscription_url: Mapped[str] = mapped_column(String(255), nullable=False)
    hwid_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )