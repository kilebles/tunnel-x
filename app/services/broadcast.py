import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, update
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.db.session import AsyncSessionLocal
from app.db.models import Broadcast, User
from app.bot.keyboards.callback_data import MainMenuCallback
from app.services.message import MessageService
from loguru import logger


class BroadcastService:
    """Сервис рассылок."""
    
    async def create_broadcast(self, text: str) -> int:
        """Создаёт новую рассылку и возвращает её ID."""
        async with AsyncSessionLocal() as session:
            broadcast = Broadcast(text=text, status='pending')
            session.add(broadcast)
            await session.commit()
            await session.refresh(broadcast)
            
            logger.info(f'Создана рассылка #{broadcast.id}')
            return broadcast.id
    
    def _build_keyboard(self, broadcast: Broadcast) -> InlineKeyboardMarkup | None:
        """Создаёт клавиатуру для рассылки."""
        if not broadcast.add_community_button and not broadcast.add_try_button:
            return None
        
        builder = InlineKeyboardBuilder()
        
        if broadcast.add_community_button and broadcast.community_url:
            button_text = broadcast.community_button_text or '👥 Сообщество'
            builder.button(text=button_text, url=broadcast.community_url)
        
        if broadcast.add_try_button:
            button_text = broadcast.try_button_text or '🚀 Попробовать'
            builder.button(
                text=button_text,
                callback_data=MainMenuCallback(action='back').pack()
            )
        
        builder.adjust(1)
        return builder.as_markup()
    
    async def start_broadcast(self, broadcast_id: int, bot: Bot) -> dict:
        """
        Запускает рассылку.
        Возвращает статистику: {sent: int, failed: int, total: int}
        """
        async with AsyncSessionLocal() as session:
            # Получаем рассылку
            result = await session.execute(
                select(Broadcast).where(Broadcast.id == broadcast_id)
            )
            broadcast = result.scalar_one_or_none()
            
            if not broadcast:
                raise ValueError(f'Рассылка #{broadcast_id} не найдена')
            
            if broadcast.status != 'pending':
                raise ValueError(f'Рассылка #{broadcast_id} уже запущена (статус: {broadcast.status})')
            
            # Обновляем статус
            broadcast.status = 'sending'
            await session.commit()
            
            logger.info(f'Рассылка #{broadcast_id}: текст = {broadcast.text[:100]}')
        
        # Получаем всех пользователей
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User.telegram_id)
            )
            user_ids = [row[0] for row in result.all()]
        
        logger.info(f'Начинаем рассылку #{broadcast_id} для {len(user_ids)} пользователей')
        
        # Создаём клавиатуру
        keyboard = self._build_keyboard(broadcast)
        
        # MessageService для обновления last_message_id
        message_service = MessageService()
        
        sent = 0
        failed = 0
        
        # Отправляем сообщения
        for telegram_id in user_ids:
            try:
                # Используем MessageService чтобы обновить/удалить старое сообщение
                await message_service.update_or_send_menu(
                    bot=bot,
                    telegram_id=telegram_id,
                    text=broadcast.text,
                    keyboard=keyboard
                )
                sent += 1
                logger.debug(f'Отправлено tg_id={telegram_id}')
                
                # Задержка чтобы не словить rate limit
                await asyncio.sleep(0.05)  # 20 сообщений в секунду
                
            except ValueError as e:
                # Пользователь не найден в БД
                logger.debug(f'Пользователь не найден tg_id={telegram_id}: {e}')
                failed += 1
                
            except TelegramForbiddenError as e:
                logger.debug(f'Пользователь заблокировал бота tg_id={telegram_id}')
                failed += 1
                
            except TelegramBadRequest as e:
                logger.warning(f'TelegramBadRequest для tg_id={telegram_id}: {e}')
                failed += 1
                
            except Exception as e:
                logger.error(f'Ошибка отправки рассылки tg_id={telegram_id}: {e}')
                failed += 1
        
        # Обновляем статистику
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Broadcast)
                .where(Broadcast.id == broadcast_id)
                .values(
                    sent_count=sent,
                    failed_count=failed,
                    status='completed',
                    completed_at=datetime.now(timezone.utc)
                )
            )
            await session.commit()
        
        logger.info(f'Рассылка #{broadcast_id} завершена: отправлено {sent}, ошибок {failed}')
        
        return {
            'sent': sent,
            'failed': failed,
            'total': len(user_ids)
        }