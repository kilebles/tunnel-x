from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.services.user import UserService
from app.core.logger.setup import logger

router = Router()


@router.message(Command('start'))
async def create_user_handler(message: Message):
    service = UserService()

    username = message.from_user.username or f'user_{message.from_user.id}'

    try:
        user = await service.create_user(
            username=username,
            expire_at='2099-01-01T00:00:00.000Z',
            telegram_id=message.from_user.id,
            description='Стартанул бота, еще не оплачивал.',
        )
    except Exception as exc:
        logger.error(f'Ошибка при создании пользователя tg_id={message.from_user.id}: {exc}')
        await message.answer('Произошла ошибка, попробуй позже')
        return

    if isinstance(user, dict) and user.get('error'):
        logger.info(f'Пользователь tg_id={message.from_user.id} уже существует')
        await message.answer('Чел, у тебя уже есть хапка')
        return

    await message.answer(
        f"<a href='{user.subscription_url}'>лови хапку</a>"
    )