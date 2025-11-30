from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from loguru import logger


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """
        Ищет пользователя по Telegram ID.
        """
        
        stmt = select(User).where(User.telegram_id == telegram_id)

        try:
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            logger.debug(
                'Запрос пользователя по tg_id=%s найден=%s',
                telegram_id,
                bool(user),
            )
            return user
        except Exception:
            logger.exception(
                'Ошибка при поиске пользователя tg_id=%s',
                telegram_id,
            )
            raise

    async def create(
        self,
        panel_uuid: str,
        short_uuid: str,
        telegram_id: int,
        username: str,
        subscription_url: str,
        hwid_limit: int | None,
    ) -> User:
        """
        Создаёт пользователя в БД.
        Если запись с таким telegram_id уже существует,
        возвращает её вместо создания.
        """
        
        existing = await self.get_by_telegram_id(telegram_id)
        if existing:
            logger.debug(
                'Попытка создать уже существующего пользователя tg_id=%s id=%s',
                telegram_id,
                existing.id,
            )
            return existing

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
            await self.session.commit()
            await self.session.refresh(user)
            logger.debug(
                'Создан пользователь tg_id=%s id=%s',
                telegram_id,
                user.id,
            )
            return user
        except Exception:
            logger.exception(
                'Ошибка при создании пользователя tg_id=%s',
                telegram_id,
            )
            raise

    async def delete(self, user: User) -> None:
        """
        Удаляет пользователя из БД.
        """
        
        try:
            await self.session.delete(user)
            await self.session.commit()
            logger.debug(
                'Удалён пользователь tg_id=%s id=%s',
                user.telegram_id,
                user.id,
            )
        except Exception:
            logger.exception(
                'Ошибка при удалении пользователя tg_id=%s',
                user.telegram_id,
            )
            raise