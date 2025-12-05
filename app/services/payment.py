from decimal import Decimal

from app.services.balance import BalanceService
from app.services.subscription import SubscriptionService
from app.services.yookassa import YooKassaService
from app.services.message import MessageService
from app.services.user import UserService
from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.bot.keyboards.main_menu import build_main_menu, get_main_menu_text
from loguru import logger


class PaymentService:
    """Обработка платежей."""
    
    def __init__(self):
        self.balance_service = BalanceService()
        self.subscription_service = SubscriptionService()
        self.yookassa_service = YooKassaService()
        self.message_service = MessageService()
        self.user_service = UserService()
    
    async def process_balance_payment(
        self,
        telegram_id: int,
        amount: int,
        devices: int,
        days: int
    ) -> dict:
        """Обрабатывает оплату с баланса."""
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(telegram_id)
            
            if not user:
                raise ValueError(f'Пользователь tg_id={telegram_id} не найден')
            
            await session.refresh(user, ['wallet'])
            
            if user.wallet.balance < Decimal(str(amount)):
                raise ValueError(f'Недостаточно средств. Баланс: {user.wallet.balance}₽, требуется: {amount}₽')
            
            old_balance = float(user.wallet.balance)
            await self.balance_service.subtract_balance(telegram_id, amount)
            new_balance = await self.balance_service.get_balance(telegram_id)
            
            logger.info(f'Списано {amount}₽ с баланса tg_id={telegram_id}. Было: {old_balance}₽, стало: {new_balance}₽')
        
        await self.subscription_service.activate_premium(
            telegram_id=telegram_id,
            duration_days=days,
            hwid_limit=devices
        )
        
        return {
            'success': True,
            'amount': amount,
            'old_balance': old_balance,
            'new_balance': float(new_balance),
            'devices': devices,
            'days': days
        }
    
    async def create_card_payment(
        self,
        telegram_id: int,
        amount: int,
        devices: int,
        days: int
    ) -> dict:
        """Создаёт платёж через ЮKassa."""
        if days == 30:
            period = "1 месяц"
        elif days == 90:
            period = "3 месяца"
        elif days == 180:
            period = "6 месяцев"
        elif days == 360:
            period = "1 год"
        else:
            period = f"{days} дней"
        
        description = f"Tunnel-X: {devices} устройств на {period}"
        
        return await self.yookassa_service.create_payment(
            amount=amount,
            description=description,
            telegram_id=telegram_id,
            devices=devices,
            days=days
        )
    
    async def process_successful_card_payment(self, payment_data: dict) -> None:
        """Обрабатывает успешный платёж от ЮKassa."""
        metadata = payment_data.get('metadata', {})
        telegram_id = int(metadata.get('telegram_id'))
        devices = int(metadata.get('devices'))
        days = int(metadata.get('days'))
        amount = float(payment_data.get('amount', '0'))
        
        await self.subscription_service.activate_premium(
            telegram_id=telegram_id,
            duration_days=days,
            hwid_limit=devices
        )
        
        logger.info(
            f'Платёж ЮKassa успешно обработан: '
            f'tg_id={telegram_id}, devices={devices}, days={days}'
        )
        
        # Отправляем уведомление пользователю
        await self._notify_user_payment_success(
            telegram_id=telegram_id,
            amount=amount,
            devices=devices,
            days=days
        )
    
    async def _notify_user_payment_success(
        self,
        telegram_id: int,
        amount: float,
        devices: int,
        days: int
    ) -> None:
        """Отправляет уведомление об успешной оплате."""
        try:
            from app.bot.dispatcher import bot
            
            user = await self.user_service.get_user_by_telegram_id(telegram_id)
            
            if not user:
                logger.warning(f'Пользователь tg_id={telegram_id} не найден для уведомления')
                return
            
            if days == 30:
                period = "1 месяц"
            elif days == 90:
                period = "3 месяца"
            elif days == 180:
                period = "6 месяцев"
            elif days == 360:
                period = "1 год"
            else:
                period = f"{days} дней"
            
            text = (
                f"✅ <b>Спасибо за подписку!</b>\n\n"
                f"Оплачено: <b>{amount:.0f}₽</b>\n"
                f"Тариф: <b>{devices} устройств</b> на <b>{period}</b>\n\n"
            ) + get_main_menu_text(user)
            
            keyboard = build_main_menu(user)
            
            await self.message_service.update_or_send_menu(
                bot=bot,
                telegram_id=telegram_id,
                text=text,
                keyboard=keyboard
            )
            
            logger.info(f'Отправлено уведомление об успешной оплате для tg_id={telegram_id}')
            
        except Exception as e:
            logger.exception(f'Ошибка отправки уведомления об оплате для tg_id={telegram_id}: {e}')