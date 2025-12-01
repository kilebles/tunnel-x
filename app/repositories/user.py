from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.models import User, Subscription, Wallet


class UserAlreadyExistsError(Exception):
    """Пользователь с таким telegram_id уже существует."""


class UserRepository:
    """Работа с пользователями в БД."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Ищет пользователя по Telegram ID с подпиской и кошельком."""
        stmt = (
            select(User)
            .options(selectinload(User.subscription), selectinload(User.wallet))
            .where(User.telegram_id == telegram_id)
        )
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
        """Создаёт пользователя с подпиской и кошельком."""
        user = User(
            panel_uuid=panel_uuid,
            short_uuid=short_uuid,
            telegram_id=telegram_id,
            username=username,
            subscription_url=subscription_url,
        )

        subscription = Subscription(
            user=user,
            hwid_limit=hwid_limit,
        )

        wallet = Wallet(user=user)

        try:
            self.session.add(user)
            self.session.add(subscription)
            self.session.add(wallet)
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except IntegrityError:
            raise UserAlreadyExistsError(f'User with telegram_id={telegram_id} exists')

    async def delete(self, user: User) -> None:
        """Удаляет пользователя из БД."""
        await self.session.delete(user)
        await self.session.flush()