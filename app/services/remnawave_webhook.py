from app.services.subscription import SubscriptionService
from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository
from loguru import logger


class RemnavaveWebhookHandler:
    """Обработка вебхуков от Remnawave."""
    
    def __init__(self):
        self.subscription_service = SubscriptionService()
    
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
    
    async def _handle_user_expired(self, data: dict) -> None:
        """Обрабатывает истечение подписки."""
        user_data = data.get('user', {})
        telegram_id = user_data.get('telegramId')
        
        if not telegram_id:
            logger.warning('telegramId отсутствует в вебхуке user.expired')
            return
        
        telegram_id = int(telegram_id)
        await self.subscription_service.expire_subscription(telegram_id)
    
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