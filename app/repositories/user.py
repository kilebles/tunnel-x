from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.models import User


class UserAlreadyExistsError(Exception):
    """Пользователь с таким telegram_id уже существует."""


class UserRepository:
    """Работа с пользователями в БД."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Ищет пользователя по Telegram ID."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        panel_uuid: str,
        short_uuid: str,
        telegram_id: int,
        username: str,
        subscription_url: str,
        hwid_limit: int | None,
    ) -> User:
        """Создаёт пользователя в БД."""
        user = User(
            panel_uuid=panel_uuid,
            short_uuid=short_uuid,
            telegram_id=telegram_id,
            username=username,
            subscription_url=subscription_url,
            hwid_limit=hwid_limit,
        )

        try:
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except IntegrityError:
            raise UserAlreadyExistsError(f'User with telegram_id={telegram_id} exists')

    async def delete(self, user: User) -> None:
        """Удаляет пользователя из БД."""
        await self.session.delete(user)
        await self.session.flush()