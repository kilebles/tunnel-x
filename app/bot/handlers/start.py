from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.services.user import UserService
from app.services.client import PanelError
from app.bot.keyboards.main_menu import build_main_menu, get_main_menu_text
from loguru import logger

router = Router()


@router.message(Command('start'))
async def start_handler(message: Message):
    """
    Обрабатывает /start - создаёт/синхронизирует юзера,
    показывает главное меню.
    """
    
    service = UserService()
    username = message.from_user.username or f'user_{message.from_user.id}'
    telegram_id = message.from_user.id

    try:
        result = await service.get_or_create_user(
            username=username,
            telegram_id=telegram_id,
            description='Стартанул бота, еще не оплачивал.',
        )
        
        user = await service.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await message.answer('❌ Ошибка получения данных')
            return
        
        if result.created:
            logger.info(f'Создан пользователь с триалом tg_id={telegram_id}')
            text = (
                "🎉 <b>Добро пожаловать!</b>\n\n"
                "Твой пробный премиум на 2 дня активирован!\n\n"
            ) + get_main_menu_text(user)
            
        elif result.synced:
            logger.info(f'Синхронизирован пользователь tg_id={telegram_id}')
            text = (
                "✅ <i>Данные синхронизированы</i>\n\n"
            ) + get_main_menu_text(user)
            
        else:
            text = get_main_menu_text(user)
        
        keyboard = build_main_menu(user)
        await message.answer(text, reply_markup=keyboard)
        
    except PanelError as e:
        logger.error(f'Панель недоступна для tg_id={telegram_id}: {e}')
        await message.answer('⚠️ Панель временно недоступна, попробуй через минуту')
        
    except Exception:
        logger.exception(f'Неожиданная ошибка для tg_id={telegram_id}')
        await message.answer('❌ Произошла ошибка, попробуй позже')