from app.services.subscription import SubscriptionService
from app.services.message import MessageService
from app.services.user import UserService
from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.bot.keyboards.main_menu import build_main_menu, get_main_menu_text
from app.bot.dispatcher import bot
from loguru import logger


class RemnavaveWebhookHandler:
    """Обработка вебхуков от Remnawave."""
    
    def __init__(self):
        self.subscription_service = SubscriptionService()
        self.message_service = MessageService()
        self.user_service = UserService()
    
    async def handle_event(self, event: str, data: dict) -> None:
        """Маршрутизирует события по обработчикам."""
        handlers = {
            'user.expired': self._handle_user_expired,
            'user.traffic_reset': self._handle_traffic_reset,
            'user.first_connected': self._handle_first_connected,
            'user_hwid_devices.added': self._handle_device_added,
            'user_hwid_devices.deleted': self._handle_device_deleted,
        }
        
        handler = handlers.get(event)
        if handler:
            await handler(data)
        else:
            logger.debug(f'Необработанное событие: {event}')
    
    async def _update_user_menu(self, telegram_id: int) -> None:
        """Обновляет меню пользователя."""
        try:
            user = await self.user_service.get_user_by_telegram_id(telegram_id)
            
            if not user or not user.last_message_id:
                return
            
            text = get_main_menu_text(user)
            keyboard = build_main_menu(user)
            
            await self.message_service.update_or_send_menu(
                bot=bot,
                telegram_id=telegram_id,
                text=text,
                keyboard=keyboard
            )
            
            logger.info(f'Меню обновлено для tg_id={telegram_id}')
            
        except Exception as e:
            logger.warning(f'Не удалось обновить меню для tg_id={telegram_id}: {e}')
    
    async def _handle_user_expired(self, data: dict) -> None:
        """Обрабатывает истечение подписки."""
        user_data = data.get('user', {})
        telegram_id = user_data.get('telegramId')
        
        if not telegram_id:
            logger.warning('telegramId отсутствует в вебхуке user.expired')
            return
        
        telegram_id = int(telegram_id)
        await self.subscription_service.expire_subscription(telegram_id)
        
        # Обновляем меню
        await self._update_user_menu(telegram_id)
    
    async def _handle_traffic_reset(self, data: dict) -> None:
        """Обрабатывает сброс трафика."""
        user_data = data.get('user', {})
        telegram_id = user_data.get('telegramId')
        logger.info(f'Сброс трафика для tg_id={telegram_id}')
    
    async def _handle_first_connected(self, data: dict) -> None:
        """Обрабатывает первое подключение."""
        user_data = data.get('user', {})
        telegram_id = user_data.get('telegramId')
        logger.info(f'Первое подключение tg_id={telegram_id}')
    
    async def _handle_device_added(self, data: dict) -> None:
        """Обрабатывает добавление устройства."""
        user_data = data.get('user', {})
        telegram_id = user_data.get('telegramId')
        
        if not telegram_id:
            logger.warning('telegramId отсутствует в вебхуке device_added')
            return
        
        telegram_id = int(telegram_id)
        
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                logger.warning(f'Пользователь tg_id={telegram_id} не найден при добавлении устройства')
                return
            
            await session.refresh(user, ['subscription'])
            user.subscription.hwid_count += 1
            await session.commit()
            
            logger.info(f'Устройство добавлено для tg_id={telegram_id}, теперь {user.subscription.hwid_count}')
        
        # Обновляем меню
        await self._update_user_menu(telegram_id)
    
    async def _handle_device_deleted(self, data: dict) -> None:
        """Обрабатывает удаление устройства."""
        user_data = data.get('user', {})
        telegram_id = user_data.get('telegramId')
        
        if not telegram_id:
            logger.warning('telegramId отсутствует в вебхуке device_deleted')
            return
        
        telegram_id = int(telegram_id)
        
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                logger.warning(f'Пользователь tg_id={telegram_id} не найден при удалении устройства')
                return
            
            await session.refresh(user, ['subscription'])
            if user.subscription.hwid_count > 0:
                user.subscription.hwid_count -= 1
            await session.commit()
            
            logger.info(f'Устройство удалено для tg_id={telegram_id}, осталось {user.subscription.hwid_count}')