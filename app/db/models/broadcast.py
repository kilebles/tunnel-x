from datetime import datetime
from sqlalchemy import Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Broadcast(Base):
    """История рассылок."""
    
    __tablename__ = 'broadcasts'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Кнопки
    add_community_button: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    community_button_text: Mapped[str | None] = mapped_column(String(100), default='👥 Сообщество', nullable=True)
    community_url: Mapped[str | None] = mapped_column(String(255), default='https://t.me/TunnelX_News', nullable=True)
    
    add_try_button: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    try_button_text: Mapped[str | None] = mapped_column(String(100), default='🚀 Попробовать', nullable=True)
    
    # Статистика
    sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='pending', nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)