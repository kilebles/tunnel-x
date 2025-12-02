from app.services.subscription import SubscriptionService
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
        }
        
        handler = handlers.get(event)
        if handler:
            await handler(data)
        else:
            logger.debug(f'Необработанное событие: {event}')
    
    async def _handle_user_expired(self, data: dict) -> None:
        """Обрабатывает истечение подписки."""
        telegram_id = data.get('telegramId')

        if not telegram_id:
            return

        telegram_id = int(telegram_id)

        await self.subscription_service.expire_subscription(telegram_id)
    
    async def _handle_traffic_reset(self, data: dict) -> None:
        """Обрабатывает сброс трафика."""
        telegram_id = data.get('telegramId')
        logger.info(f'Сброс трафика для tg_id={telegram_id}')
    
    async def _handle_first_connected(self, data: dict) -> None:
        """Обрабатывает первое подключение."""
        telegram_id = data.get('telegramId')
        logger.info(f'Первое подключение tg_id={telegram_id}')