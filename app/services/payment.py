from decimal import Decimal

from app.services.balance import BalanceService
from app.services.subscription import SubscriptionService
from app.db.session import AsyncSessionLocal
from app.repositories.user import UserRepository
from loguru import logger


class PaymentService:
    """Обработка платежей."""
    
    def __init__(self):
        self.balance_service = BalanceService()
        self.subscription_service = SubscriptionService()
    
    async def process_balance_payment(
        self,
        telegram_id: int,
        amount: int,
        devices: int,
        days: int
    ) -> dict:
        """
        Обрабатывает оплату с баланса.
        Возвращает результат операции.
        """
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