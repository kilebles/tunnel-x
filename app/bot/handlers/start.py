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
            telegram_id=telegram_id,
            description='Стартанул бота, еще не оплачивал.',
        )
        
        if result.created:
            logger.info(f'Создан пользователь с триалом tg_id={telegram_id}')
            await message.answer(
                f"🎉 Твой пробный премиум на 2 дня активирован!\n\n"
                f"<a href='{result.user.subscription_url}'>Получить подписку</a>"
            )
        elif result.synced:
            logger.info(f'Синхронизирован пользователь tg_id={telegram_id}')
            await message.answer(
                f"✅ Данные синхронизированы\n\n"
                f"<a href='{result.user.subscription_url}'>Твоя подписка</a>"
            )
        else:
            status = result.user.subscription.status
            if status == 'TRIAL':
                await message.answer('⏳ У тебя уже активен пробный период')
            elif status == 'PREMIUM':
                await message.answer('💎 У тебя уже есть премиум подписка')
            else:
                await message.answer('📱 У тебя уже есть подписка')
            
            logger.debug(f'Пользователь tg_id={telegram_id} уже существует, статус={status}')
        
    except PanelError as e:
        logger.error(f'Панель недоступна для tg_id={telegram_id}: {e}')
        await message.answer('⚠️ Панель временно недоступна, попробуй через минуту')
        
    except Exception:
        logger.exception(f'Неожиданная ошибка для tg_id={telegram_id}')
        await message.answer('❌ Произошла ошибка, попробуй позже')