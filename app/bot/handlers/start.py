from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.services.user import UserService
from app.services.client import PanelError
from loguru import logger

router = Router()


@router.message(Command('start'))
async def create_user_handler(message: Message):
    service = UserService()
    username = message.from_user.username or f'user_{message.from_user.id}'
    telegram_id = message.from_user.id

    try:
        result = await service.get_or_create_user(
            username=username,
            expire_at='2099-01-01T00:00:00.000Z',
            telegram_id=telegram_id,
            description='Стартанул бота, еще не оплачивал.',
        )
        
        if result.created:
            logger.info(f'Создан пользователь tg_id={telegram_id}')
            await message.answer(f"<a href='{result.user.subscription_url}'>лови хапку</a>")
        elif result.synced:
            logger.info(f'Синхронизирован пользователь tg_id={telegram_id}')
            await message.answer(f"<a href='{result.user.subscription_url}'>данные синхронизированы, лови хапку</a>")
        else:
            logger.debug(f'Пользователь tg_id={telegram_id} уже существует')
            await message.answer('Чел, у тебя уже есть хапка')
        
    except PanelError as e:
        logger.error(f'Панель недоступна для tg_id={telegram_id}: {e}')
        await message.answer('Панель недоступна, попробуй позже')
        
    except Exception:
        logger.exception(f'Неожиданная ошибка для tg_id={telegram_id}')
        await message.answer('Произошла ошибка, попробуй позже')