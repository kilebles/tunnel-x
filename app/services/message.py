from datetime import datetime, timezone, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest

from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository
from loguru import logger


class MessageService:
    """Управление сообщениями бота (всегда одно сообщение)."""
    
    async def update_or_send_menu(
        self,
        bot: Bot,
        telegram_id: int,
        text: str,
        keyboard: InlineKeyboardMarkup
    ) -> int:
        """
        Обновляет существующее сообщение или отправляет новое.
        Возвращает message_id отправленного/обновлённого сообщения.
        """
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                raise ValueError(f'Пользователь tg_id={telegram_id} не найден')
            
            if user.last_message_id:
                try:
                    await bot.edit_message_text(
                        text=text,
                        chat_id=telegram_id,
                        message_id=user.last_message_id,
                        reply_markup=keyboard
                    )
                    logger.debug(f'Обновлено сообщение {user.last_message_id} для tg_id={telegram_id}')
                    return user.last_message_id
                    
                except TelegramBadRequest as e:
                    logger.debug(f'Не удалось обновить сообщение {user.last_message_id}: {e}')
                    
                    try:
                        await bot.delete_message(
                            chat_id=telegram_id,
                            message_id=user.last_message_id
                        )
                    except:
                        pass
            
            msg = await bot.send_message(
                chat_id=telegram_id,
                text=text,
                reply_markup=keyboard
            )
            
            user.last_message_id = msg.message_id
            await session.commit()
            
            logger.debug(f'Отправлено новое сообщение {msg.message_id} для tg_id={telegram_id}')
            return msg.message_id